"""Regression tests of parsed formable-decision scripts, not an HOI4 emulator."""
import unittest
from dataclasses import dataclass
from validate_mod import MOD, one, parse


def load(relative):
    return parse((MOD / relative).read_text(encoding='utf-8-sig'))


TRIGGERS = {key: body for key, _, body in load('common/scripted_triggers/sr_formable_triggers.txt')}
DECISION = one(one(load('common/decisions/sr_formable_decisions.txt'), 'sr_formable_union'),
               'sr_proclaim_slavic_union')
TAGS = ('POL', 'YUG', 'ALB', 'BUL', 'GRE', 'ROM', 'TUR')


@dataclass
class State:
    name: str
    cores: set
    owner: str = 'SOV'
    controller: str = 'SOV'


class FormableHarness:
    def __init__(self):
        self.tag, self.subject, self.at_war = 'SOV', False, False
        self.flags = {'sr_lito_initialized'}
        self.power, self.stability, self.balance, self.cosmetic = 200, 0.5, 0.0, None
        self.states = [State(f'{tag}-{index}', {tag}) for tag in TAGS for index in (1, 2)]
        self.states.append(State('unrelated', {'GER'}, 'GER', 'GER'))

    def trigger(self, nodes, state=None):
        return all([self.condition(key, value, state) for key, _, value in nodes])

    def condition(self, key, value, state):
        if key in TRIGGERS:
            assert value in ('yes', 'no')
            return self.trigger(TRIGGERS[key], state) == (value == 'yes')
        if key in ('AND', 'OR', 'NOT'):
            results = [self.condition(k, v, state) for k, _, v in value]
            return any(results) if key == 'OR' else not all(results) if key == 'NOT' else all(results)
        if key == 'custom_trigger_tooltip':
            return self.trigger([node for node in value if node[0] != 'tooltip'], state)
        if key == 'any_state':
            return any([self.trigger(value, candidate) for candidate in self.states])
        if key in ('is_core_of', 'is_owned_by', 'is_controlled_by'):
            assert state is not None
            if key == 'is_core_of':
                return value in state.cores
            target = self.tag if value == 'ROOT' else value
            return (state.owner if key == 'is_owned_by' else state.controller) == target
        if key == 'tag':
            return self.tag == value
        if key == 'is_subject':
            return self.subject == (value == 'yes')
        if key == 'has_country_flag':
            return value in self.flags
        if key == 'has_war':
            return self.at_war == (value == 'yes')
        raise AssertionError(f'Unsupported trigger {key}')

    def ready(self):
        return (self.trigger(one(DECISION, 'visible')) and
                self.trigger(one(DECISION, 'available')) and self.power >= float(one(DECISION, 'cost')))

    def proclaim(self):
        if not self.ready():
            raise ValueError('Decision unavailable')
        self.power -= float(one(DECISION, 'cost'))
        for key, _, value in one(DECISION, 'complete_effect'):
            if key == 'set_country_flag':
                self.flags.add(value)
            elif key == 'set_cosmetic_tag':
                self.cosmetic = value
            elif key == 'add_stability':
                self.stability += float(value)
            elif key == 'add_power_balance_value':
                assert one(value, 'id') == 'sr_union_balance'
                self.balance += float(one(value, 'value'))
            else:
                raise AssertionError(f'Unsupported effect {key}')


class FormableUnionTests(unittest.TestCase):
    def test_all_core_territory_allows_proclamation_during_war(self):
        game = FormableHarness()
        game.at_war = True
        self.assertTrue(game.ready())
        game.proclaim()
        self.assertEqual(game.tag, 'SOV')
        self.assertEqual(game.cosmetic, 'SOV_LITO_SFSU')
        self.assertEqual(game.power, 100)
        self.assertAlmostEqual(game.stability, 0.55)
        self.assertAlmostEqual(game.balance, 0.10)

    def test_each_required_country_needs_every_core_state(self):
        for tag in TAGS:
            with self.subTest(country=tag):
                game = FormableHarness()
                next(s for s in game.states if s.name == f'{tag}-2').owner = tag
                self.assertFalse(game.ready())

    def test_occupation_ownership_and_subject_land_are_distinct(self):
        for owner, controller in (('TUR', 'SOV'), ('SOV', 'TUR'), ('PUP', 'SOV'), ('SOV', 'PUP')):
            with self.subTest(owner=owner, controller=controller):
                game = FormableHarness()
                target = next(s for s in game.states if 'TUR' in s.cores)
                target.owner, target.controller = owner, controller
                self.assertFalse(game.ready())

    def test_non_soviet_subject_and_uninitialized_countries_cannot_form(self):
        for restriction in ('tag', 'subject', 'initialization'):
            with self.subTest(restriction=restriction):
                game = FormableHarness()
                if restriction == 'tag':
                    game.tag = 'YUG'
                elif restriction == 'subject':
                    game.subject = True
                else:
                    game.flags.clear()
                self.assertFalse(game.ready())

    def test_empty_core_definition_does_not_pass_vacuously(self):
        game = FormableHarness()
        game.states = [state for state in game.states if 'TUR' not in state.cores]
        self.assertFalse(game.ready())

    def test_proclamation_is_one_time_and_does_not_change_territory(self):
        game = FormableHarness()
        original = [(s.name, set(s.cores), s.owner, s.controller) for s in game.states]
        self.assertEqual(one(DECISION, 'fire_only_once'), 'yes')
        game.proclaim()
        self.assertIn('sr_slavic_union_proclaimed', game.flags)
        self.assertFalse(game.ready())
        with self.assertRaises(ValueError):
            game.proclaim()
        self.assertEqual(original, [(s.name, s.cores, s.owner, s.controller) for s in game.states])
        self.assertEqual(game.power, 100)

    def test_insufficient_political_power_blocks_decision(self):
        game = FormableHarness()
        game.power = 99
        self.assertFalse(game.ready())


if __name__ == '__main__':
    unittest.main(verbosity=2)
