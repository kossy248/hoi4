"""Verify that every custom focus and balance icon is wired to a valid DDS."""
from pathlib import Path
import hashlib
import json
import re
import struct
import unittest

from test_focus_tree import load_focuses
from validate_mod import MOD, ROOT, one


PLAN_PATH = ROOT/'tools/gfx_plan.json'
GFX_PATH = MOD/'interface/sr_focus_icons.gfx'
BOP_PATH = MOD/'common/bop/sr_union_balance.txt'


class FocusGfxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assets = json.loads(PLAN_PATH.read_text(encoding='utf-8'))['items']
        cls.by_id = {asset['id']: asset for asset in cls.assets}
        cls.focuses = {one(focus, 'id'): focus for focus in load_focuses()}

    def test_plan_has_exactly_78_focuses_and_two_balance_icons(self):
        self.assertEqual(len(self.assets), 80)
        self.assertEqual(len(self.by_id), 80)
        self.assertEqual(len(self.focuses), 102)
        self.assertLessEqual({asset['id'] for asset in self.assets[:78]}, set(self.focuses))
        self.assertEqual({asset['id'] for asset in self.assets[78:]},
                         {'sr_union_collapse', 'sr_union_preservation'})

    def test_every_focus_uses_its_planned_unique_sprite(self):
        used = set()
        for key, focus in self.focuses.items():
            sprite = one(focus, 'icon')
            if key in self.by_id:
                self.assertEqual(sprite, self.by_id[key]['sprite'])
            else:
                self.assertIn(sprite, {asset['sprite'] for asset in self.assets[:78]})
            self.assertNotEqual(sprite, 'GFX_goal_generic_national_unity')
            used.add(sprite)
        self.assertEqual(len(used), 78)

    def test_gfx_database_defines_every_planned_sprite_and_texture(self):
        text = GFX_PATH.read_text(encoding='utf-8')
        blocks = re.findall(r'spriteType\s*=\s*\{(.*?)\}', text, re.S)
        definitions = {}
        for block in blocks:
            name = re.search(r'name\s*=\s*"([^"]+)"', block)
            texture = re.search(r'texturefile\s*=\s*"([^"]+)"', block)
            self.assertIsNotNone(name)
            self.assertIsNotNone(texture)
            self.assertNotIn(name.group(1), definitions)
            definitions[name.group(1)] = texture.group(1)
        self.assertEqual(definitions, {asset['sprite']: asset['texture'] for asset in self.assets})

    def test_balance_sides_use_their_dedicated_sprites(self):
        text = BOP_PATH.read_text(encoding='utf-8')
        self.assertIn('icon = GFX_sr_union_collapse', text)
        self.assertIn('icon = GFX_sr_union_preservation', text)
        self.assertNotIn('GFX_goal_generic_national_unity', text)

    def test_all_dds_files_are_unique_95_by_85_dxt5_textures(self):
        hashes = set()
        for asset in self.assets:
            path = MOD/asset['texture']
            data = path.read_bytes()
            with self.subTest(texture=asset['texture']):
                self.assertEqual(data[:4], b'DDS ')
                self.assertEqual(struct.unpack_from('<I', data, 12)[0], 85)
                self.assertEqual(struct.unpack_from('<I', data, 16)[0], 95)
                self.assertEqual(data[84:88], b'DXT5')
            hashes.add(hashlib.sha256(data).digest())
        self.assertEqual(len(hashes), 80)

    def test_custom_lito_portrait_is_bound_to_a_156_by_210_dds(self):
        gfx = (MOD/'interface/sr_custom_portraits.gfx').read_text(encoding='utf-8')
        self.assertIn('name = "GFX_sr_lito_portrait"', gfx)
        path = re.search(r'texturefile\s*=\s*"([^"]+)"', gfx).group(1)
        data = (MOD/path).read_bytes()
        self.assertEqual(data[:4], b'DDS ')
        self.assertEqual(struct.unpack_from('<II', data, 12), (210, 156))
        self.assertEqual(data[84:88], b'DXT5')


if __name__ == '__main__':
    unittest.main(verbosity=2)
