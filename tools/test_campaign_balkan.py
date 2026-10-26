"""Execute the 0.5 Balkan campaign AST in the limited story fixture.

These checks exercise native-script conditions and consequences, not the HOI4
engine, UI, diplomacy AI or real calendar timing.
"""
from copy import deepcopy
import unittest

from test_story import EFFECTS, EVENTS, StoryWorld
from validate_mod import one, values, walk


PREFIX = 'sr_campaign_balkan.'
MONTHLY = 'sr_campaign_balkan_monthly_effect'
KARDELJ = 'YUG_sr_edvard_kardelj'
COUNCIL = 'YUG_sr_balkan_federal_council'


class BalkanCampaignWorld(StoryWorld):
    def __init__(self):
        super().__init__()
        self.sov.flags.update({'sr_lito_initialized': None,
                               'sr_story_first_hundred_days': None})
        self.sov.variables['sr_story_trust'] = 50
        self.sov.leader = 'SOV_cosif_kozs_lito'
        self.sov.focuses.add('sr_lito_balkan_partnership')
        self.countries['YUG'].government = 'communism'
        self.countries['YUG'].leader = KARDELJ

    def condition(self, key, op, value, tag, state):
        if key == 'has_country_leader':
            return getattr(self.countries[tag], 'leader', None) == one(value, 'character')
        return super().condition(key, op, value, tag, state)

    def monthly(self):
        self.run(EFFECTS[MONTHLY])

    def choose_flag(self, number, flag):
        event_id = PREFIX + str(number)
        candidates = [option for option in self.options(event_id)
                      if ('set_country_flag', '=', flag) in list(walk(option))]
        if len(candidates) != 1:
            raise AssertionError(f'Expected one available {event_id} option setting {flag}')
        self.choose(event_id, one(candidates[0], 'name'))

    def choose_first(self, number):
        event_id = PREFIX + str(number)
        options = self.options(event_id)
        if not options:
            raise AssertionError(f'No available choice in {event_id}')
        self.choose(event_id, one(options[0], 'name'))


class BalkanCampaignTests(unittest.TestCase):
    def test_monthly_shared_cooldown_prevents_reentry_and_preserves_milestone_priority(self):
        world = BalkanCampaignWorld()
        world.monthly()
        self.assertEqual([event for event, _ in world.scheduled], [PREFIX + '1'])
        self.assertIn('sr_cb_kardelj_started', world.sov.flags)
        self.assertIn('sr_campaign_event_cooldown', world.sov.flags)
        world.sov.flags['sr_slavic_union_proclaimed'] = None
        for _ in range(4):
            world.monthly()
        self.assertEqual(len(world.scheduled), 1)
        world.advance(60)
        world.monthly()
        self.assertEqual([event for event, _ in world.scheduled], [PREFIX + '1', PREFIX + '7'])
        self.assertIn('sr_cb_charter_started', world.sov.flags)
        world.advance(60)
        yug = world.countries['YUG']
        yug.flags['sr_balkan_federal_state'] = None
        yug.overlord, yug.leader = 'SOV', COUNCIL
        world.sov.flags['sr_bs_federal_grievance'] = None
        world.monthly()
        self.assertEqual([event for event, _ in world.scheduled],
                         [PREFIX + '1', PREFIX + '7', PREFIX + '4'])
        self.assertIn('sr_cb_federation_started', world.sov.flags)
        world.advance(60)
        world.monthly()
        self.assertEqual(len(world.scheduled), 3)

    def test_delayed_kardelj_negotiations_recheck_the_current_foreign_government(self):
        for restriction in ('missing', 'human', 'hostile', 'foreign_subject', 'noncommunist', 'other_leader'):
            with self.subTest(restriction=restriction):
                world = BalkanCampaignWorld()
                world.monthly()
                world.choose_flag(1, 'sr_cb_reciprocity')
                world.advance(90)
                yug = world.countries['YUG']
                if restriction == 'missing': yug.exists = False
                elif restriction == 'human': yug.ai = False
                elif restriction == 'hostile': yug.wars.add('SOV')
                elif restriction == 'foreign_subject': yug.overlord = 'GER'
                elif restriction == 'noncommunist': yug.government = 'neutrality'
                else: yug.leader = 'other_leader'
                before = deepcopy(vars(yug))
                self.assertEqual(world.options(PREFIX + '2'), [])
                self.assertEqual(vars(yug), before)

    def test_reciprocal_and_directed_trade_paths_have_different_delayed_results(self):
        results = []
        for opening, customs in (('sr_cb_reciprocity', 'sr_cb_customs_joint'),
                                 ('sr_cb_instructions', 'sr_cb_customs_directed')):
            world = BalkanCampaignWorld()
            world.monthly()
            world.choose_flag(1, opening)
            world.advance(90)
            world.choose_flag(2, customs)
            world.advance(90)
            world.choose_first(3)
            yug = world.countries['YUG']
            results.append((world.sov.variables['sr_story_trust'],
                            deepcopy(world.sov.ideas), deepcopy(yug.ideas)))
            self.assertEqual(yug.leader, KARDELJ)
            self.assertEqual(world.sov.leader, 'SOV_cosif_kozs_lito')
            self.assertEqual(world.options(PREFIX + '3'), [])
        self.assertNotEqual(results[0], results[1])
        self.assertGreater(results[0][0], results[1][0])

    def test_slavic_charter_continues_after_yugoslavia_has_been_annexed(self):
        world = BalkanCampaignWorld()
        world.countries['YUG'].exists = False
        world.sov.flags['sr_slavic_union_proclaimed'] = None
        world.monthly()
        self.assertEqual([event for event, _ in world.scheduled], [PREFIX + '7'])
        world.choose_flag(7, 'sr_cb_charter_plural')
        world.advance(120)
        world.choose_flag(8, 'sr_cb_charter_revised')
        world.advance(120)
        world.choose_first(9)
        self.assertFalse(world.countries['YUG'].exists)
        self.assertTrue(0 <= world.sov.variables['sr_story_trust'] <= 100)
        self.assertEqual(world.options(PREFIX + '9'), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
