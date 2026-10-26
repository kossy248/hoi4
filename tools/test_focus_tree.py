"""Regression checks for the actual expanded focus scripts and reproducible build.

Reachability tests cover prerequisites and mutual exclusions. They deliberately
ignore country availability/bypass conditions and do not emulate the HOI4 engine.
"""
from collections import defaultdict
from itertools import product
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unittest

from validate_mod import MOD, REPUBLICS, ROOT, one, parse, values, walk
from test_union_resistance import ScriptHarness
from test_story import StoryWorld


FOCUS_PATH = MOD/'common/national_focus/sr_soviet.txt'


def load_focuses():
    tree = one(parse(FOCUS_PATH.read_text(encoding='utf-8-sig')), 'focus_tree')
    return values(tree, 'focus')


def prerequisite_groups(focus):
    return [values(group, 'focus') for group in values(focus, 'prerequisite')]


def excluded(focus):
    return {key for group in values(focus, 'mutually_exclusive') for key in values(group, 'focus')}


def reachable(focuses, forbidden=frozenset()):
    done = set()
    changed = True
    while changed:
        changed = False
        for key, focus in focuses.items():
            if key in done or key in forbidden or excluded(focus) & done:
                continue
            if all(set(group) & done for group in prerequisite_groups(focus)):
                done.add(key)
                changed = True
    return done


def localized_keys(language):
    result = set()
    for path in (MOD/f'localisation/{language}').glob('*.yml'):
        result.update(re.findall(r'^ ([A-Za-z0-9_]+):0 ', path.read_text(encoding='utf-8-sig'), re.M))
    return result


class ExpandedFocusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blocks = load_focuses()
        cls.focuses = {one(focus, 'id'): focus for focus in cls.blocks}

    def test_one_hundred_two_unique_focuses_and_real_rewards(self):
        self.assertEqual(len(self.blocks), 102)
        self.assertEqual(len(self.focuses), 102)
        for key, focus in self.focuses.items():
            with self.subTest(focus=key):
                self.assertTrue(one(focus, 'completion_reward'), 'Every focus needs a gameplay reward')
                self.assertIn(int(one(focus, 'cost')), (5, 8, 10))

    def test_dependencies_form_a_dag_with_known_parents(self):
        active, visited = set(), set()

        def visit(key):
            self.assertNotIn(key, active, f'Focus cycle at {key}')
            if key in visited:
                return
            active.add(key)
            for group in prerequisite_groups(self.focuses[key]):
                self.assertTrue(group, f'Empty prerequisite block in {key}')
                for parent in group:
                    self.assertIn(parent, self.focuses, f'Undefined parent in {key}')
                    visit(parent)
            active.remove(key)
            visited.add(key)

        for key in self.focuses:
            visit(key)
        self.assertEqual(visited, set(self.focuses))
        roots = {key for key, focus in self.focuses.items() if not prerequisite_groups(focus)}
        self.assertEqual(roots, {'sr_lito_course'})

    def test_layout_has_no_overlapping_focuses_and_descends(self):
        occupied = defaultdict(list)
        for key, focus in self.focuses.items():
            point = (int(one(focus, 'x')), int(one(focus, 'y')))
            occupied[point].append(key)
            for group in prerequisite_groups(focus):
                for parent in group:
                    self.assertLess(int(one(self.focuses[parent], 'y')), point[1],
                                    f'Backward/equal-height prerequisite {parent} -> {key}')
        self.assertFalse({point: keys for point, keys in occupied.items() if len(keys) > 1})

    def test_mutual_exclusions_are_symmetric_and_four_binary_choices(self):
        pairs = set()
        for key, focus in self.focuses.items():
            for other in excluded(focus):
                self.assertIn(other, self.focuses)
                self.assertNotEqual(key, other)
                self.assertIn(key, excluded(self.focuses[other]))
                pairs.add(tuple(sorted((key, other))))
        self.assertEqual(len(pairs), 4)
        self.assertEqual(len({key for pair in pairs for key in pair}), 8)

    def test_every_choice_reaches_preservation_and_every_focus_can_be_reached(self):
        pairs = sorted({tuple(sorted((key, other)))
                        for key, focus in self.focuses.items() for other in excluded(focus)})
        all_reachable = set()
        for choices in product((0, 1), repeat=len(pairs)):
            forbidden = {pair[1-choice] for pair, choice in zip(pairs, choices)}
            completed = reachable(self.focuses, forbidden)
            with self.subTest(selected=tuple(pair[choice] for pair, choice in zip(pairs, choices))):
                self.assertIn('sr_lito_union_future', completed,
                              'The main ending must work after every legitimate choice')
                for pair, choice in zip(pairs, choices):
                    self.assertIn(pair[choice], completed)
                    self.assertNotIn(pair[1-choice], completed)
            all_reachable.update(completed)
        self.assertEqual(all_reachable, set(self.focuses),
                         'Every focus must be reachable for at least one choice combination')

    def test_exactly_one_additional_research_slot(self):
        slots = [(key, value) for key, focus in self.focuses.items()
                 for effect, _, value in walk(one(focus, 'completion_reward'))
                 if effect == 'add_research_slot']
        self.assertEqual(len(slots), 1, slots)
        self.assertEqual(slots[0][1], '1')

    def test_succession_event_has_different_paid_and_centralized_outcomes(self):
        for choice, trust, flag, balance in (
                ('a', 58, 'sr_exp_binding_succession', 0.19),
                ('b', 42, 'sr_exp_party_succession', 0.11)):
            with self.subTest(choice=choice):
                game = StoryWorld()
                game.sov.flags['sr_lito_initialized'] = None
                game.sov.variables['sr_story_trust'] = 50
                before = game.sov.power
                game.choose('sr_expansion.2', f'sr_exp_2_{choice}')
                self.assertEqual(game.sov.variables['sr_story_trust'], trust)
                self.assertIn(flag, game.sov.flags)
                self.assertAlmostEqual(game.sov.balance, balance)
                self.assertEqual(game.sov.power, before + (-50 if choice == 'a' else 50))
                with self.assertRaises(ValueError):
                    game.choose('sr_expansion.2', f'sr_exp_2_{choice}')

    def test_timed_ideas_exist_and_research_bonus_names_are_unique_localized(self):
        ideas = set()
        for path in (MOD/'common/ideas').glob('*.txt'):
            nodes = parse(path.read_text(encoding='utf-8-sig'))
            ideas.update(key for key, _, _ in one(one(nodes, 'ideas'), 'country'))
        names = []
        for focus in self.focuses.values():
            for effect, _, body in walk(one(focus, 'completion_reward')):
                if effect == 'add_timed_idea':
                    self.assertIn(one(body, 'idea'), ideas)
                    durations = [float(value) for unit in ('days', 'months', 'years') for value in values(body, unit)]
                    self.assertEqual(len(durations), 1)
                    self.assertGreater(durations[0], 0)
                elif effect in ('add_tech_bonus', 'add_doctrine_cost_reduction'):
                    names.append(one(body, 'name'))
        self.assertTrue(names)
        self.assertEqual(len(names), len(set(names)), 'Named bonuses should identify their distinct focus source')
        for language in ('german', 'english'):
            self.assertLessEqual(set(names), localized_keys(language))

    def test_focus_rewards_do_not_declare_war_or_transfer_territory(self):
        forbidden = {'declare_war_on', 'annex_country', 'transfer_state', 'set_state_owner',
                     'set_state_controller', 'puppet', 'set_autonomy', 'release', 'create_country'}
        for key, focus in self.focuses.items():
            effects = {effect for effect, _, body in walk(one(focus, 'completion_reward'))}
            self.assertFalse(effects & forbidden, f'Unexpected automatic war or territory change in {key}')

    def test_political_influence_is_in_existing_foreign_country_scope(self):
        influence_focuses, targets = set(), set()

        def inspect(nodes, guarded=frozenset(), target=None, focus_id=None):
            for key, _, body in nodes:
                if not isinstance(body, list):
                    continue
                if key in ('if', 'else_if'):
                    limit = one(body, 'limit')
                    # The existence check must be an affirmative direct condition.
                    existing = {value for trigger, op, value in limit if trigger == 'exists' and op == '='}
                    inspect([node for node in body if node[0] != 'limit'], guarded | existing, target, focus_id)
                elif re.fullmatch('[A-Z]{3}', key):
                    inspect(body, guarded, key, focus_id)
                elif key == 'add_popularity':
                    self.assertIsNotNone(target, f'Influence applied to domestic country in {focus_id}')
                    self.assertIn(target, guarded, f'No matching existence guard for {target} in {focus_id}')
                    self.assertEqual(one(body, 'ideology'), 'communism')
                    self.assertGreater(float(one(body, 'popularity')), 0)
                    self.assertLessEqual(float(one(body, 'popularity')), 0.10)
                    influence_focuses.add(focus_id)
                    targets.add(target)
                else:
                    inspect(body, guarded, target, focus_id)

        for key, focus in self.focuses.items():
            inspect(one(focus, 'completion_reward'), focus_id=key)
        self.assertEqual(len(influence_focuses), 5)
        self.assertEqual(targets, {'YUG', 'ALB', 'BUL', 'GRE', 'ROM'})

    def test_federal_recovery_targets_active_republics_clamps_and_refreshes(self):
        path = MOD/'common/scripted_effects/sr_lito_focus_effects.txt'
        effect = one(parse(path.read_text(encoding='utf-8-sig')), 'sr_lito_reduce_republic_resistance_effect')
        blocks = values(effect, 'if')
        self.assertEqual(len(blocks), len(REPUBLICS))
        for republic, block in zip(REPUBLICS, blocks):
            self.assertEqual(one(block, 'limit'), [(f'sr_union_{republic}_represented', '=', 'yes')])
            self.assertEqual(one(block, 'subtract_from_variable'), [(f'sr_resistance_{republic}', '=', '5')])
            clamp = one(block, 'clamp_variable')
            self.assertEqual((one(clamp, 'var'), one(clamp, 'min'), one(clamp, 'max')),
                             (f'sr_resistance_{republic}', '0', '100'))
        self.assertEqual(effect[-1], ('sr_update_union_resistance_ideas_effect', '=', 'yes'))
        game = ScriptHarness()
        game.variables = {'sr_resistance_' + r: 3 for r in REPUBLICS[:11]}
        game.variables['sr_resistance_russia'] = 80
        game.variables['sr_resistance_estonia'] = 100  # Inactive values must not be changed or count as unrest.
        game.run(effect)
        self.assertEqual(game.resistance('russia'), 75)
        self.assertEqual([game.resistance(r) for r in REPUBLICS[1:11]], [0] * 10)
        self.assertEqual(game.resistance('estonia'), 100)
        self.assertEqual(game.ideas, {'sr_union_mass_strikes'})
        game.variables['sr_resistance_russia'] = 4
        game.run(effect)
        self.assertEqual(game.resistance('russia'), 0)
        self.assertFalse(game.ideas)

    @unittest.skipUnless(shutil.which('dot'), 'Graphviz is optional for source checks; diagram rebuild test requires dot')
    def test_rebuilding_twice_is_byte_deterministic(self):
        generated = [
            FOCUS_PATH, MOD/'common/ideas/sr_ideas.txt',
            MOD/'common/opinion_modifiers/sr_lito_opinions.txt',
            MOD/'common/scripted_effects/sr_lito_focus_effects.txt',
            MOD/'interface/sr_focus_icons.gfx',
            MOD/'localisation/german/sr_l_german.yml',
            MOD/'localisation/english/sr_l_english.yml',
            ROOT/'docs/focus_manifest.json', ROOT/'docs/FOKUSBAUM.md',
            ROOT/'docs/focus_tree.dot', ROOT/'docs/focus_tree.svg',
            ROOT/'soviet_renewal.mod', MOD/'descriptor.mod',
        ]

        def build_snapshot():
            completed = subprocess.run([sys.executable, str(ROOT/'tools/build_focus_tree.py')],
                                       cwd=ROOT, capture_output=True, text=True, timeout=60)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            return {path.relative_to(ROOT).as_posix(): path.read_bytes() for path in generated}

        self.assertEqual(build_snapshot(), build_snapshot())


if __name__ == '__main__':
    unittest.main(verbosity=2)
