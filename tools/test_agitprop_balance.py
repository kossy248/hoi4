"""Exercise Union policies and retirement of the removed standalone agitprop."""
import unittest

from test_story import StoryWorld, EFFECTS, SCRIPTS
from validate_mod import MOD, one, parse, values


def load(relative):
    return parse((MOD/relative).read_text(encoding='utf-8-sig'))


CATEGORIES = {
    'sr_union_council': one(load('common/decisions/categories/sr_union_categories.txt'), 'sr_union_council'),
}
POLICIES = dict((key, body) for key, _, body in one(load('common/decisions/sr_union_policies.txt'), 'sr_union_council'))


class PolicyWorld(StoryWorld):
    def __init__(self):
        super().__init__()
        self.sov.flags.update({key: None for key in ('sr_lito_initialized', 'sr_story_initialized', 'sr_union_initialized')})
        self.sov.variables['sr_story_trust'] = 50
        self.cooldowns = {}
        self.completed_decisions = set()
        self.idea_expiry = {}

    def run(self, nodes, tag='SOV', state=None):
        for key, _, value in nodes:
            if key == 'add_timed_idea':
                self.idea_expiry[(tag, one(value, 'idea'))] = self.day + float(one(value, 'days'))
        super().run(nodes, tag, state)

    def ready(self, key, tag='SOV'):
        body = POLICIES[key]
        category = CATEGORIES['sr_union_council']
        return (key not in self.completed_decisions
                and self.day >= self.cooldowns.get(key, 0)
                and self.countries[tag].power >= float(one(body, 'cost'))
                and self.trigger(one(category, 'allowed'), tag)
                and self.trigger(one(category, 'visible'), tag)
                and self.trigger(one(body, 'visible'), tag)
                and self.trigger(one(body, 'available'), tag))

    def activate(self, key, tag='SOV'):
        if not self.ready(key, tag):
            raise ValueError('Decision unavailable')
        body = POLICIES[key]
        self.countries[tag].power -= float(one(body, 'cost'))
        self.run(one(body, 'complete_effect'), tag)
        self.cooldowns[key] = self.day + int((values(body, 'days_re_enable') or ['0'])[0])
        if values(body, 'fire_only_once') == ['yes']:
            self.completed_decisions.add(key)

    def advance(self, days):
        super().advance(days)
        for (tag, idea), deadline in list(self.idea_expiry.items()):
            if deadline <= self.day:
                self.countries[tag].ideas.pop(idea, None)
                del self.idea_expiry[(tag, idea)]


class UnionPolicyTests(unittest.TestCase):
    def test_reserve_has_no_instant_reward_and_can_only_be_released_once_in_crisis(self):
        world = PolicyWorld(); world.sov.variables['sr_story_trust'] = 60
        world.activate('sr_union_prepare_budget_reserve')
        self.assertEqual(world.sov.power, 440)
        self.assertFalse(world.ready('sr_union_release_budget_reserve'))
        world.sov.balance = -0.30
        world.activate('sr_union_release_budget_reserve')
        self.assertEqual(world.sov.power, 525)
        self.assertNotIn('sr_union_budget_reserve', world.sov.flags)
        self.assertFalse(world.ready('sr_union_release_budget_reserve'))
        self.assertFalse(world.ready('sr_union_prepare_budget_reserve'))

    def test_unused_reserve_expires_without_a_reward(self):
        world = PolicyWorld(); world.sov.variables['sr_story_trust'] = 60
        world.activate('sr_union_prepare_budget_reserve')
        world.advance(365); world.sov.balance = -0.50
        self.assertFalse(world.ready('sr_union_release_budget_reserve'))
        self.assertEqual(world.sov.power, 440)

    def test_amnesty_only_reduces_resistance_in_represented_republics(self):
        world = PolicyWorld()
        world.sov.variables.update(sr_story_trust=99, sr_resistance_ukraine=80,
                                   sr_resistance_georgia=7, sr_resistance_kazakhstan=3,
                                   sr_resistance_estonia=100)
        world.activate('sr_union_republic_amnesty')
        self.assertEqual(world.sov.variables['sr_resistance_ukraine'], 65)
        self.assertEqual(world.sov.variables['sr_resistance_georgia'], 0)
        self.assertEqual(world.sov.variables['sr_resistance_kazakhstan'], 0)
        self.assertEqual(world.sov.variables['sr_resistance_estonia'], 100)
        self.assertEqual(world.sov.variables['sr_story_trust'], 100)

    def test_emergency_powers_need_war_and_crisis_and_cannot_be_farmed(self):
        world = PolicyWorld()
        self.assertFalse(world.ready('sr_union_central_emergency_powers'))
        world.sov.wars.add('GER')
        self.assertFalse(world.ready('sr_union_central_emergency_powers'))
        world.sov.balance = -0.30
        world.sov.variables['sr_story_trust'] = 4
        world.activate('sr_union_central_emergency_powers')
        self.assertEqual(world.sov.variables['sr_story_trust'], 0)
        self.assertAlmostEqual(world.sov.balance, -0.42)
        world.advance(365)
        self.assertFalse(world.ready('sr_union_central_emergency_powers'))

    def test_peace_and_war_policies_have_distinct_availability(self):
        world = PolicyWorld(); world.sov.focuses.add('sr_lito_federal_plan')
        self.assertTrue(world.ready('sr_union_public_plan_audit'))
        self.assertFalse(world.ready('sr_union_joint_war_council'))
        world.sov.wars.add('GER')
        self.assertFalse(world.ready('sr_union_public_plan_audit'))
        self.assertTrue(world.ready('sr_union_joint_war_council'))


class LegacyAgitpropRemovalTests(unittest.TestCase):
    def test_old_campaign_state_is_removed_without_resetting_the_government(self):
        world = PolicyWorld()
        slots = ('star', 'peoples', 'steel', 'councils', 'sky', 'horizon', 'earth', 'light')
        old_flags = {'sr_agitprop_active', *(f'sr_agitprop_{slot}_active' for slot in slots)}
        old_ideas = {f'sr_agitprop_{slot}_spirit' for slot in slots}
        world.sov.flags.update({key: None for key in old_flags})
        world.sov.ideas.update({key: 100 for key in old_ideas})
        world.sov.ideas['sr_story_cultural_autonomy'] = None
        world.sov.variables['sr_story_trust'] = 67
        world.sov.balance = -0.35
        world.run(EFFECTS['sr_retire_legacy_agitprop_effect'])
        self.assertFalse(old_flags & world.sov.flags.keys())
        self.assertFalse(old_ideas & world.sov.ideas.keys())
        self.assertIn('sr_legacy_agitprop_removed', world.sov.flags)
        self.assertIn('sr_story_cultural_autonomy', world.sov.ideas)
        self.assertEqual(world.sov.variables['sr_story_trust'], 67)
        self.assertEqual(world.sov.balance, -0.35)
        snapshot = (dict(world.sov.flags), dict(world.sov.ideas), world.sov.power)
        world.run(EFFECTS['sr_retire_legacy_agitprop_effect'])
        self.assertEqual((world.sov.flags, world.sov.ideas, world.sov.power), snapshot)

    def test_cleanup_ignores_other_countries_and_uninitialized_soviets(self):
        world = PolicyWorld()
        for tag in ('YUG', 'SOV'):
            country = world.countries[tag]
            if tag == 'YUG':
                country.flags['sr_lito_initialized'] = None
            else:
                country.flags.pop('sr_lito_initialized')
            country.flags['sr_agitprop_active'] = None
            country.ideas['sr_agitprop_star_spirit'] = 90
            world.run(EFFECTS['sr_retire_legacy_agitprop_effect'], tag)
            self.assertIn('sr_agitprop_active', country.flags)
            self.assertIn('sr_agitprop_star_spirit', country.ideas)
            self.assertNotIn('sr_legacy_agitprop_removed', country.flags)

    def test_removed_category_cannot_start_new_campaigns_and_retired_ideas_are_inert(self):
        decision_scripts = {name: nodes for name, nodes in SCRIPTS.items()
                            if name.startswith('common/decisions/')}
        for name, nodes in decision_scripts.items():
            self.assertFalse(values(nodes, 'sr_agitprop'), name)
        retired = one(one(load('common/ideas/sr_deprecated_agitprop_ideas.txt'), 'ideas'), 'country')
        self.assertEqual(len(retired), 8)
        for key, _, body in retired:
            self.assertEqual(one(one(body, 'allowed'), 'always'), 'no', key)
            self.assertEqual(one(one(body, 'visible'), 'always'), 'no', key)
            self.assertFalse(values(body, 'modifier'), key)


if __name__ == '__main__':
    unittest.main(verbosity=2)
