"""Execute the mod's parsed resistance scripts in a deliberately small test harness.

This checks script behavior and targeting; it does not emulate or validate HOI4.
Unknown directives fail instead of being treated as successful no-ops.
"""
import operator
import unittest
from dataclasses import dataclass
from validate_mod import MOD, REPUBLICS, one, parse, values


def load(relative):
    return parse((MOD / relative).read_text(encoding='utf-8-sig'))


EFFECTS = dict((key, body) for key, _, body in load('common/scripted_effects/sr_union_effects.txt'))
TRIGGERS = dict((key, body) for key, _, body in load('common/scripted_triggers/sr_union_triggers.txt'))
DECISIONS = one(load('common/decisions/sr_union_decisions.txt'), 'sr_union_council')
TAGS = dict(zip(REPUBLICS, (None, 'UKR', 'BLR', 'GEO', 'ARM', 'AZR', 'KAZ', 'UZB',
                           'TMS', 'KYR', 'TAJ', 'EST', 'LAT', 'LIT', 'MOL')))
COMPARE = {'=': operator.eq, '>': operator.gt, '<': operator.lt,
           '>=': operator.ge, '<=': operator.le, '!=': operator.ne,
           'greater_than_or_equals': operator.ge, 'greater_than': operator.gt,
           'less_than': operator.lt, 'less_than_or_equals': operator.le,
           'equals': operator.eq, 'not_equals': operator.ne}


@dataclass
class State:
    name: str
    cores: set
    owned: bool = True
    controller: str = 'SOV'


class ScriptHarness:
    def __init__(self, active=REPUBLICS[:11], balance=-0.8):
        self.balance, self.variables, self.ideas, self.flags, self.damage = balance, {}, set(), {}, []
        self.states = [State(key, {'SOV'} | ({tag} if tag else set()), key in active)
                       for key, tag in TAGS.items()]

    def resistance(self, republic):
        return self.variables.get('sr_resistance_' + republic, 0)

    def trigger(self, nodes, state=None):
        return all([self.condition(key, op, value, state) for key, op, value in nodes])

    def condition(self, key, op, value, state):
        if key in ('AND', 'OR', 'NOT'):
            results = [self.condition(k, o, v, state) for k, o, v in value]
            return any(results) if key == 'OR' else not all(results) if key == 'NOT' else all(results)
        if key in TRIGGERS:
            assert value in ('yes', 'no')
            return self.trigger(TRIGGERS[key], state) == (value == 'yes')
        if key == 'tag':
            return value == 'SOV'
        if key == 'any_owned_state':
            return any([self.trigger(value, s) for s in self.states if s.owned])
        if key == 'is_core_of':
            assert state is not None
            return value in state.cores
        if key == 'is_controlled_by':
            assert state is not None
            return state.controller == ('SOV' if value == 'ROOT' else value)
        if key in ('has_idea', 'has_country_flag'):
            return value in (self.ideas if key == 'has_idea' else self.flags)
        if key == 'power_balance_value':
            assert one(value, 'id') == 'sr_union_balance'
            _, comparison, target = next(node for node in value if node[0] == 'value')
            return COMPARE[comparison](self.balance, float(target))
        if key == 'check_variable':
            pairs = [(k, v) for k, _, v in value if k not in ('compare', 'tooltip')]
            assert len(pairs) == 1, 'Extend harness for explicit var/value syntax'
            name, target = pairs[0]
            comparison = values(value, 'compare') or ['greater_than_or_equals']
            return COMPARE[comparison[0]](self.variables.get(name, 0), float(target))
        raise AssertionError(f'Unsupported trigger: {key}')

    def run(self, nodes, state=None):
        i = 0
        while i < len(nodes):
            key, op, value = nodes[i]
            if key == 'if':
                branches = [(key, value)]
                i += 1
                while i < len(nodes) and nodes[i][0] in ('else_if', 'else'):
                    branches.append((nodes[i][0], nodes[i][2]))
                    i += 1
                for kind, body in branches:
                    if kind == 'else' or self.trigger(one(body, 'limit'), state):
                        self.run([node for node in body if node[0] != 'limit'], state)
                        break
                continue
            if key in EFFECTS:
                assert value == 'yes'
                self.run(EFFECTS[key], state)
            elif key in ('set_variable', 'add_to_variable', 'subtract_from_variable'):
                assert len(value) == 1
                name, _, amount = value[0]
                amount = float(amount)
                current = self.variables.get(name, 0)
                self.variables[name] = (amount if key == 'set_variable' else
                                        current + amount if key == 'add_to_variable' else current - amount)
            elif key == 'clamp_variable':
                name = one(value, 'var')
                self.variables[name] = max(float(one(value, 'min')),
                                           min(float(one(value, 'max')), self.variables.get(name, 0)))
            elif key in ('add_ideas', 'remove_ideas'):
                (self.ideas.add if key == 'add_ideas' else self.ideas.discard)(value)
            elif key == 'random_owned_state':
                eligible = [s for s in self.states if s.owned and self.trigger(one(value, 'limit'), s)]
                if eligible:
                    self.run([node for node in value if node[0] != 'limit'], eligible[0])
            elif key == 'damage_building':
                assert state is not None
                self.damage.append((state.name, one(value, 'type'), float(one(value, 'damage'))))
            elif key == 'add_power_balance_value':
                assert one(value, 'id') == 'sr_union_balance'
                self.balance = max(-1, min(1, self.balance + float(one(value, 'value'))))
            elif key == 'set_country_flag':
                self.flags[one(value, 'flag')] = float(one(value, 'days'))
            elif key == 'custom_effect_tooltip':
                assert isinstance(value, str)  # Text only; no gameplay effect.
            else:
                raise AssertionError(f'Unsupported effect: {key}')
            i += 1

    def month(self):
        self.run(EFFECTS['sr_union_resistance_monthly_effect'])

    def council(self, republic):
        self.run(one(one(DECISIONS, 'sr_union_consult_' + republic), 'complete_effect'))


class ResistanceTests(unittest.TestCase):
    def test_eight_crisis_months_execute_growth_strikes_and_sabotage(self):
        game = ScriptHarness()
        for _ in range(8):
            game.month()
        self.assertEqual([game.resistance(r) for r in REPUBLICS[:11]], [80] * 11)
        self.assertEqual(game.ideas, {'sr_union_mass_strikes', 'sr_union_sabotage_networks'})
        self.assertEqual({name for name, _, _ in game.damage}, set(REPUBLICS[:11]))
        self.assertEqual(len(game.damage), 11)
        self.assertTrue(all(kind == 'infrastructure' and amount == 1 for _, kind, amount in game.damage))

    def test_growth_caps_all_fifteen_republics_at_one_hundred(self):
        game = ScriptHarness(active=REPUBLICS)
        game.variables = {'sr_resistance_' + r: 97 for r in REPUBLICS}
        game.month()
        self.assertEqual([game.resistance(r) for r in REPUBLICS], [100] * 15)
        self.assertEqual(len(game.damage), 15)

    def test_preservation_removes_sabotage_then_strikes(self):
        game = ScriptHarness(balance=0.5)
        game.variables['sr_resistance_russia'] = 80
        game.run(EFFECTS['sr_update_union_resistance_ideas_effect'])
        game.month()
        self.assertEqual(game.resistance('russia'), 75)
        self.assertEqual(game.ideas, {'sr_union_mass_strikes'})
        self.assertFalse(game.damage)
        for _ in range(6):
            game.month()
        self.assertEqual(game.resistance('russia'), 45)
        self.assertFalse(game.ideas)

    def test_inactive_republic_resets_without_penalties_or_damage(self):
        game = ScriptHarness()
        game.variables['sr_resistance_estonia'] = 100
        game.month()
        self.assertEqual(game.resistance('estonia'), 0)
        self.assertFalse(game.ideas)
        self.assertFalse(game.damage)

    def test_council_targets_own_resistance_and_refreshes_thresholds(self):
        for index, republic in enumerate(REPUBLICS):
            with self.subTest(republic=republic):
                other = REPUBLICS[(index + 1) % len(REPUBLICS)]
                game = ScriptHarness(active=REPUBLICS)
                game.variables.update({'sr_resistance_' + republic: 80, 'sr_resistance_' + other: 49})
                game.run(EFFECTS['sr_update_union_resistance_ideas_effect'])
                game.council(republic)
                self.assertEqual((game.resistance(republic), game.resistance(other)), (65, 49))
                self.assertEqual(game.ideas, {'sr_union_mass_strikes'})
                self.assertEqual(game.flags['sr_union_' + republic + '_consulted'], 180)
                game.variables['sr_resistance_' + republic] = 5
                # Effect execution only; UI cooldown constraints are checked by validate_mod.py.
                game.council(republic)
                self.assertEqual(game.resistance(republic), 0)
                self.assertFalse(game.ideas)

    def test_exact_thresholds_use_script_comparisons(self):
        for balance in (-0.60, 0.20):
            game = ScriptHarness(balance=balance)
            game.variables['sr_resistance_russia'] = 10
            game.month()
            self.assertEqual(game.resistance('russia'), 8)

    def test_russian_sabotage_excludes_other_republics_and_occupied_states(self):
        russia = values(EFFECTS['sr_union_resistance_monthly_effect'], 'if')[0]
        sabotage = one(values(russia, 'if')[-1], 'random_owned_state')
        limit = one(sabotage, 'limit')
        excluded = values(one(one(limit, 'NOT'), 'OR'), 'is_core_of')
        self.assertEqual(set(excluded), {tag for tag in TAGS.values() if tag})
        self.assertEqual(len(excluded), 14)
        game = ScriptHarness()
        game.states.reverse()  # Ukrainian and other cores must never substitute for Russia.
        next(s for s in game.states if s.name == 'russia').controller = 'GER'
        game.variables['sr_resistance_russia'] = 80
        game.month()
        self.assertFalse(game.damage)

    def test_unknown_directives_fail_closed(self):
        game = ScriptHarness()
        with self.assertRaisesRegex(AssertionError, 'Unsupported effect'):
            game.run([('invented_effect', '=', 'yes')])
        with self.assertRaisesRegex(AssertionError, 'Unsupported trigger'):
            game.trigger([('invented_trigger', '=', 'yes')])


if __name__ == '__main__':
    unittest.main(verbosity=2)
