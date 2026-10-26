"""Create small decision-row DDS files without resizing shared focus/header art."""
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'soviet_renewal'
CUSTOM = (
    'decision_LITO_eastern_europe',
    'focus_LITO_experts_in_camouflage',
    'focus_LITO_the_molotov_line',
)
FOCUS = (
    'sr_lito_congress',
    'sr_lito_constitutional_guarantees',
    'sr_lito_defence_council',
    'sr_lito_federal_plan',
    'sr_lito_local_budgets',
    'sr_lito_local_investment',
    'sr_lito_politics_accountability',
    'sr_lito_politics_central_mandate',
    'sr_lito_politics_council_mandate',
    'sr_lito_ratify_compromise',
    'sr_lito_regional_workshops',
    'sr_lito_republic_congress',
    'sr_lito_supply_corridors',
    'sr_lito_technical_education',
    'sr_lito_union_charter',
)


def build():
    magick = shutil.which('magick')
    if not magick:
        raise SystemExit('ImageMagick (magick) is required to rebuild DDS thumbnails.')
    output = MOD / 'gfx/interface/decisions/icons'
    output.mkdir(parents=True, exist_ok=True)
    for stem in CUSTOM + FOCUS:
        source_folder = 'decisions' if stem in CUSTOM else 'focus_icons'
        source = ROOT / 'artwork' / source_folder / (stem + '.png')
        if not source.is_file():
            fallback_folder = 'decisions' if stem in CUSTOM else 'goals'
            source = MOD / 'gfx/interface' / fallback_folder / (stem + '.dds')
        if not source.is_file():
            raise FileNotFoundError(source)
        # Fit the complete motif; a 2px transparent border keeps it inside the row.
        subprocess.run([
            magick, str(source), '-alpha', 'on', '-background', 'none',
            '-resize', '28x28', '-gravity', 'center', '-extent', '32x32',
            '-define', 'dds:compression=dxt5', '-define', 'dds:mipmaps=0',
            str(output / (stem + '.dds')),
        ], check=True)
    print(f'Built {len(CUSTOM) + len(FOCUS)} transparent 32x32 decision thumbnails.')


if __name__ == '__main__':
    build()
