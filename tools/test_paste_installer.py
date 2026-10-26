"""Execute the actual pasteable updater against a synthetic, offline game install."""
from pathlib import Path
import argparse
import base64
import hashlib
import os
import shutil
import struct
import subprocess
import tempfile

from build_paste_installer import ROOT, build


def quote(value):
    return "'" + str(value).replace("'", "''") + "'"


def snapshot(root):
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob('*') if path.is_file()
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pwsh', default=shutil.which('pwsh'))
    args = parser.parse_args()
    if not args.pwsh:
        parser.error('PowerShell 7 is required; pass --pwsh with its executable path.')
    wrapper, files = build()
    with tempfile.TemporaryDirectory(prefix='lito-paste-test-') as temp:
        test_root = Path(temp)
        game = test_root/'game'
        mods = test_root/'mods'
        for folder in ('common/ideologies', 'gfx/leaders/Europe', 'gfx/flags/medium', 'gfx/flags/small'):
            (game/folder).mkdir(parents=True)
        original = '''# String and comment braces must be preserved: } {
ideologies = {
    communism = { types = { stalinism = { } } color = { 1 2 3 } }
    democratic = { types = { liberalism = { } } }
    neutrality = { types = { despotism = { } } }
    fascism = { types = { fascism = { } } }
}
'''
        (game/'common/ideologies/00_ideologies.txt').write_text(original, encoding='utf-8-sig')
        (game/'gfx/leaders/Europe/Portrait_Europe_Generic_1.dds').write_bytes(b'test portrait: not an engine asset')
        for folder in ('gfx/flags', 'gfx/flags/medium', 'gfx/flags/small'):
            (game/folder/'SOV.tga').write_bytes(b'test flag: not an engine asset')
            (game/folder/'YUG.tga').write_bytes(b'test Yugoslav flag: not an engine asset')
        old = mods/'soviet_renewal'
        old.mkdir(parents=True)
        (old/'old-user-file.txt').write_text('preserve me')
        (mods/'soviet_renewal.mod').write_text('old external descriptor')
        game_before = snapshot(game)
        source = wrapper.read_text()
        source = source.replace("$litoGamePath = ''", '$litoGamePath = ' + quote(game), 1)
        source = source.replace("$litoModDirectory = ''", '$litoModDirectory = ' + quote(mods), 1)
        test_script = test_root/'paste.ps1'
        test_script.write_text(source)
        run_env = os.environ.copy()
        if os.name != 'nt':
            for name, directory in (('XDG_CACHE_HOME', 'cache'), ('XDG_CONFIG_HOME', 'config'), ('XDG_DATA_HOME', 'data')):
                run_env[name] = str(test_root/directory)

        def execute():
            return subprocess.run([args.pwsh, '-NoLogo', '-NoProfile', '-File', str(test_script)],
                                  capture_output=True, text=True, env=run_env, timeout=60)

        completed = execute()
        assert completed.returncode == 0, completed.stdout + completed.stderr
        for relative, content in files.items():
            if relative.startswith('soviet_renewal/'):
                installed = mods/relative
                expected = (content.encode('utf-8') if isinstance(content, str)
                            else base64.b64decode(content['base64']))
                assert installed.read_bytes() == expected, f'Payload changed: {relative}'
        ideology = (old/'common/ideologies/00_ideologies.txt').read_text(encoding='utf-8-sig')
        assert 'titoism = { can_be_randomly_selected = no }' in ideology
        for group in ('democratic', 'neutrality', 'fascism', 'stalinism'):
            assert group in ideology
        assert (old/'interface/sr_lito_portrait.gfx').is_file()
        assert 'GFX_sr_balkan_council_portrait' in (old/'interface/sr_lito_portrait.gfx').read_text()
        for folder, dimensions in (('gfx/flags', (82, 52)),
                                   ('gfx/flags/medium', (41, 26)),
                                   ('gfx/flags/small', (10, 7))):
            formable_flags = []
            for flag in ('SOV_LITO_SFSU.tga', 'SOV_LITO_SFSU_communism.tga'):
                supplied = (ROOT/'soviet_renewal'/folder/flag).read_bytes()
                assert (old/folder/flag).read_bytes() == supplied, f'Custom formable flag replaced: {folder}/{flag}'
                assert supplied[1:3] == b'\x00\x02', f'Expected an uncompressed true-color TGA: {folder}/{flag}'
                assert struct.unpack_from('<HH', supplied, 12) == dimensions
                assert supplied[16] == 24 and supplied[17] & 0x0F == 0, 'Flag must be RGB without alpha'
                formable_flags.append(supplied)
            assert formable_flags[0] == formable_flags[1], 'Base and communist formable flags must match'
            assert not (old/folder/'SOV.tga').exists(), 'The normal Soviet flag must not be overridden'
            for flag in ('YUG_LITO_BALKAN.tga', 'YUG_LITO_BALKAN_communism.tga'):
                assert (old/folder/flag).read_bytes() == b'test Yugoslav flag: not an engine asset'
        backups = list(mods.glob('soviet_renewal.backup-*'))
        assert len(backups) == 1 and (backups[0]/'old-user-file.txt').read_text() == 'preserve me'
        assert len(list(mods.glob('soviet_renewal.mod.backup-*'))) == 1
        assert snapshot(game) == game_before, 'Game installation was modified'
        print('PASS: complete pasted updater executes, exact mod bytes/BOM, full ideology groups, portrait, flags, old-mod backup, unchanged game')

        installed_before = snapshot(mods)
        # A single changed payload character must fail the checksum before any install.
        marker = "$litoPayload = @'\n"
        payload_start = source.index(marker) + len(marker)
        source = source[:payload_start] + ('A' if source[payload_start] != 'A' else 'B') + source[payload_start+1:]
        test_script.write_text(source)
        corrupted = execute()
        assert corrupted.returncode != 0, 'Corrupt payload was accepted'
        assert snapshot(mods) == installed_before
        assert snapshot(game) == game_before
        print('PASS: corrupted copied payload is rejected before changing the mod or game')
    print('2 paste-installer integration scenarios passed. Synthetic files only; no HOI4 engine test.')


if __name__ == '__main__':
    main()
