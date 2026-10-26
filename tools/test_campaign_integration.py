"""Execute campaign coordination and project outcomes, without the HOI4 engine."""
import unittest

from test_story import DECISIONS, EFFECTS, StoryWorld
from test_campaign_balkan import BalkanCampaignWorld
from validate_mod import one


class ProjectWorld(StoryWorld):
    def __init__(self):
        super().__init__()
        self.initialize()
        self.sov.flags.update({'sr_lito_initialized': None,
                               'sr_story_first_hundred_days': None,
                               'sr_fs_workers_decide': None})
        self.sov.focuses.update({'sr_lito_workers_councils', 'sr_lito_academy_network',
                                 'sr_lito_army_supply'})
        self.run(EFFECTS['sr_campaign_initialize_effect'])

    def start(self, project):
        body = DECISIONS['sr_project_start_' + project]
        cost = float(one(body, 'cost'))
        if (not self.trigger(one(body, 'visible')) or
                not self.trigger(one(body, 'available')) or self.sov.power < cost):
            raise ValueError('Project unavailable')
        self.sov.power -= cost
        self.run(one(body, 'complete_effect'))


class ProjectIntegrationTests(unittest.TestCase):
    def test_only_one_project_at_a_time_and_no_repeat_after_completion(self):
        world = ProjectWorld()
        world.start('workshops')
        for target in ('workshops', 'education', 'supply'):
            with self.assertRaises(ValueError): world.start(target)
        power = world.sov.power
        with self.assertRaises(ValueError): world.finish_mission('sr_project_finish_workshops')
        self.assertEqual(world.sov.power, power)
        world.advance(90)
        world.choose('sr_projects.2', 'sr_projects_2_a')
        world.sov.focuses.add('sr_lito_regional_workshops')
        world.finish_mission('sr_project_finish_workshops')
        self.assertNotIn('sr_project_active', world.sov.flags)
        self.assertIn('sr_project_workshops_completed', world.sov.flags)
        self.assertIn('sr_project_practical_councils', world.sov.ideas)
        self.assertNotIn('sr_project_workshop_budget', world.sov.ideas)
        with self.assertRaises(ValueError): world.start('workshops')
        world.start('education')
        self.assertIn('sr_project_education_active', world.sov.flags)

    def test_failure_or_government_change_releases_lock_and_budget(self):
        for cancelled in (False, True):
            with self.subTest(cancelled=cancelled):
                world = ProjectWorld(); world.start('workshops')
                if cancelled: world.sov.government = 'neutrality'
                world.advance(1 if cancelled else 240)
                self.assertNotIn('sr_project_active', world.sov.flags)
                self.assertNotIn('sr_project_workshops_active', world.sov.flags)
                self.assertNotIn('sr_project_workshop_budget', world.sov.ideas)
                self.assertIn('sr_project_workshops_' + ('cancelled' if cancelled else 'failed'), world.sov.flags)
                self.assertNotIn('sr_project_practical_councils', world.sov.ideas)

    def test_education_and_supply_need_midpoint_and_specific_completed_focuses(self):
        for project, number, option, focuses in (
                ('education', 5, 'sr_projects_5_a', {'sr_lito_technical_education'}),
                ('supply', 8, 'sr_projects_8_a', {'sr_lito_supply_corridors'})):
            with self.subTest(project=project):
                world = ProjectWorld(); world.start(project)
                mission = 'sr_project_finish_' + project
                with self.assertRaises(ValueError): world.finish_mission(mission)
                world.advance(90)
                world.choose(f'sr_projects.{number}', option)
                with self.assertRaises(ValueError): world.finish_mission(mission)
                world.sov.focuses.update(focuses)
                world.finish_mission(mission)
                self.assertIn('sr_project_' + project + '_completed', world.sov.flags)
                self.assertNotIn('sr_project_active', world.sov.flags)


class CampaignCoordinatorTests(unittest.TestCase):
    def test_init_preserves_existing_story_and_pending_project(self):
        world = ProjectWorld(); world.start('education')
        world.sov.variables['sr_story_trust'] = 73
        before = list(world.scheduled)
        for _ in range(3): world.run(EFFECTS['sr_campaign_initialize_effect'])
        self.assertEqual(world.sov.variables['sr_story_trust'], 73)
        self.assertEqual(world.scheduled, before)
        self.assertIn('sr_project_education_active', world.sov.flags)

    def test_domestic_and_foreign_openings_share_one_automatic_slot(self):
        world = BalkanCampaignWorld(); world.initialize()
        world.sov.flags['sr_fs_workers_decide'] = None
        world.sov.focuses.add('sr_lito_politics_constitution')
        world.scheduled.clear()
        world.run(EFFECTS['sr_campaign_monthly_effect'])
        self.assertEqual([key for key, _ in world.scheduled], ['sr_campaign_dom.1'])
        world.run(EFFECTS['sr_campaign_monthly_effect'])
        self.assertEqual(len(world.scheduled), 1)
        world.advance(60)
        world.run(EFFECTS['sr_campaign_monthly_effect'])
        self.assertEqual([key for key, _ in world.scheduled],
                         ['sr_campaign_dom.1', 'sr_campaign_balkan.1'])

    def test_non_soviet_monthly_scope_does_not_start_campaigns(self):
        world = BalkanCampaignWorld(); world.initialize()
        world.scheduled.clear()
        world.run(EFFECTS['sr_campaign_monthly_effect'], tag='YUG')
        self.assertEqual(world.scheduled, [])
        self.assertNotIn('sr_campaign_initialized', world.countries['YUG'].flags)


if __name__ == '__main__':
    unittest.main(verbosity=2)
