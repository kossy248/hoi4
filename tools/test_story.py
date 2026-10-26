"""Regression checks for actual story ASTs, using a deliberately limited fixture.

The fixture executes event options and native mission outcome blocks. It does
not replace a game test or simulate daily political power, AI or the HOI4 UI.
"""
from collections import defaultdict
from dataclasses import dataclass, field
import operator
import re
import unittest

from validate_mod import MOD, one, parse, values, walk


def load(path):
    return parse(path.read_text(encoding='utf-8-sig'))


SCRIPTS = {path.relative_to(MOD).as_posix(): load(path)
           for path in MOD.rglob('*.txt')}
EVENT_BLOCKS = [event for name, nodes in SCRIPTS.items() if name.startswith('events/')
                for event in values(nodes, 'country_event')]
EVENTS = {one(event, 'id'): event for event in EVENT_BLOCKS}
EFFECTS = {key: body for name, nodes in SCRIPTS.items()
           if name.startswith('common/scripted_effects/') for key, _, body in nodes}
TRIGGERS = {key: body for name, nodes in SCRIPTS.items()
            if name.startswith('common/scripted_triggers/') for key, _, body in nodes}
DECISIONS = {key: body for name, nodes in SCRIPTS.items()
             if name.startswith('common/decisions/') and '/categories/' not in name
             for _, _, category in nodes for key, _, body in category}
COMPARE = {'=': operator.eq, '>': operator.gt, '<': operator.lt,
           '>=': operator.ge, '<=': operator.le, '!=': operator.ne,
           'equals': operator.eq, 'not_equals': operator.ne,
           'greater_than': operator.gt, 'less_than': operator.lt,
           'greater_than_or_equals': operator.ge, 'less_than_or_equals': operator.le}


@dataclass
class Country:
    exists: bool = True
    ai: bool = True
    government: str = 'neutrality'
    overlord: str = None
    wars: set = field(default_factory=set)
    faction_leader: bool = False
    flags: dict = field(default_factory=dict)
    variables: dict = field(default_factory=lambda: defaultdict(float))
    ideas: dict = field(default_factory=dict)
    focuses: set = field(default_factory=set)
    popularity: float = 0.25
    power: float = 500
    stability: float = 0.50
    balance: float = 0.15


@dataclass
class State:
    owner: str
    controller: str
    cores: set
    slots: dict = field(default_factory=lambda: {'industrial_complex': 2, 'infrastructure': 2})
    buildings: list = field(default_factory=list)


class StoryWorld:
    def __init__(self):
        self.countries = {tag: Country() for tag in ('SOV', 'YUG', 'ALB', 'BUL', 'GRE', 'ROM', 'GER')}
        self.countries['SOV'].ai = False
        self.countries['SOV'].government = 'communism'
        self.states = [State('SOV', 'SOV', {tag}) for tag in ('UKR', 'GEO', 'KAZ')]
        self.day = 0
        self.scheduled = []
        self.fired = set()
        self.opened = set()
        self.missions = {}
        self.finished_missions = set()
        self.misc = defaultdict(float)

    @property
    def sov(self):
        return self.countries['SOV']

    def trigger(self, nodes, tag='SOV', state=None):
        return all(self.condition(key, op, value, tag, state) for key, op, value in nodes)

    def condition(self, key, op, value, tag, state):
        country = self.countries[tag]
        if key in ('AND', 'OR', 'NOT'):
            results = [self.condition(k, o, v, tag, state) for k, o, v in value]
            return any(results) if key == 'OR' else not all(results) if key == 'NOT' else all(results)
        if key in self.countries:
            return self.countries[key].exists and self.trigger(value, key)
        if key in TRIGGERS:
            return self.trigger(TRIGGERS[key], tag, state) == (value == 'yes')
        if key == 'tag': return tag == value
        if key == 'always': return value == 'yes'
        if key == 'exists':
            return country.exists == (value == 'yes') if value in ('yes', 'no') else self.countries[value].exists
        if key == 'is_ai': return country.ai == (value == 'yes')
        if key == 'has_government': return country.government == value
        if key == 'is_subject': return (country.overlord is not None) == (value == 'yes')
        if key == 'is_subject_of': return country.overlord == value
        if key == 'has_war': return bool(country.wars) == (value == 'yes')
        if key == 'has_war_with': return value in country.wars
        if key == 'is_faction_leader': return country.faction_leader == (value == 'yes')
        if key == 'has_country_flag': return value in country.flags
        if key == 'has_idea': return value in country.ideas
        if key == 'has_completed_focus': return value in country.focuses
        if key == 'has_active_mission': return value in self.missions
        if key == 'has_political_power': return COMPARE[op](country.power, float(value))
        if key == 'check_variable':
            pairs = [(k, o, v) for k, o, v in value if k not in ('compare', 'tooltip')]
            assert len(pairs) == 1, 'Fixture only supports the short variable syntax'
            name, comparison, target = pairs[0]
            comparison = (values(value, 'compare') or ['greater_than_or_equals' if comparison == '=' else comparison])[0]
            return COMPARE[comparison](country.variables.get(name, 0), float(target))
        if key == 'power_balance_value':
            _, comparison, target = next(node for node in value if node[0] == 'value')
            return COMPARE[comparison](country.balance, float(target))
        if key == 'any_owned_state':
            return any(self.trigger(value, tag, s) for s in self.states if s.owner == tag)
        if key == 'is_core_of': return value in state.cores
        if key == 'is_controlled_by': return state.controller == ('SOV' if value == 'ROOT' else value)
        if key == 'free_building_slots':
            _, comparison, target = next(node for node in value if node[0] == 'size')
            return COMPARE[comparison](state.slots.get(one(value, 'building'), 0), float(target))
        raise AssertionError('Unsupported story trigger ' + key)

    def run(self, nodes, tag='SOV', state=None):
        branch_taken = None
        for key, _, value in nodes:
            country = self.countries[tag]
            if key == 'if':
                branch_taken = self.trigger(one(value, 'limit'), tag, state)
                if branch_taken: self.run([n for n in value if n[0] != 'limit'], tag, state)
            elif key == 'else_if':
                assert branch_taken is not None
                if not branch_taken and self.trigger(one(value, 'limit'), tag, state):
                    self.run([n for n in value if n[0] != 'limit'], tag, state)
                    branch_taken = True
            elif key == 'else':
                assert branch_taken is not None
                if not branch_taken: self.run(value, tag, state)
                branch_taken = None
            elif key in EFFECTS:
                assert value == 'yes'
                self.run(EFFECTS[key], tag, state)
            elif key in self.countries:
                assert self.countries[key].exists, 'Effect entered a missing country'
                self.run(value, key)
            elif key == 'every_other_country':
                for other, candidate in self.countries.items():
                    if other != tag and candidate.exists and self.trigger(one(value, 'limit'), other):
                        self.run([n for n in value if n[0] != 'limit'], other)
            elif key == 'random_owned_state':
                matches = [s for s in self.states if s.owner == tag and self.trigger(one(value, 'limit'), tag, s)]
                if matches: self.run([n for n in value if n[0] != 'limit'], tag, matches[0])
            elif key == 'set_country_flag':
                flag = one(value, 'flag') if isinstance(value, list) else value
                country.flags[flag] = self.day + int(one(value, 'days')) if isinstance(value, list) else None
            elif key == 'clr_country_flag': country.flags.pop(value, None)
            elif key in ('set_variable', 'add_to_variable', 'subtract_from_variable'):
                for name, _, number in value:
                    if key == 'set_variable': country.variables[name] = float(number)
                    else: country.variables[name] += float(number) * (-1 if key == 'subtract_from_variable' else 1)
            elif key == 'clamp_variable':
                name = one(value, 'var')
                country.variables[name] = max(float(one(value, 'min')), min(float(one(value, 'max')), country.variables[name]))
            elif key == 'add_political_power': country.power += float(value)
            elif key == 'add_stability': country.stability += float(value)
            elif key == 'add_power_balance_value': country.balance = max(-1, min(1, country.balance + float(one(value, 'value'))))
            elif key == 'add_ideas': country.ideas[value] = None
            elif key == 'remove_ideas': country.ideas.pop(value, None)
            elif key == 'add_timed_idea': country.ideas[one(value, 'idea')] = int(one(value, 'days'))
            elif key == 'add_popularity': country.popularity = max(0, min(1, country.popularity + float(one(value, 'popularity'))))
            elif key == 'country_event':
                days = sum(float(n) * factor for unit, factor in (('days', 1), ('months', 30), ('hours', 1/24)) for n in values(value, unit))
                self.scheduled.append((one(value, 'id'), self.day + days))
            elif key == 'activate_mission':
                assert value not in self.missions and value not in self.finished_missions
                self.missions[value] = self.day + int(one(DECISIONS[value], 'days_mission_timeout'))
            elif key == 'add_building_construction':
                assert state is not None
                building, levels = one(value, 'type'), int(one(value, 'level'))
                state.buildings.append((building, levels))
                state.slots[building] -= levels
            elif key in ('army_experience', 'navy_experience', 'air_experience', 'add_war_support'):
                self.misc[key] += float(value)
            elif key == 'add_tech_bonus': self.misc['tech_bonus:' + one(value, 'name')] += int(one(value, 'uses'))
            elif key in ('name', 'ai_chance', 'trigger', 'custom_effect_tooltip'): pass
            else: raise AssertionError('Unsupported story effect ' + key)

    def options(self, event_id):
        event = EVENTS[event_id]
        if event_id in self.fired or not self.trigger(one(event, 'trigger')):
            return []
        if event_id not in self.opened:
            self.opened.add(event_id)
            for immediate in values(event, 'immediate'): self.run(immediate)
        return [option for option in values(event, 'option')
                if not values(option, 'trigger') or self.trigger(one(option, 'trigger'))]

    def choose(self, event_id, name):
        options = {one(option, 'name'): option for option in self.options(event_id)}
        if name not in options: raise ValueError('Story event or option unavailable')
        self.run(options[name])
        self.fired.add(event_id)

    def finish_mission(self, mission_id):
        if mission_id not in self.missions: raise ValueError('Mission is not active')
        decision = DECISIONS[mission_id]
        cost = float(one(decision, 'cost'))
        if self.sov.power < cost or not self.trigger(one(decision, 'available')):
            raise ValueError('Mission cannot be completed')
        self.sov.power -= cost
        self.run(one(decision, 'complete_effect'))
        self.finished_missions.add(mission_id)
        del self.missions[mission_id]

    def advance(self, days):
        self.day += days
        for country in self.countries.values():
            for flag, expiry in list(country.flags.items()):
                if expiry is not None and expiry <= self.day: del country.flags[flag]
        for mission, deadline in list(self.missions.items()):
            decision = DECISIONS[mission]
            cancelled = self.trigger(one(decision, 'cancel_trigger'))
            if cancelled or self.day >= deadline:
                self.run(one(decision, 'cancel_effect' if cancelled else 'timeout_effect'))
                self.finished_missions.add(mission)
                del self.missions[mission]

    def initialize(self):
        self.run(EFFECTS['sr_story_initialize_effect'])


class StoryStructureTests(unittest.TestCase):
    def test_event_ids_unique_and_options_fully_localized_in_both_languages(self):
        self.assertGreaterEqual(len(EVENT_BLOCKS), 30)
        self.assertEqual(len(EVENTS), len(EVENT_BLOCKS))
        required = set()
        for event_id, event in EVENTS.items():
            self.assertEqual(one(event, 'is_triggered_only'), 'yes')
            repeatable = event_id.startswith('sr_socialist_operation.')
            self.assertEqual(one(event, 'fire_only_once'), 'no' if repeatable else 'yes')
            required.add(one(event, 'title'))
            for desc in values(event, 'desc'):
                required.add(one(desc, 'text') if isinstance(desc, list) else desc)
            self.assertTrue(values(event, 'option'), event_id)
            for option in values(event, 'option'):
                required.add(one(option, 'name'))
                self.assertGreater(float(one(one(option, 'ai_chance'), 'base')), 0)
        for language in ('german', 'english'):
            defined = set()
            for path in (MOD/'localisation'/language).glob('*.yml'):
                defined.update(re.findall(r'^ ([\w.]+):0 ', path.read_text(encoding='utf-8-sig'), re.M))
            self.assertLessEqual(required, defined, f'Missing {language}: {required-defined}')

    def test_all_events_reachable_from_real_common_hooks_through_effects(self):
        def references(nodes):
            found = set()
            for key, _, value in walk(nodes):
                if key in EFFECTS and value == 'yes': found.add(('effect', key))
                elif key == 'country_event' and isinstance(value, list): found.add(('event', one(value, 'id')))
            return found
        edges = {('effect', key): references(body) for key, body in EFFECTS.items()}
        edges.update({('event', key): references(body) for key, body in EVENTS.items()})
        reached = set()
        for name, body in SCRIPTS.items():
            if name.startswith('common/') and not name.startswith('common/scripted_effects/'):
                reached.update(references(body))
        pending = list(reached)
        while pending:
            node = pending.pop()
            self.assertIn(node, edges, f'Unknown story reference {node}')
            for target in edges[node] - reached:
                reached.add(target)
                pending.append(target)
        self.assertLessEqual({('event', key) for key in EVENTS}, reached)

    def test_political_power_cost_options_require_an_affordable_budget(self):
        for event_id, event in EVENTS.items():
            for option in values(event, 'option'):
                costs = [-float(value) for key, _, value in option if key == 'add_political_power' and float(value) < 0]
                if not costs: continue
                self.assertTrue(values(option, 'trigger'), (event_id, one(option, 'name')))
                bounds = [(op, float(value)) for key, op, value in walk(one(option, 'trigger')) if key == 'has_political_power']
                self.assertTrue(any((op == '>' and value >= sum(costs)-1) or (op == '>=' and value >= sum(costs))
                                    for op, value in bounds), (event_id, one(option, 'name'), bounds))


class DomesticStoryTests(unittest.TestCase):
    def test_startup_is_idempotent_and_initial_events_have_distinct_dates(self):
        world = StoryWorld(); world.initialize()
        first = list(world.scheduled)
        self.assertEqual(world.sov.variables['sr_story_trust'], 50)
        self.assertEqual({event for event, _ in first}, {'sr_domestic.1', 'sr_domestic.2', 'sr_domestic.3', 'sr_domestic.4'})
        self.assertEqual(sorted(day for _, day in first), [1, 30, 60, 100])
        world.sov.variables['sr_story_trust'] = 63
        world.initialize()
        self.assertEqual(world.scheduled, first)
        self.assertEqual(world.sov.variables['sr_story_trust'], 63)

    def test_opening_choices_lead_to_different_hundred_day_outcomes(self):
        for choices, expected in ((('a', 'a', 'a'), 'mandate'), (('b', 'b', 'b'), 'crisis'), (('c', 'c', 'c'), 'uncertain')):
            with self.subTest(choices=choices):
                world = StoryWorld(); world.initialize()
                for number, letter in zip((1, 2, 3), choices):
                    world.choose(f'sr_domestic.{number}', f'sr_domestic.{number}.{letter}')
                enabled = world.options('sr_domestic.4')
                self.assertEqual(len(enabled), 1)
                world.choose('sr_domestic.4', one(enabled[0], 'name'))
                self.assertIn('sr_story_hundred_days_' + expected, world.sov.flags)
                self.assertEqual('sr_story_government_in_crisis' in world.sov.ideas, expected == 'crisis')

    def test_opening_events_offer_affordable_choices_and_immediate_budget_is_not_duplicated(self):
        world = StoryWorld(); world.initialize(); world.sov.power = 0
        for event_id in ('sr_domestic.1', 'sr_domestic.2', 'sr_domestic.3'):
            world.sov.power = 0
            options = world.options(event_id)
            self.assertTrue(options, event_id)
            budget = world.sov.power
            world.options(event_id)
            self.assertEqual(world.sov.power, budget, 'Immediate budget was granted twice')
            for option in options:
                cost = sum(-float(v) for k, _, v in option if k == 'add_political_power' and float(v) < 0)
                self.assertLessEqual(cost, budget)

    def petitions(self):
        world = StoryWorld(); world.initialize()
        world.run(EFFECTS['sr_story_republic_petitions_effect'])
        first = list(world.scheduled)
        world.run(EFFECTS['sr_story_republic_petitions_effect'])
        self.assertEqual(first, world.scheduled)
        for number in (11, 12, 13): world.choose(f'sr_domestic.{number}', f'sr_domestic.{number}.a')
        return world

    def test_promise_completion_builds_or_grants_autonomy_and_clears_only_its_own_promise(self):
        for republic in ('ukraine', 'georgia', 'kazakhstan'):
            with self.subTest(republic=republic):
                world = self.petitions()
                world.sov.variables['sr_resistance_' + republic] = 10
                mission = 'sr_story_' + republic + '_promise'
                initial_power = world.sov.power
                world.finish_mission(mission)
                self.assertNotIn('sr_story_' + republic + '_promised', world.sov.flags)
                self.assertIn('sr_story_' + republic + '_fulfilled', world.sov.flags)
                self.assertEqual(world.sov.variables['sr_resistance_' + republic], 0)
                self.assertGreater(world.sov.variables['sr_story_trust'], 50)
                self.assertAlmostEqual(world.sov.power, initial_power-float(one(DECISIONS[mission], 'cost')))
                self.assertAlmostEqual(world.sov.balance, 0.19)
                for other in {'ukraine', 'georgia', 'kazakhstan'} - {republic}:
                    self.assertIn('sr_story_' + other + '_promised', world.sov.flags)
                if republic == 'georgia': self.assertIn('sr_story_cultural_autonomy', world.sov.ideas)
                else: self.assertTrue(any(state.buildings for state in world.states))
                with self.assertRaises(ValueError): world.finish_mission(mission)
                world.advance(220)
                self.assertNotIn('sr_story_' + republic + '_broken', world.sov.flags)

    def test_expired_promise_has_opposite_outcome_and_does_not_replay(self):
        world = self.petitions()
        world.advance(150)
        self.assertIn('sr_story_georgia_broken', world.sov.flags)
        self.assertNotIn('sr_story_georgia_promised', world.sov.flags)
        self.assertIn('sr_story_ukraine_promised', world.sov.flags)
        self.assertIn('sr_story_kazakhstan_promised', world.sov.flags)
        self.assertEqual(world.sov.variables['sr_resistance_georgia'], 25)
        self.assertEqual(world.sov.variables['sr_story_trust'], 35)
        first = list(world.scheduled)
        world.advance(1)
        self.assertEqual(world.scheduled, first)
        self.assertAlmostEqual(world.sov.balance, 0.09)
        with self.assertRaises(ValueError): world.finish_mission('sr_story_georgia_promise')

    def test_unaffordable_or_unbuildable_promises_do_not_charge_or_grant_rewards(self):
        for reason in ('budget', 'building_slots'):
            with self.subTest(reason=reason):
                world = self.petitions()
                if reason == 'budget': world.sov.power = 64.5
                else: world.states[0].slots['industrial_complex'] = 0
                before = (world.sov.power, world.sov.variables['sr_story_trust'], world.sov.balance)
                with self.assertRaises(ValueError): world.finish_mission('sr_story_ukraine_promise')
                self.assertEqual(before, (world.sov.power, world.sov.variables['sr_story_trust'], world.sov.balance))
                self.assertIn('sr_story_ukraine_promise', world.missions)
                self.assertNotIn('sr_story_ukraine_fulfilled', world.sov.flags)

    def test_lost_republic_cancels_just_its_promise_without_punishment(self):
        world = self.petitions()
        world.states[0].owner = world.states[0].controller = 'GER'
        world.advance(1)
        self.assertIn('sr_story_ukraine_cancelled', world.sov.flags)
        self.assertNotIn('sr_story_ukraine_promised', world.sov.flags)
        self.assertNotIn('sr_story_ukraine_broken', world.sov.flags)
        self.assertIn('sr_story_georgia_promised', world.sov.flags)
        self.assertEqual(world.sov.variables['sr_story_trust'], 50)
        self.assertAlmostEqual(world.sov.balance, 0.15)

    def test_crisis_alert_is_conditional_and_not_repeated_monthly(self):
        world = StoryWorld(); world.initialize()
        world.run(EFFECTS['sr_story_monthly_effect'])
        self.assertNotIn('sr_domestic.20', [event for event, _ in world.scheduled])
        world.sov.balance = -0.7
        world.sov.variables['sr_resistance_ukraine'] = 60
        for _ in range(4): world.run(EFFECTS['sr_story_monthly_effect'])
        self.assertEqual([event for event, _ in world.scheduled].count('sr_domestic.20'), 1)

    def test_trust_and_resistance_changes_clamp_at_both_boundaries(self):
        world = self.petitions()
        world.sov.variables['sr_story_trust'] = 99
        world.finish_mission('sr_story_georgia_promise')
        self.assertEqual(world.sov.variables['sr_story_trust'], 100)
        world.sov.variables['sr_story_trust'] = 2
        world.sov.variables['sr_resistance_ukraine'] = 99
        world.advance(180)
        self.assertEqual(world.sov.variables['sr_story_trust'], 0)
        self.assertEqual(world.sov.variables['sr_resistance_ukraine'], 100)


class BalkanStoryTests(unittest.TestCase):
    def test_contacts_start_once_and_schedule_backlash_even_if_yugoslavia_is_missing(self):
        world = StoryWorld(); world.initialize(); world.countries['YUG'].exists = False
        for _ in range(2): world.run(EFFECTS['sr_story_balkan_contacts_effect'])
        ids = [event for event, _ in world.scheduled]
        self.assertNotIn('sr_balkan_story.1', ids)
        self.assertEqual(ids.count('sr_balkan_story.3'), 1)

    def test_delayed_support_rechecks_humans_wars_subjects_and_communist_governments(self):
        for effect, gain in (('cultural', .03), ('underground', .06), ('retreat', -.02)):
            with self.subTest(effect=effect):
                world = StoryWorld()
                world.countries['ALB'].ai = False
                world.countries['BUL'].wars.add('SOV')
                world.countries['GRE'].overlord = 'GER'
                world.countries['ROM'].government = 'communism'
                world.run(EFFECTS['sr_story_balkan_' + effect + '_result_effect'])
                self.assertAlmostEqual(world.countries['YUG'].popularity, .25+gain)
                for tag in ('ALB', 'BUL', 'GRE', 'ROM', 'GER', 'SOV'):
                    self.assertEqual(world.countries[tag].popularity, .25, tag)

    def test_federation_story_requires_designated_safe_subject_and_starts_only_once(self):
        world = StoryWorld(); world.initialize()
        hook = EFFECTS['sr_story_balkan_federation_effect']
        world.run(hook)
        self.assertNotIn('sr_balkan_story.7', [event for event, _ in world.scheduled])
        yug = world.countries['YUG']
        yug.flags['sr_balkan_federal_state'] = None
        yug.overlord = 'SOV'
        for _ in range(3): world.run(hook)
        self.assertEqual([event for event, _ in world.scheduled].count('sr_balkan_story.7'), 1)
        world.choose('sr_balkan_story.7', 'sr_bs_7_a')
        self.assertIn('sr_bs_republic_assembly', yug.ideas)
        yug.overlord = 'GER'
        self.assertFalse(world.options('sr_balkan_story.8'))
        with self.assertRaises(ValueError): world.choose('sr_balkan_story.8', 'sr_bs_8_a')


class FocusStoryTests(unittest.TestCase):
    def test_factory_choice_changes_its_delayed_report_and_cannot_be_farmed(self):
        outcomes = []
        for choice, followup in (('councils', 'councils'), ('director', 'directors')):
            with self.subTest(choice=choice):
                world = StoryWorld(); world.initialize()
                world.choose('sr_focus_story.1', 'sr_focus_story_1_' + choice)
                self.assertIn(('sr_focus_story.9', 90), world.scheduled)
                options = world.options('sr_focus_story.9')
                self.assertEqual([one(option, 'name') for option in options], ['sr_focus_story_9_' + followup])
                world.choose('sr_focus_story.9', one(options[0], 'name'))
                with self.assertRaises(ValueError): world.choose('sr_focus_story.9', one(options[0], 'name'))
                outcomes.append((world.sov.variables['sr_story_trust'], world.sov.stability, set(world.sov.ideas)))
        self.assertNotEqual(outcomes[0], outcomes[1])

    def test_final_report_reacts_to_low_and_high_trust_without_dead_end(self):
        for trust, option in ((0, 'contested'), (64, 'contested'), (65, 'trusted'), (100, 'trusted')):
            with self.subTest(trust=trust):
                world = StoryWorld(); world.initialize(); world.sov.variables['sr_story_trust'] = trust
                options = world.options('sr_focus_story.8')
                self.assertEqual([one(o, 'name') for o in options], ['sr_focus_story_8_' + option])


if __name__ == '__main__':
    unittest.main(verbosity=2)
