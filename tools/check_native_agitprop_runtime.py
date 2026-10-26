"""Check prepared native Agitprop scripts in a bounded offline AST model.

Requires the user's actual game sources and a prepared mod; no original game
code is bundled. This checks selected state transitions, not HOI4 execution,
AI, rendering, event ageing or the engine's internal decision scheduler. The
clock below explicitly models expiry followed by the declared cooldown.
"""
from dataclasses import dataclass
from pathlib import Path
import argparse
import operator

from validate_mod import TOKEN, one, parse, values


NATIVE_EFFECTS = (
    'SOV_pick_propaganda_campaign_slot_effect',
    'SOV_reset_propaganda_campaign_slot_effect',
    'SOV_unlock_propaganda_campaign_slot_effect',
    'SOV_increase_propaganda_campaign_cost_effect',
    'SOV_achievement_propaganda_counter_effect',
)
PRIMARY = 'sr_lito_politics_cadre_schools'
COUNCILS = 'sr_lito_native_agitprop_councils_milestone'
ACADEMY = 'sr_lito_native_agitprop_academy_milestone'
UNLOCKED = 'sr_lito_native_agitprop_unlocked'
READY = 'sr_lito_native_agitprop_ready'
FRAMES = tuple(f'SOV_poster_{side}_icon_frame' for side in ('left', 'center', 'right'))
CAMPAIGNS = (
    'SOV_propaganda_hit_of_hammer',
    'SOV_propaganda_high_yield',
    'SOV_propaganda_motherland_calls',
)
COMPARE = {
    '=': operator.eq, '==': operator.eq, '>': operator.gt, '<': operator.lt,
    '>=': operator.ge, '<=': operator.le, '!=': operator.ne,
    'equals': operator.eq, 'not_equals': operator.ne,
    'greater_than': operator.gt, 'less_than': operator.lt,
    'greater_than_or_equals': operator.ge, 'less_than_or_equals': operator.le,
}


def extract_root_blocks(path, wanted):
    """Token-index only the requested top-level blocks, then parse those spans."""
    text = path.read_text(encoding='utf-8-sig')
    tokens = [match for match in TOKEN.finditer(text)
              if not match[0].isspace() and not match[0].startswith('#')]
    result, index, depth = {}, 0, 0
    while index < len(tokens):
        key = tokens[index][0]
        if (depth == 0 and key in wanted and index + 2 < len(tokens)
                and tokens[index + 1][0] == '=' and tokens[index + 2][0] == '{'):
            end, nested = index + 3, 1
            while end < len(tokens) and nested:
                nested += (tokens[end][0] == '{') - (tokens[end][0] == '}')
                end += 1
            assert nested == 0, f'Unclosed requested block {key} in {path}'
            assert key not in result, f'Duplicate requested block {key} in {path}'
            span = text[tokens[index].start():tokens[end - 1].end()]
            result[key] = one(parse(span), key)
            index = end
            continue
        depth += (key == '{') - (key == '}')
        assert depth >= 0, f'Unexpected closing brace in {path}'
        index += 1
    assert set(result) == set(wanted), f'Missing requested blocks in {path}: {set(wanted) - set(result)}'
    return result


@dataclass
class ActiveCampaign:
    deadline: float
    cooldown: float


class NativeWorld:
    """Deliberately small interpreter for the actual tested native commands."""
    def __init__(self, effects, triggers, category, decisions, tag='SOV', initialized=True):
        self.effects, self.triggers = effects, triggers
        self.category, self.decisions = category, decisions
        self.tag = self.original_tag = tag
        self.variables = {'sr_story_trust': 50.0}
        self.flags = {'sr_lito_initialized': None} if initialized else {}
        self.focuses = set()
        self.day, self.power = 0.0, 500.0
        self.at_war, self.enemy_is_major = False, True
        self.surrender_progress = 0.0
        self.active, self.cooldowns, self.scheduled = {}, {}, []
        self.unlock_calls = 0

    def number(self, text):
        try:
            return float(text)
        except ValueError:
            return self.variables.get(text, 0.0)

    def trigger(self, nodes):
        return all(self.condition(key, op, value) for key, op, value in nodes)

    def condition(self, key, op, value):
        if key in ('AND', 'OR', 'NOT'):
            results = [self.condition(k, o, v) for k, o, v in value]
            return any(results) if key == 'OR' else not all(results) if key == 'NOT' else all(results)
        if key == 'custom_trigger_tooltip':
            return self.trigger([node for node in value if node[0] != 'tooltip'])
        if key in self.triggers:
            return self.trigger(self.triggers[key]) == (value == 'yes')
        if key == 'always': return value == 'yes'
        if key == 'tag': return self.tag == value
        if key == 'original_tag': return self.original_tag == value
        if key == 'has_country_flag': return value in self.flags
        if key == 'has_variable': return value in self.variables
        if key == 'has_completed_focus': return value in self.focuses
        if key == 'has_war': return self.at_war == (value == 'yes')
        if key == 'is_major': return self.enemy_is_major == (value == 'yes')
        if key == 'any_enemy_country': return self.at_war and self.trigger(value)
        if key == 'surrender_progress': return COMPARE[op](self.surrender_progress, self.number(value))
        if key == 'check_variable':
            if values(value, 'var'):
                variable, target = one(value, 'var'), one(value, 'value')
                comparison = (values(value, 'compare') or ['='])[0]
            else:
                variable, comparison, target = next(node for node in value if node[0] not in ('compare', 'tooltip'))
                comparison = (values(value, 'compare') or [comparison])[0]
            return COMPARE[comparison](self.variables.get(variable, 0.0), self.number(target))
        raise AssertionError(f'Unsupported bounded-model trigger: {key}')

    def run(self, nodes):
        branch = None
        for key, _, value in nodes:
            if key == 'if':
                branch = self.trigger(one(value, 'limit'))
                if branch: self.run([node for node in value if node[0] != 'limit'])
            elif key == 'else_if':
                assert branch is not None
                if not branch and self.trigger(one(value, 'limit')):
                    self.run([node for node in value if node[0] != 'limit'])
                    branch = True
            elif key == 'else':
                assert branch is not None
                if not branch: self.run(value)
                branch = None
            elif key in self.effects:
                assert value == 'yes'
                if key == 'SOV_unlock_propaganda_campaign_slot_effect': self.unlock_calls += 1
                self.run(self.effects[key])
            elif key == 'hidden_effect': self.run(value)
            elif key in ('set_variable', 'add_to_variable', 'multiply_variable'):
                if values(value, 'var'):
                    assignments = [(one(value, 'var'), '=', one(value, 'value'))]
                else:
                    assignments = value
                for name, _, number in assignments:
                    amount = self.number(number)
                    if key == 'set_variable': self.variables[name] = amount
                    elif key == 'add_to_variable': self.variables[name] = self.variables.get(name, 0.0) + amount
                    else: self.variables[name] = self.variables.get(name, 0.0) * amount
            elif key == 'clear_variable': self.variables.pop(value, None)
            elif key == 'set_country_flag':
                if isinstance(value, list):
                    self.flags[one(value, 'flag')] = self.day + self.number(one(value, 'days'))
                else: self.flags[value] = None
            elif key == 'clr_country_flag': self.flags.pop(value, None)
            elif key == 'country_event':
                self.scheduled.append((one(value, 'id'), self.day + self.number(one(value, 'days'))))
            elif key == 'custom_effect_tooltip': pass
            else: raise AssertionError(f'Unsupported bounded-model effect: {key}')

    def sync(self):
        self.run(self.effects['sr_lito_native_agitprop_sync_effect'])

    def ready(self, campaign):
        body = self.decisions[campaign]
        return (campaign not in self.active and self.day >= self.cooldowns.get(campaign, 0.0)
                and self.power >= self.number(one(body, 'cost'))
                and self.trigger(one(self.category, 'allowed'))
                and self.trigger(one(self.category, 'visible'))
                and self.trigger(one(body, 'allowed'))
                and self.trigger(one(body, 'visible'))
                and self.trigger(one(body, 'available')))

    def take(self, campaign):
        if not self.ready(campaign): return False
        body = self.decisions[campaign]
        self.power -= self.number(one(body, 'cost'))
        self.run(one(body, 'complete_effect'))
        self.active[campaign] = ActiveCampaign(self.day + self.number(one(body, 'days_remove')),
                                               self.number(one(body, 'days_re_enable')))
        return True

    def advance(self, days):
        target = self.day + days
        for campaign, active in sorted(list(self.active.items()), key=lambda item: item[1].deadline):
            if active.deadline > target: continue
            self.day = active.deadline
            self.run(one(self.decisions[campaign], 'remove_effect'))
            del self.active[campaign]
            self.cooldowns[campaign] = self.day + active.cooldown
        self.day = target
        self.flags = {name: expiry for name, expiry in self.flags.items()
                      if expiry is None or expiry > self.day}

    def frames(self):
        return tuple(self.variables.get(name) for name in FRAMES)


def check(game, mod):
    effects = extract_root_blocks(game/'common/scripted_effects/SOV_scripted_effects.txt', NATIVE_EFFECTS)
    effects['sr_lito_native_agitprop_sync_effect'] = one(
        parse((mod/'common/scripted_effects/sr_native_agitprop_effects.txt').read_text(encoding='utf-8-sig')),
        'sr_lito_native_agitprop_sync_effect')
    triggers = extract_root_blocks(game/'common/scripted_triggers/SOV_scripted_triggers.txt',
                                   {'SOV_propaganda_poster_slot_available'})
    category = extract_root_blocks(mod/'common/decisions/categories/SOV_decision_categories.txt',
                                   {'SOV_propaganda_campaigns'})['SOV_propaganda_campaigns']
    decisions = {key: body for key, _, body in extract_root_blocks(mod/'common/decisions/SOV.txt',
                 {'SOV_propaganda_campaigns'})['SOV_propaganda_campaigns']}

    def world(**kwargs):
        return NativeWorld(effects, triggers, category, decisions, **kwargs)

    first = world(); first.sync()
    assert READY in first.flags and UNLOCKED not in first.flags and first.frames() == (1, 1, 1)
    assert not first.ready('SOV_propaganda_transport')
    assert all(first.variables[one(decisions[key], 'cost')] == 15 for key in decisions if key.startswith('SOV_propaganda_'))
    first.flags[UNLOCKED] = None; first.sync()
    assert PRIMARY not in first.focuses and first.frames() == (2, 1, 1)
    first.flags[COUNCILS] = None; first.sync(); assert first.frames() == (2, 2, 1)
    first.flags[ACADEMY] = None; first.sync(); assert first.frames() == (2, 2, 2)
    assert first.unlock_calls == 3
    print('PASS: focus completion and two milestone flags unlock exactly one native slot each.')

    reordered = world(); reordered.flags.update({COUNCILS: None, ACADEMY: None}); reordered.sync()
    assert reordered.frames() == (1, 1, 1)
    reordered.flags[UNLOCKED] = None; reordered.sync()
    assert reordered.frames() == (2, 2, 2) and reordered.unlock_calls == 3
    print('PASS: milestones completed before the Agitprop focus are recovered without premature unlocks.')

    first.at_war = True
    for key in CAMPAIGNS: assert first.take(key), key
    assert first.frames() == (7, 11, 3)
    assert first.variables['SOV_propaganda_campaigns_taken'] == 3
    assert first.scheduled == [
        ('NSB_soviet_propaganda_capmaign_events.101', 150),
        ('NSB_soviet_propaganda_capmaign_events.102', 150),
        ('NSB_soviet_propaganda_capmaign_events.103', 150),
    ]
    before = (dict(first.variables), dict(first.flags), first.power, first.unlock_calls)
    assert not first.take('SOV_propaganda_transport')
    assert (first.variables, first.flags, first.power, first.unlock_calls) == before
    first.sync()
    assert (first.variables, first.flags, first.power, first.unlock_calls) == before
    print('PASS: three native campaigns occupy all slots; a fourth and repeated sync cannot charge or erase an active slot.')

    scripted_gui = one(parse((mod/'common/scripted_guis/SOV_propaganda_campaigns_scripted_gui.txt').read_text(encoding='utf-8-sig')),
                       'scripted_gui')
    gui_triggers = one(one(scripted_gui, 'sov_propaganda_campaigns_ui'), 'triggers')
    shown = {key for key, _, body in gui_triggers if key.startswith('sr_lito_poster_') and first.trigger(body)}
    assert shown == {'sr_lito_poster_left_star_visible', 'sr_lito_poster_center_peoples_visible',
                     'sr_lito_poster_right_light_visible'}
    assert all(not first.trigger(one(gui_triggers, f'propaganda_poster_{side}_visible'))
               for side in ('left', 'center', 'right'))
    print('PASS: actual prepared GUI triggers select the three supplied posters for the matching native campaign frames.')

    first.advance(179); assert len(first.active) == 3
    first.advance(1); assert not first.active and first.frames() == (2, 2, 2)
    for key in CAMPAIGNS: assert first.variables[one(decisions[key], 'cost')] == 30
    assert first.variables['SOV_propaganda_campaigns_taken'] == 3
    assert not first.ready(CAMPAIGNS[0]) and first.ready('SOV_propaganda_transport')
    assert not any(first.trigger(body) for key, _, body in gui_triggers if key.startswith('sr_lito_poster_'))
    assert all(first.trigger(one(gui_triggers, f'propaganda_poster_{side}_visible'))
               for side in ('left', 'center', 'right'))
    first.advance(89); assert not first.ready(CAMPAIGNS[0])
    first.advance(1); assert first.ready(CAMPAIGNS[0])
    power = first.power; assert first.take(CAMPAIGNS[0]); assert first.power == power - 30
    print('PASS: bounded clock executes actual native expiry/reset and cost doubling at 180 days, with the declared 90-day cooldown.')

    old = world(); old.sync()
    old.focuses.update({PRIMARY, 'sr_lito_workers_councils', 'sr_lito_academy_network'})
    old.variables.update(dict(zip(FRAMES, (7, 11, 3))))
    old.variables.update(SOV_propaganda_hit_of_hammer_cost=60, SOV_propaganda_campaigns_taken=12,
                         sr_story_trust=67, propaganda_counter=8)
    prior = dict(old.variables); old.sync()
    assert old.variables == prior and old.frames() == (7, 11, 3) and old.unlock_calls == 0
    assert UNLOCKED in old.flags
    print('PASS: old-save active frames, raised costs, counters and political trust survive synchronization.')

    for kwargs in ({'tag': 'GER'}, {'initialized': False}):
        excluded = world(**kwargs)
        excluded.flags.update({UNLOCKED: None, COUNCILS: None, ACADEMY: None})
        snapshot = (dict(excluded.variables), dict(excluded.flags))
        excluded.sync()
        assert (excluded.variables, excluded.flags) == snapshot and READY not in excluded.flags
    print('PASS: foreign countries and uninitialized Soviets are unaffected.')
    print('7 bounded AST scenarios passed. This is not an HOI4 engine, AI, ageing-event or GUI-rendering test.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-root', type=Path, required=True)
    parser.add_argument('--staged-mod', type=Path, required=True)
    args = parser.parse_args()
    check(args.game_root, args.staged_mod)
