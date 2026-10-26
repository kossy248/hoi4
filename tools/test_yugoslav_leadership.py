"""Execute the actual Kardelj replacement effect in a small country fixture.

This checks the replacement and guards; it does not emulate the HOI4 engine.
"""
from dataclasses import dataclass, field
import unittest

from validate_mod import MOD, one, parse


KARDELJ = 'YUG_sr_edvard_kardelj'
COUNCIL = 'YUG_sr_balkan_federal_council'
EFFECT = one(parse((MOD/'common/scripted_effects/sr_yugoslav_leadership_effects.txt')
                   .read_text(encoding='utf-8-sig')),
             'sr_ensure_yugoslav_communist_leader_effect')


@dataclass
class Country:
    exists: bool = True
    government: str = 'communism'
    leader: str = 'old_communist_leader'
    characters: set = field(default_factory=set)
    flags: set = field(default_factory=set)


class World:
    def __init__(self):
        self.countries = {
            'SOV': Country(leader='SOV_cosif_kozs_lito'),
            'YUG': Country(),
        }
        self.recruitments = 0
        self.promotions = 0

    def trigger(self, nodes, tag):
        results = []
        country = self.countries[tag]
        for key, _, value in nodes:
            if key == 'NOT':
                results.append(not self.trigger(value, tag))
            elif key == 'exists':
                results.append(self.countries[value].exists)
            elif key == 'has_government':
                results.append(country.government == value)
            elif key == 'has_country_flag':
                results.append(value in country.flags)
            elif key == 'has_character':
                results.append(value in country.characters)
            elif key == 'has_country_leader':
                assert one(value, 'ruling_only') == 'yes'
                results.append(country.leader == one(value, 'character'))
            else:
                raise AssertionError('Unsupported leadership trigger ' + key)
        return all(results)

    def run(self, nodes=EFFECT, tag='SOV'):
        for key, _, value in nodes:
            country = self.countries[tag]
            if key == 'if':
                if self.trigger(one(value, 'limit'), tag):
                    self.run([node for node in value if node[0] != 'limit'], tag)
            elif key in self.countries:
                assert self.countries[key].exists, 'Entered a missing country scope'
                self.run(value, key)
            elif key == 'recruit_character':
                assert value not in country.characters, 'Duplicate recruitment'
                country.characters.add(value)
                self.recruitments += 1
            elif key == 'promote_character':
                character = one(value, 'character')
                assert character in country.characters
                assert one(value, 'ideology') == 'titoism'
                country.leader = character
                self.promotions += 1
            else:
                raise AssertionError('Unsupported leadership effect ' + key)


class YugoslavLeadershipTests(unittest.TestCase):
    def test_communist_yugoslavia_gets_kardelj_and_lito_remains_in_soviet_union(self):
        world = World()
        world.run()
        self.assertEqual(world.countries['YUG'].leader, KARDELJ)
        self.assertEqual(world.countries['SOV'].leader, 'SOV_cosif_kozs_lito')
        self.assertEqual((world.recruitments, world.promotions), (1, 1))

    def test_missing_yugoslavia_is_not_entered_or_recreated(self):
        world = World()
        world.countries['YUG'].exists = False
        world.run()
        self.assertEqual((world.recruitments, world.promotions), (0, 0))
        self.assertFalse(world.countries['YUG'].exists)

    def test_noncommunist_governments_keep_their_leader(self):
        for government in ('neutrality', 'democratic', 'fascism'):
            with self.subTest(government=government):
                world = World()
                world.countries['YUG'].government = government
                world.run()
                self.assertEqual(world.countries['YUG'].leader, 'old_communist_leader')
                self.assertEqual((world.recruitments, world.promotions), (0, 0))

    def test_repeated_calls_do_not_recruit_or_promote_again(self):
        world = World()
        for _ in range(12):
            world.run()
        self.assertEqual((world.recruitments, world.promotions), (1, 1))

    def test_already_recruited_kardelj_is_promoted_without_duplicate(self):
        world = World()
        world.countries['YUG'].characters.add(KARDELJ)
        world.run()
        self.assertEqual(world.countries['YUG'].leader, KARDELJ)
        self.assertEqual((world.recruitments, world.promotions), (0, 1))

    def test_later_communist_switch_and_restoration_both_get_kardelj(self):
        world = World()
        yug = world.countries['YUG']
        yug.government = 'neutrality'
        world.run()
        yug.government = 'communism'
        world.run()
        self.assertEqual(yug.leader, KARDELJ)
        yug.government, yug.leader = 'fascism', 'other_leader'
        world.run()
        self.assertEqual(yug.leader, 'other_leader')
        yug.government = 'communism'
        world.run()
        self.assertEqual(yug.leader, KARDELJ)
        self.assertEqual((world.recruitments, world.promotions), (1, 2))

    def test_federation_flag_protects_collective_government(self):
        world = World()
        world.countries['YUG'].flags.add('sr_balkan_federal_state')
        world.run()
        self.assertEqual((world.recruitments, world.promotions), (0, 0))

    def test_federal_council_is_protected_even_if_its_flag_has_not_yet_been_set(self):
        world = World()
        world.countries['YUG'].leader = COUNCIL
        world.run()
        self.assertEqual(world.countries['YUG'].leader, COUNCIL)
        self.assertEqual((world.recruitments, world.promotions), (0, 0))

    def test_character_has_matching_ideology_and_dedicated_portrait_reference(self):
        nodes = parse((MOD/'common/characters/sr_kardelj.txt').read_text())
        character = one(one(nodes, 'characters'), KARDELJ)
        self.assertEqual(one(one(character, 'country_leader'), 'ideology'), 'titoism')
        portrait = one(one(one(character, 'portraits'), 'civilian'), 'large')
        self.assertEqual(portrait, 'GFX_sr_kardelj_portrait')


if __name__ == '__main__':
    unittest.main(verbosity=2)
