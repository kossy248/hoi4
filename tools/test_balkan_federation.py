"""Execute actual Balkan decision AST against a small world fixture, not HOI4."""
import operator
import unittest
from dataclasses import dataclass, field
from validate_mod import MOD, one, parse, values


def load(path):
    return parse((MOD / path).read_text(encoding='utf-8-sig'))


MEMBERS = {'yugoslavia': 'YUG', 'albania': 'ALB', 'bulgaria': 'BUL', 'greece': 'GRE', 'romania': 'ROM'}
TRIGGERS = {k: v for p in ('sr_balkan_triggers.txt', 'sr_formable_triggers.txt')
            for k, _, v in load('common/scripted_triggers/' + p)}
EFFECTS = {k: v for p in ('sr_balkan_effects.txt', 'sr_balkan_story_effects.txt')
           for k, _, v in load('common/scripted_effects/' + p)}
CATEGORY = one(load('common/decisions/categories/sr_balkan_categories.txt'), 'sr_balkan_federation')
DECISIONS = {k: v for k, _, v in one(load('common/decisions/sr_balkan_federation_decisions.txt'), 'sr_balkan_federation')}
FORMABLE = one(one(load('common/decisions/sr_formable_decisions.txt'), 'sr_formable_union'), 'sr_proclaim_slavic_union')


@dataclass
class Country:
    exists: bool = True
    ai: bool = True
    government: str = 'communism'
    popularity: float = 0.20
    overlord: str = None
    wars: set = field(default_factory=set)
    faction: str = None
    faction_leader: bool = False
    flags: set = field(default_factory=set)
    focuses: set = field(default_factory=set)
    ideas: dict = field(default_factory=dict)
    characters: set = field(default_factory=set)
    troops: int = 10
    leader: str = 'old_leader'
    cosmetic: str = None
    elections: bool = True


@dataclass
class State:
    owner: str
    controller: str
    cores: set


class World:
    def __init__(self):
        self.countries = {tag: Country() for tag in ('SOV', *MEMBERS.values(), 'GER', 'POL', 'TUR')}
        self.countries['SOV'].flags.add('sr_lito_initialized')
        self.countries['SOV'].ai = False
        self.countries['SOV'].leader = 'SOV_cosif_kozs_lito'
        self.states = [State(tag, tag, {tag}) for tag in MEMBERS.values() for _ in range(2)]
        self.states += [State('SOV', 'SOV', {'POL'}), State('SOV', 'SOV', {'TUR'}), State('GER', 'GER', {'GER'})]
        self.power, self.day, self.cooldowns, self.fired = 2000, 0, {}, set()
        self.events = []

    def trigger(self, body, tag='SOV', state=None):
        return all([self.condition(k, op, v, tag, state) for k, op, v in body])

    def condition(self, key, op, value, tag, state):
        country = self.countries[tag]
        if key in self.countries:
            return self.trigger(value, key)
        if key in TRIGGERS:
            assert value in ('yes', 'no')
            return self.trigger(TRIGGERS[key], tag, state) == (value == 'yes')
        if key in ('AND', 'OR', 'NOT'):
            results = [self.condition(k, o, v, tag, state) for k, o, v in value]
            return any(results) if key == 'OR' else not all(results) if key == 'NOT' else all(results)
        if key == 'custom_trigger_tooltip':
            return self.trigger([n for n in value if n[0] != 'tooltip'], tag, state)
        if key == 'any_state':
            return any([self.trigger(value, tag, candidate) for candidate in self.states])
        if key in ('is_core_of', 'is_owned_by', 'is_controlled_by'):
            assert state is not None
            if key == 'is_core_of':
                return value in state.cores
            expected = 'SOV' if value == 'ROOT' else value
            return (state.owner if key == 'is_owned_by' else state.controller) == expected
        if key == 'tag': return tag == value
        if key == 'exists':
            return self.countries[value].exists if value in self.countries else country.exists == (value == 'yes')
        if key == 'is_ai': return country.ai == (value == 'yes')
        if key == 'is_subject': return (country.overlord is not None) == (value == 'yes')
        if key == 'is_subject_of': return country.overlord == value
        if key == 'has_war': return bool(country.wars) == (value == 'yes')
        if key == 'has_war_with': return value in country.wars
        if key == 'has_government': return country.government == value
        if key == 'is_in_faction': return (country.faction is not None) == (value == 'yes')
        if key == 'is_faction_leader': return country.faction_leader == (value == 'yes')
        if key == 'is_in_faction_with': return country.faction is not None and country.faction == self.countries[value].faction
        if key == 'has_country_flag': return value in country.flags
        if key == 'has_completed_focus': return value in country.focuses
        if key == 'communism':
            return {'<': operator.lt, '>': operator.gt, '=': operator.eq}[op](country.popularity, float(value))
        raise AssertionError('Unsupported trigger ' + key)

    def ready(self, decision):
        body = DECISIONS[decision]
        return (decision not in self.fired and self.day >= self.cooldowns.get(decision, 0)
                and self.power >= float(one(body, 'cost')) and self.trigger(one(CATEGORY, 'allowed'))
                and self.trigger(one(CATEGORY, 'visible')) and self.trigger(one(body, 'visible'))
                and self.trigger(one(body, 'available')))

    def activate(self, decision):
        if not self.ready(decision): raise ValueError('Decision unavailable')
        body = DECISIONS[decision]
        self.power -= float(one(body, 'cost'))
        self.run(one(body, 'complete_effect'))
        if values(body, 'days_re_enable'):
            self.cooldowns[decision] = self.day + int(one(body, 'days_re_enable'))
        if values(body, 'fire_only_once') == ['yes']: self.fired.add(decision)

    def run(self, nodes, tag='SOV', state=None):
        for key, _, value in nodes:
            country = self.countries[tag]
            if key in self.countries: self.run(value, key)
            elif key in EFFECTS:
                assert value == 'yes'
                self.run(EFFECTS[key], tag, state)
            elif key == 'if':
                if self.trigger(one(value, 'limit'), tag, state):
                    self.run([n for n in value if n[0] != 'limit'], tag, state)
            elif key == 'add_popularity':
                assert one(value, 'ideology') == 'communism'
                country.popularity = min(1, country.popularity + float(one(value, 'popularity')))
            elif key == 'add_timed_idea': country.ideas[one(value, 'idea')] = int(one(value, 'days'))
            elif key == 'set_politics':
                country.government = one(value, 'ruling_party')
                country.elections = one(value, 'elections_allowed') == 'yes'
            elif key == 'annex_country':
                target = one(value, 'target')
                for province in self.states:
                    if province.owner == target: province.owner, province.controller = tag, tag
                if one(value, 'transfer_troops') == 'yes': country.troops += self.countries[target].troops
                self.countries[target].exists = False
                self.countries[target].faction = None
            elif key == 'every_owned_state':
                for province in self.states:
                    if province.owner == tag and self.trigger(one(value, 'limit'), tag, province):
                        self.run([n for n in value if n[0] != 'limit'], tag, province)
            elif key == 'add_core_of':
                assert state is not None
                state.cores.add(value)
            elif key == 'set_cosmetic_tag': country.cosmetic = value
            elif key == 'recruit_character': country.characters.add(value)
            elif key == 'promote_character':
                character = one(value, 'character')
                assert character in country.characters
                assert one(value, 'ideology') == 'titoism'
                country.leader = character
            elif key == 'puppet':
                assert one(value, 'end_wars') == one(value, 'end_civil_wars') == 'no'
                self.countries[one(value, 'target')].overlord = tag
            elif key == 'set_country_flag': country.flags.add(value)
            elif key == 'country_event': self.events.append((tag, one(value, 'id')))
            elif key == 'leave_faction':
                assert value == 'yes'
                country.faction = None
            else: raise AssertionError('Unsupported effect ' + key)

    def enable_federation(self):
        self.countries['SOV'].focuses.add('sr_lito_balkan_cooperation')


class BalkanFederationTests(unittest.TestCase):
    def test_propaganda_and_government_form_a_repeatable_political_ladder(self):
        game = World()
        target = game.countries['BUL']
        target.government, target.popularity = 'neutrality', 0.52
        propaganda = 'sr_balkan_propaganda_bulgaria'
        government = 'sr_balkan_socialist_government_bulgaria'
        self.assertFalse(game.ready(propaganda))
        game.countries['SOV'].focuses.add('sr_lito_influence_bulgaria')
        self.assertFalse(game.ready(government))
        game.activate(propaganda)
        self.assertAlmostEqual(target.popularity, 0.60)
        self.assertEqual(target.ideas, {'sr_lito_balkan_influence_network': 365})
        self.assertFalse(game.ready(propaganda))
        self.assertTrue(game.ready(government))
        game.activate(government)
        self.assertEqual(target.government, 'communism')
        self.assertFalse(target.elections)
        self.assertTrue(target.exists)
        self.assertFalse(target.wars)
        self.assertIsNone(target.overlord)
        game.day = 180
        self.assertTrue(game.ready(propaganda))
        target.government = 'neutrality'
        self.assertFalse(game.ready(government))
        game.day = 365
        self.assertTrue(game.ready(government))

    def test_influence_rejects_missing_human_hostile_or_foreign_subject_targets(self):
        for restriction in ('missing', 'human', 'hostile', 'foreign_subject'):
            with self.subTest(restriction=restriction):
                game = World()
                game.countries['SOV'].focuses.add('sr_lito_influence_greece')
                target = game.countries['GRE']
                if restriction == 'missing': target.exists = False
                if restriction == 'human': target.ai = False
                if restriction == 'hostile': target.wars.add('SOV')
                if restriction == 'foreign_subject': target.overlord = 'GER'
                self.assertFalse(game.ready('sr_balkan_propaganda_greece'))
        game = World()
        game.countries['SOV'].focuses.add('sr_lito_influence_greece')
        game.countries['GRE'].overlord = 'SOV'
        self.assertTrue(game.ready('sr_balkan_propaganda_greece'))

    def test_each_of_five_members_must_be_communist_peaceful_ai_and_not_foreign_subject(self):
        for tag in MEMBERS.values():
            for restriction in ('government', 'war', 'human', 'foreign_subject', 'faction_leader'):
                with self.subTest(tag=tag, restriction=restriction):
                    game = World(); game.enable_federation()
                    target = game.countries[tag]
                    if restriction == 'government': target.government = 'neutrality'
                    if restriction == 'war': target.wars.add('GER')
                    if restriction == 'human': target.ai = False
                    if restriction == 'foreign_subject': target.overlord = 'GER'
                    if restriction == 'faction_leader': target.faction, target.faction_leader = 'foreign', True
                    self.assertFalse(game.ready('sr_balkan_form_federation'))

    def test_federation_transfers_to_host_and_creates_one_puppet_with_separate_leader(self):
        game = World(); game.enable_federation()
        game.countries['ALB'].overlord = 'SOV'
        game.states.append(State('ALB', 'ALB', {'GER'}))  # Non-home colonial core stays non-core.
        game.activate('sr_balkan_form_federation')
        self.assertTrue(game.countries['YUG'].exists)
        self.assertEqual(game.countries['YUG'].overlord, 'SOV')
        self.assertEqual(game.countries['YUG'].troops, 50)
        self.assertEqual(game.countries['YUG'].leader, 'YUG_sr_balkan_federal_council')
        self.assertEqual(game.countries['SOV'].leader, 'SOV_cosif_kozs_lito')
        self.assertTrue(all(not game.countries[tag].exists for tag in ('ALB', 'BUL', 'GRE', 'ROM')))
        for state in game.states[:10]:
            self.assertEqual((state.owner, state.controller), ('YUG', 'YUG'))
            self.assertIn('YUG', state.cores)
        self.assertNotIn('YUG', game.states[-1].cores)
        self.assertEqual(game.states[-2].owner, 'GER')
        self.assertFalse(game.ready('sr_balkan_form_federation'))
        self.assertFalse(game.trigger(one(FORMABLE, 'available')))

    def test_peaceful_foreign_faction_members_can_leave_without_disbanding_their_faction(self):
        game = World(); game.enable_federation()
        for tag in MEMBERS.values(): game.countries[tag].faction = 'foreign'
        game.countries['GER'].faction, game.countries['GER'].faction_leader = 'foreign', True
        self.assertTrue(game.ready('sr_balkan_form_federation'))
        game.activate('sr_balkan_form_federation')
        self.assertIsNone(game.countries['YUG'].faction)
        self.assertEqual(game.countries['GER'].faction, 'foreign')
        self.assertTrue(game.countries['GER'].faction_leader)

    def test_sponsor_needs_focus_independence_and_peace(self):
        for restriction in ('focus', 'subject', 'war', 'initialization'):
            with self.subTest(restriction=restriction):
                game = World(); game.enable_federation()
                if restriction == 'focus': game.countries['SOV'].focuses.clear()
                if restriction == 'subject': game.countries['SOV'].overlord = 'GER'
                if restriction == 'war': game.countries['SOV'].wars.add('GER')
                if restriction == 'initialization': game.countries['SOV'].flags.clear()
                self.assertFalse(game.ready('sr_balkan_form_federation'))

    def test_integration_requires_poland_turkey_and_the_designated_safe_subject(self):
        decision = 'sr_balkan_integrate_federation'
        for restriction in ('turkey', 'poland', 'foreign_master', 'human', 'war'):
            with self.subTest(restriction=restriction):
                game = World(); game.enable_federation(); game.activate('sr_balkan_form_federation')
                if restriction in ('turkey', 'poland'):
                    tag = 'TUR' if restriction == 'turkey' else 'POL'
                    next(s for s in game.states if tag in s.cores).owner = tag
                if restriction == 'foreign_master': game.countries['YUG'].overlord = 'GER'
                if restriction == 'human': game.countries['YUG'].ai = False
                if restriction == 'war': game.countries['YUG'].wars.add('GER')
                self.assertFalse(game.ready(decision))
        game = World(); game.enable_federation(); game.activate('sr_balkan_form_federation')
        self.assertTrue(game.ready(decision))
        game.activate(decision)
        self.assertFalse(game.countries['YUG'].exists)
        self.assertTrue(all(s.owner == 'SOV' for s in game.states[:12]))
        self.assertTrue(game.trigger(one(FORMABLE, 'available')))
        self.assertEqual(game.countries['SOV'].leader, 'SOV_cosif_kozs_lito')
        self.assertIsNone(game.countries['SOV'].cosmetic)
        self.assertFalse(game.ready(decision))


if __name__ == '__main__':
    unittest.main(verbosity=2)
