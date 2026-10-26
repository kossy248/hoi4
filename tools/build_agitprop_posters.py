"""Prepare supplied poster art without enabling the unfinished native system."""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import subprocess


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'artwork/agitprop/manifest.json'


def build():
    magick = shutil.which('magick')
    if not magick:
        raise SystemExit('ImageMagick (magick) is required to prepare DDS posters.')
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    width, height = manifest['texture_size']
    slots = set()
    for poster in manifest['posters']:
        slot = poster['slot']
        if slot in slots:
            raise ValueError(f'Duplicate poster slot: {slot}')
        slots.add(slot)
        source = (ROOT / poster['source']).resolve()
        target = (ROOT / poster['texture']).resolve()
        if not source.is_relative_to(ROOT / 'artwork/agitprop/originals'):
            raise ValueError(f'Unexpected poster source: {source}')
        expected = ROOT / 'soviet_renewal/gfx/interface/agitprop' / f'sr_agitprop_{slot}.dds'
        if target != expected:
            raise ValueError(f'Unexpected poster target: {target}')
        original = source.read_bytes()
        if hashlib.sha256(original).hexdigest() != poster['source_sha256']:
            raise ValueError(f'Poster source checksum changed: {source.name}')
        size = subprocess.check_output([
            magick, 'identify', '-format', '%w %h', str(source),
        ], text=True)
        if [int(value) for value in size.split()] != poster['source_size']:
            raise ValueError(f'Poster source dimensions changed: {source.name}')
        target.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([
            magick, str(source), '-alpha', 'on', '-background', 'none',
            '-resize', f'{width}x{height}', '-gravity', 'center',
            '-extent', f'{width}x{height}',
            '-define', 'dds:compression=dxt5', '-define', 'dds:mipmaps=0',
            str(target),
        ], check=True)
        data = target.read_bytes()
        if (data[:4] != b'DDS ' or struct.unpack_from('<II', data, 12) != (height, width)
                or data[84:88] != b'DXT5'):
            raise ValueError(f'Invalid generated poster texture: {target.name}')
        if source.read_bytes() != original:
            raise AssertionError(f'Original poster was changed: {source.name}')
        print(f'Prepared {slot}: {width}x{height} DXT5, full poster fitted without cropping.')
    print('Native Agitprop integration remains pending; no category or GUI was enabled.')


if __name__ == '__main__':
    build()
