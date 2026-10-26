"""Exercise the actual native operation completion in a limited country fixture.

This verifies scopes, eligibility and the political effect; it cannot simulate
La Resistance operation UI, operative risks or engine preparation costs.
"""
from dataclasses import dataclass, field
import unittest

from validate_mod import MOD, one, parse, values, walk


def load(path):
    return parse((MOD/path).read_text(encoding='utf-8-sig'))


OPERATION = one(load('common/operations/sr_socialist_operations.txt'), 'sr_operation_red_dawn')
PHASES = {key: body for key, _, body in load('common/operation_phases/sr_socialist_operation_phases.txt')}
TRIGGERS = {key: body for key, _, body in load('common/scripted_triggers/sr_socialist_operation_triggers.txt')}
EFFECTS = {key: body for filename in ('sr_socialist_operation_effects.txt', 'sr_yugoslav_leadership_effects.txt')
           for key, _, body in load('common/scripted_effects/' + filename)}


@dataclass
class Country:
    exists: bool = True
    government: str = 'neutrality'
    popularity: float = 0.10
    power: float = 500
    ai: bool = True
    agency: bool = False
    flags: dict = field(default_factory=dict)
    faction: str = None
    overlord: str = None
    wars: set = field(default_factory=set)
    characters: set = field(default_factory=set)
    leader: str = 'old_leader'


class OperationWorld:
    def __init__(self, target='GER', actor='SOV'):
        self.actor, self.target, self.day = actor, target, 0
        self.countries = {'SOV': Country(government='communism', ai=False, agency=True,
                                         flags={'sr_lito_initialized': None}, leader='SOV_cosif_kozs_lito'),
                          'YUG': Country()}
        if target not in self.countries:
            self.countries[target] = Country()
        if actor not in self.countries:
            self.countries[actor] = Country(government='communism', ai=False, agency=True,
                                             flags={'sr_lito_initialized': None})
        self.events, self.event_targets = [], {}
        self.dlc = True

    def scope(self, key):
        return self.actor if key == 'ROOT' else self.target if key == 'FROM' else key

    def trigger(self, nodes, tag):
        result = []
        country = self.countries[tag]
        for key, op, value in nodes:
            if key == 'NOT': result.append(not self.trigger(value, tag))
            elif key in TRIGGERS: result.append(self.trigger(TRIGGERS[key], tag) == (value == 'yes'))
            elif key in ('ROOT', 'FROM') or key in self.countries:
                result.append(self.trigger(value, self.scope(key)))
            elif key == 'exists': result.append(country.exists == (value == 'yes') if value in ('yes', 'no') else self.countries[value].exists)
            elif key == 'tag': result.append(tag == self.scope(value))
            elif key == 'has_government': result.append(country.government == value)
            elif key == 'has_country_flag': result.append(value in country.flags)
            elif key == 'is_ai': result.append(country.ai == (value == 'yes'))
            elif key == 'has_dlc': result.append(self.dlc and value.strip('"') == 'La Resistance')
            elif key == 'has_intelligence_agency': result.append(country.agency == (value == 'yes'))
            elif key == 'has_political_power':
                assert op == '>'
                result.append(country.power > float(value))
            elif key == 'has_character': result.append(value in country.characters)
            elif key == 'has_country_leader': result.append(country.leader == one(value, 'character'))
            else: raise AssertionError('Unsupported operation trigger: ' + key)
        return all(result)

    def run(self, nodes, tag=None):
        tag = tag or self.actor
        country = self.countries[tag]
        for key, _, value in nodes:
            if key == 'if':
                if self.trigger(one(value, 'limit'), tag): self.run([n for n in value if n[0] != 'limit'], tag)
            elif key in ('ROOT', 'FROM') or key in self.countries:
                self.run(value, self.scope(key))
            elif key in EFFECTS: self.run(EFFECTS[key], tag)
            elif key == 'add_political_power': country.power += float(value)
            elif key == 'add_popularity':
                assert one(value, 'ideology') == 'communism'
                country.popularity = min(1, country.popularity + float(one(value, 'popularity')))
            elif key == 'set_politics': country.government = one(value, 'ruling_party')
            elif key == 'set_country_flag': country.flags[one(value, 'flag')] = self.day + int(one(value, 'days'))
            elif key == 'save_event_target_as': self.event_targets[value] = tag
            elif key == 'country_event': self.events.append((tag, one(value, 'id')))
            elif key == 'recruit_character': country.characters.add(value)
            elif key == 'promote_character': country.leader = one(value, 'character')
            else: raise AssertionError('Unsupported operation effect: ' + key)

    def available(self):
        return all(self.trigger(one(OPERATION, block), self.actor)
                   for block in ('allowed', 'visible', 'available', 'requirements'))

    def start(self):
        if not self.available(): raise ValueError('Operation unavailable')
        self.run(one(OPERATION, 'on_start'))

    def complete(self):
        self.run(one(OPERATION, 'outcome_execute'))


class SocialistOperationTests(unittest.TestCase):
    def test_native_operation_has_three_ordered_phases_and_explicit_requirements(self):
        self.assertEqual((one(OPERATION, 'days'), one(OPERATION, 'operatives'), one(OPERATION, 'network_strength')),
                         ('90', '2', '50'))
        groups = values(OPERATION, 'phases')
        self.assertEqual(len(groups), 3)
        self.assertEqual([group[0][0] for group in groups], list(PHASES))
        self.assertFalse(values(OPERATION, 'operation_target'), 'No tag whitelist should restrict the worldwide operation')
        self.assertEqual(one(one(OPERATION, 'ai_will_do'), 'factor'), '0')

    def test_worldwide_targets_change_immediately_without_changing_foreign_relationships(self):
        for target in ('GER', 'USA', 'CHI', 'JAP', 'MEX', 'ENG', 'LUX', 'TAN', 'ZZZ'):
            with self.subTest(target=target):
                world = OperationWorld(target)
                foreign = world.countries[target]
                foreign.faction, foreign.overlord, foreign.wars = 'existing_faction', 'ENG', {'ITA'}
                foreign.ai = False  # Worldwide means no unrequested human-country exclusion.
                relations = (foreign.faction, foreign.overlord, set(foreign.wars))
                self.assertTrue(world.available())
                world.start()
                self.assertEqual(world.countries['SOV'].power, 425)
                world.complete()
                self.assertEqual(foreign.government, 'communism')
                self.assertAlmostEqual(foreign.popularity, .70)
                self.assertEqual((foreign.faction, foreign.overlord, foreign.wars), relations)
                self.assertEqual(world.countries['SOV'].government, 'communism')
                self.assertEqual(world.countries['SOV'].leader, 'SOV_cosif_kozs_lito')
                self.assertEqual(world.event_targets['sr_socialist_revolution_target'], target)
                self.assertEqual(world.events, [(target, 'sr_socialist_operation.2'), ('SOV', 'sr_socialist_operation.1')])

    def test_unavailable_for_self_missing_communist_or_recently_converted_targets(self):
        for restriction in ('self', 'missing', 'communist', 'cooldown'):
            with self.subTest(restriction=restriction):
                world = OperationWorld('SOV' if restriction == 'self' else 'GER')
                target = world.countries[world.target]
                if restriction == 'missing': target.exists = False
                if restriction == 'communist': target.government = 'communism'
                if restriction == 'cooldown': target.flags['sr_socialist_operation_recent_revolution'] = 365
                self.assertFalse(world.available())
                before = (target.government, target.popularity)
                world.complete()
                self.assertEqual((target.government, target.popularity), before)
                self.assertFalse(world.events)

    def test_launch_requires_dlc_agency_budget_and_the_lito_player(self):
        for restriction in ('dlc', 'agency', 'budget', 'ai', 'uninitialized', 'non_soviet'):
            with self.subTest(restriction=restriction):
                world = OperationWorld(actor='USA' if restriction == 'non_soviet' else 'SOV')
                actor = world.countries[world.actor]
                if restriction == 'dlc': world.dlc = False
                if restriction == 'agency': actor.agency = False
                if restriction == 'budget': actor.power = 74
                if restriction == 'ai': actor.ai = True
                if restriction == 'uninitialized': actor.flags.clear()
                before = actor.power
                with self.assertRaises(ValueError): world.start()
                self.assertEqual(actor.power, before)

    def test_resolution_rechecks_target_and_cannot_apply_twice(self):
        world = OperationWorld(); world.start()
        world.countries['GER'].exists = False
        world.complete()
        self.assertEqual(world.countries['GER'].government, 'neutrality')
        self.assertFalse(world.events)
        world.countries['GER'].exists = True
        world.complete()
        first = list(world.events)
        world.complete()
        self.assertEqual(world.events, first)
        world.countries['GER'].government = 'democratic'
        self.assertFalse(world.available(), 'A counterrevolution must not bypass the 365-day protection')
        world.countries['GER'].flags.clear()
        self.assertTrue(world.available())

    def test_communist_yugoslavia_gets_kardelj_instead_of_tito(self):
        world = OperationWorld('YUG')
        world.start(); world.complete()
        self.assertEqual(world.countries['YUG'].government, 'communism')
        self.assertEqual(world.countries['YUG'].leader, 'YUG_sr_edvard_kardelj')

    def test_completion_has_no_war_annexation_or_puppet_effect(self):
        forbidden = {'annex_country', 'declare_war_on', 'puppet', 'set_autonomy', 'leave_faction', 'add_to_faction', 'transfer_state'}
        for body in EFFECTS.values():
            self.assertFalse({key for key, _, _ in walk(body)} & forbidden)


if __name__ == '__main__':
    unittest.main(verbosity=2)
