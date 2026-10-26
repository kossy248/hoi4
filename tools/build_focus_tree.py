"""Render Lito's 102-focus design, localization and review diagram."""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import json
import os
import re
import subprocess
import tempfile
import textwrap

from focus_data import core, civil, military, politics, story, expansion

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT/'soviet_renewal'
VERSION = '0.6.0'
# Native continuous-focus palette uses interface coordinates, not focus rows.
# Keep it below the ordinary tree, whose final focus is on row 15.
CONTINUOUS_FOCUS_POSITION = {'x': 50, 'y': 2500}
BRANCHES = {
    'politics': ('Litos Machtsicherung', '#8956a4'),
    'federation': ('Republiken und Unionsvertrag', '#3b8d82'),
    'economy': ('Wirtschaft und Selbstverwaltung', '#be8540'),
    'research': ('Forschung und Bildung', '#347cab'),
    'army': ('Heer und Landesverteidigung', '#64754c'),
    'air': ('Luftwaffe', '#6599bb'),
    'navy': ('Marine', '#416597'),
    'diplomacy': ('Jugoslawien und Balkanpolitik', '#ac5a65'),
}
BRANCH_COUNTS = {key: (14 if key == 'diplomacy' else 16 if key in ('politics', 'economy', 'army') else 8)
                 for key in BRANCHES}


def requirements(item):
    return [[parent] for parent in item.get('parents', [])] + item.get('parent_groups', [])


def design():
    focuses = deepcopy(core.COMMON)
    ideas, loc, opinions, terminals = deepcopy(core.IDEAS), deepcopy(core.BASE_LOC), deepcopy(core.OPINIONS), {}
    for module in (civil, military, politics, expansion):
        focuses.extend(deepcopy(module.FOCUSES))
        ideas.update(deepcopy(module.IDEAS))
        loc.update(deepcopy(module.LOC))
        opinions.update(deepcopy(getattr(module, 'OPINIONS', {})))
        terminals.update(deepcopy(module.TERMINALS))
    assert Counter(item['branch'] for item in focuses if item['branch'] != 'common') == Counter(BRANCH_COUNTS)

    def groups(*branches):
        return [group for branch in branches for group in terminals[branch]]

    def ending(key, x, row, parents, cost, de, en, de_desc, en_desc, reward, **extra):
        item = dict(id=key, branch='endgame', x=x, row=row, parents=[], parent_groups=parents,
                    cost=cost, de=de, en=en, de_desc=de_desc, en_desc=en_desc, reward=reward)
        item.update(extra)
        focuses.append(item)

    ending('sr_lito_civil_compact', 17, 13, groups('economy', 'research'), 10,
           'Wissen und Wohlstand verbinden', 'Unite Knowledge and Prosperity',
           'Wirtschaft und Forschung bündeln ihre Erfahrungen. Zwei zusätzliche 50-Prozent-Boni für Industrietechnologien unterstützen den weiteren Aufbau.',
           'Economy and research pool their experience. Two additional 50% industrial research bonuses support further development.',
           'add_tech_bonus = { name = sr_lito_civil_compact_bonus bonus = 0.5 uses = 2 category = industry }')
    loc['sr_lito_civil_compact_bonus'] = {'de': 'Föderales Aufbauprogramm', 'en': 'Federal Development Program'}
    ending('sr_lito_federal_resolution', 5, 13, groups('politics', 'federation'), 8,
           'Der Vertrag hält', 'The Charter Holds',
           'Partei und Republiken bestätigen ihre gemeinsame Ordnung. Widerstand jeder vertretenen Republik: −5; zusätzlich 5 Punkte zur Erhaltung.',
           'Party and republics reaffirm their shared order. Resistance in each represented republic: −5; also gain 5 preservation points.',
           'sr_lito_reduce_republic_resistance_effect = yes\nadd_power_balance_value = { id = sr_union_balance value = 0.05 }')
    ending('sr_lito_defence_council', 32, 13, groups('army', 'air', 'navy'), 10,
           'Ein gemeinsamer Verteidigungsrat', 'A Joint Defence Council',
           'Heer, Luftwaffe und Marine stimmen ihre Einsatzplanung ab. Jede Teilstreitkraft erhält 25 Erfahrung.',
           'Army, air force and navy coordinate operational planning. Each service gains 25 experience.',
           'army_experience = 25\nair_experience = 25\nnavy_experience = 25')
    ending('sr_lito_socialist_partnership', 44, 13, groups('diplomacy'), 8,
           'Die Union handelt eigenständig', 'The Union Acts Independently',
           'Der eingeschlagene außenpolitische Kurs wird durch einen gemeinsamen Wissenschafts- und Koordinationsstab unterstützt. Für 730 Tage: +2 % Forschungsgeschwindigkeit.',
           'A joint scientific coordination staff supports our chosen foreign policy. Gain 2% research speed for 730 days.',
           'add_timed_idea = { idea = sr_lito_joint_coordination days = 730 }')
    ideas['sr_lito_joint_coordination'] = dict(de='Gemeinsamer Koordinationsstab', en='Joint Coordination Staff',
        de_desc='Ein zeitlich begrenztes Koordinationsprogramm erhöht die Forschungsgeschwindigkeit um 2 %.',
        en_desc='A temporary coordination program increases research speed by 2%.', modifier='research_speed_factor = 0.02')
    ending('sr_lito_union_future', 23, 15,
           [[key] for key in ('sr_lito_civil_compact', 'sr_lito_federal_resolution', 'sr_lito_defence_council', 'sr_lito_socialist_partnership')], 10,
           'Die Union erhalten', 'Preserve the Union',
           'Litos Regierungsprogramm verbindet föderalen Zusammenhalt, Wirtschaft und gemeinsame Verteidigung. Erhalte 5 Prozentpunkte Stabilität und 10 Punkte zur Erhaltung.',
           'Lito’s program unites federal cohesion, development and common defence. Gain 5 percentage points stability and 10 preservation points.',
           'add_stability = 0.05\nadd_power_balance_value = { id = sr_union_balance value = 0.10 }')
    ending('sr_lito_slavic_consolidation', 43, 15,
           [['sr_lito_socialist_partnership'], ['sr_lito_civil_compact']], 10,
           'Die große Föderation festigen', 'Consolidate the Greater Federation',
           'Nach der Ausrufung der Sozialistischen Föderalen Slawischen Union müssen ihre Institutionen zusammenfinden. Erhalte 5 Prozentpunkte Stabilität und 10 Punkte zur Erhaltung; der Widerstand jeder vertretenen Republik sinkt um 5.',
           'After proclaiming the Socialist Federal Slavic Union, its institutions must work together. Gain 5 percentage points stability and 10 preservation points; resistance in each represented republic falls by 5.',
           'add_stability = 0.05\nadd_power_balance_value = { id = sr_union_balance value = 0.10 }\nsr_lito_reduce_republic_resistance_effect = yes',
           available='has_country_flag = sr_slavic_union_proclaimed')
    story.enrich(focuses)
    # Reuse existing milestones for Vanilla's second/third poster slots.
    # Flags make completion rewards work before the engine marks the focus done.
    for item in focuses:
        for focus_id, milestone, tooltip in (
                ('sr_lito_workers_councils', 'councils', 'sr_lito_native_agitprop_councils_slot_tt'),
                ('sr_lito_academy_network', 'academy', 'sr_lito_native_agitprop_academy_slot_tt')):
            if item['id'] == focus_id:
                item['reward'] += (f'\nset_country_flag = sr_lito_native_agitprop_{milestone}_milestone'
                                   '\nsr_lito_native_agitprop_sync_effect = yes'
                                   f'\ncustom_effect_tooltip = {tooltip}')
                item['de_desc'] += (' Nach „Agitprop der Völker“ wird ein weiterer originaler '
                                    'Agitprop-Posterplatz freigeschaltet.')
                item['en_desc'] += (' After Agitprop of the Peoples, unlock one additional '
                                    'original Agitprop poster slot.')
    assert len(focuses) == 102 and len({item['id'] for item in focuses}) == 102
    for item in focuses:
        if 'x' not in item:
            item['x'] = list(BRANCHES).index(item['branch'])*6 + item['column']*2
        assert item['cost'] in (5, 8, 10)
        for key, language in (('de', 'de'), ('en', 'en')):
            loc.setdefault(item['id'], {})[language] = item[key]
            loc.setdefault(item['id']+'_desc', {})[language] = item[key+'_desc']
    for key, idea in ideas.items():
        loc[key] = {language: idea[language] for language in ('de', 'en')}
        loc[key+'_desc'] = {language: idea[language+'_desc'] for language in ('de', 'en')}
    for key, opinion in opinions.items():
        loc[key] = {language: opinion[language] for language in ('de', 'en')}
    # Emit parents before children, including every member of OR prerequisites.
    result, emitted = [], set()
    while len(result) < len(focuses):
        ready = sorted((f for f in focuses if f['id'] not in emitted and
                        all(parent in emitted for group in requirements(f) for parent in group)),
                       key=lambda f: (f['row'], f['x'], f['id']))
        assert ready, 'Missing reference or cycle in focus design'
        for item in ready:
            result.append(item)
            emitted.add(item['id'])
    return result, ideas, loc, opinions


def indent(text, spaces):
    return textwrap.indent(textwrap.dedent(text).strip(), ' '*spaces)


def build():
    focuses, ideas, loc, opinions = design()
    gfx_plan = json.loads((ROOT/'tools/gfx_plan.json').read_text(encoding='utf-8'))['items']
    assert len(gfx_plan) == 80
    assert len({asset['id'] for asset in gfx_plan}) == 80
    assert len({asset['sprite'] for asset in gfx_plan}) == 80
    focus_assets = {asset['id']: asset for asset in gfx_plan if asset['id'].startswith('sr_lito_')}
    assert set(focus_assets) <= {item['id'] for item in focuses}
    for asset in gfx_plan:
        assert (MOD/asset['texture']).is_file(), f"Missing generated texture: {asset['texture']}"
    for item in focuses:
        source = item.get('icon_source', item['id'])
        assert source in focus_assets, f'Unknown artwork source: {source}'
        item['icon'] = focus_assets[source]['sprite']

    gfx = '# Generated by tools/build_focus_tree.py from tools/gfx_plan.json.\nspriteTypes = {\n'
    for asset in gfx_plan:
        gfx += (f'    spriteType = {{\n'
                f'        name = "{asset["sprite"]}"\n'
                f'        texturefile = "{asset["texture"]}"\n'
                f'    }}\n')
    gfx += '}\n'
    interface = MOD/'interface'
    interface.mkdir(parents=True, exist_ok=True)
    (interface/'sr_focus_icons.gfx').write_text(gfx, encoding='utf-8')

    chapter_art = {
        'council': ('sr_domestic_story.txt', 'sr_campaign_domestic.txt'),
        'workshops': ('sr_focus_story.txt', 'sr_campaign_projects.txt'),
        'balkan': ('sr_balkan_story.txt', 'sr_campaign_balkan.txt'),
    }
    chapter_gfx = '# Generated chapter illustrations, shared by related events.\nspriteTypes = {\n'
    for theme, filenames in chapter_art.items():
        texture = f'gfx/event_pictures/sr_campaign_{theme}.dds'
        assert (MOD/texture).is_file(), f'Missing event artwork: {texture}'
        chapter_gfx += f'    spriteType = {{\n        name = "GFX_sr_campaign_{theme}"\n        texturefile = "{texture}"\n    }}\n'
        for filename in filenames:
            path = MOD/'events'/filename
            original = path.read_text(encoding='utf-8-sig')
            rendered = re.sub(r'(?m)^(country_event\s*=\s*\{\n)(?:[ \t]*picture\s*=\s*GFX_sr_campaign_\w+\n)?',
                              lambda match: match.group(1) + f'    picture = GFX_sr_campaign_{theme}\n', original)
            if rendered != original:
                path.write_text(rendered, encoding='utf-8')
    (interface/'sr_campaign_event_pictures.gfx').write_text(chapter_gfx + '}\n', encoding='utf-8')

    text = '# Generated by tools/build_focus_tree.py; edit tools/focus_data instead.\nfocus_tree = {\n    id = sr_soviet_tree\n    country = {\n        factor = 0\n        modifier = { add = 100 tag = SOV }\n    }\n    default = no\n'
    text += ('    # Separate the native continuous-focus panel from ordinary focus icons.\n'
             '    continuous_focus_position = { '
             f'x = {CONTINUOUS_FOCUS_POSITION["x"]} y = {CONTINUOUS_FOCUS_POSITION["y"]}'
             ' }\n')
    for item in focuses:
        text += f'    focus = {{\n        id = {item["id"]}\n        icon = {item["icon"]}\n        x = {item["x"]}\n        y = {item["row"]}\n        cost = {item["cost"]}\n'
        for group in requirements(item):
            text += '        prerequisite = { ' + ' '.join('focus = '+key for key in group) + ' }\n'
        if item.get('exclusive'):
            text += '        mutually_exclusive = { ' + ' '.join('focus = '+key for key in item['exclusive']) + ' }\n'
        for block in ('available', 'bypass'):
            if item.get(block):
                text += f'        {block} = {{\n' + indent(item[block], 12) + '\n        }\n'
        text += '        completion_reward = {\n' + indent(item['reward'], 12) + '\n        }\n    }\n'
    (MOD/'common/national_focus/sr_soviet.txt').write_text(text+'}\n')
    text = '# Generated by tools/build_focus_tree.py\nideas = {\n    country = {\n'
    for key, idea in sorted(ideas.items()):
        text += f'        {key} = {{\n            picture = generic_industry\n            allowed = {{ always = yes }}\n            removal_cost = -1\n            modifier = {{\n' + indent(idea['modifier'], 16) + '\n            }\n        }\n'
    (MOD/'common/ideas/sr_ideas.txt').write_text(text+'    }\n}\n')
    text = 'opinion_modifiers = {\n'
    for key, opinion in sorted(opinions.items()):
        text += f'    {key} = {{ value = {opinion["value"]} }}\n'
    (MOD/'common/opinion_modifiers/sr_lito_opinions.txt').write_text(text+'}\n')
    for language, short in (('german', 'de'), ('english', 'en')):
        def escape(value):
            return value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        text = f'l_{language}:\n' + ''.join(f' {key}:0 "{escape(value[short])}"\n' for key, value in sorted(loc.items()))
        (MOD/f'localisation/{language}/sr_l_{language}.yml').write_text(text, encoding='utf-8-sig')
    effect = '# Generated federal focus recovery; never affects foreign/inactive republics.\nsr_lito_reduce_republic_resistance_effect = {\n'
    republics = ('russia','ukraine','belarus','georgia','armenia','azerbaijan','kazakhstan','uzbekistan','turkmenistan','kyrgyzstan','tajikistan','estonia','latvia','lithuania','moldavia')
    for republic in republics:
        effect += f'    if = {{\n        limit = {{ sr_union_{republic}_represented = yes }}\n        subtract_from_variable = {{ sr_resistance_{republic} = 5 }}\n        clamp_variable = {{ var = sr_resistance_{republic} min = 0 max = 100 }}\n    }}\n'
    effect += '    sr_update_union_resistance_ideas_effect = yes\n}\n'
    (MOD/'common/scripted_effects/sr_lito_focus_effects.txt').write_text(effect)
    manifest = dict(focus_count=len(focuses), branches={key: {'title': title, 'count': BRANCH_COUNTS[key]} for key, (title, color) in BRANCHES.items()}, focuses=focuses)
    (ROOT/'docs/focus_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    docs = f'# Litos Fokusbaum — {len(focuses)} Schwerpunkte\n\nZwei Einstiege, Politik, Wirtschaft und Heer mit je sechzehn Schwerpunkten,\nvier weitere Zweige mit je acht, Balkanpolitik mit vierzehn und sechs\nAbschlussziele. Laufzeiten: 35, 56 oder 70 Tage. Die 24 späteren Schwerpunkte\nvertiefen die Institutionen, Industriegesellschaft und Militärpolitik von Litos\nZeitlinie. Sechs davon lösen zusätzliche erzählerische Entscheidungen aus.\nGestrichelte rote Verbindungen markieren gegenseitige Ausschlüsse. Alternative\nVoraussetzungen sind als ODER-Gruppen angegeben. Die Ausrufung der Slawischen\nUnion bleibt eine eigenständige Entscheidung.\n\n'
    docs += ('Das native Fenster „Fortgesetzte Schwerpunkte“ liegt mit Abstand unter\n'
             'der letzten regulären Fokusreihe. Seine Oberflächenposition wird im\n'
             'Generator über `continuous_focus_position` festgelegt; die Werte sind\n'
             'keine Fokuszeilen. Die Darstellung muss noch im Spiel geprüft werden.\n\n')
    for branch, title in [('common','Gemeinsamer Einstieg')] + [(key, val[0]) for key, val in BRANCHES.items()] + [('endgame','Abschlussziele')]:
        docs += f'## {title}\n\n| Schwerpunkt | Tage | Voraussetzungen |\n| --- | ---: | --- |\n'
        for item in focuses:
            if item['branch'] != branch:
                continue
            labels = {f['id']: f['de'] for f in focuses}
            parents = ' UND '.join('('+' ODER '.join(labels[parent] for parent in group)+')' for group in requirements(item)) or '—'
            docs += f'| {item["de"]} | {item["cost"]*7} | {parents} |\n'
        docs += '\n'
    docs += f'## Prüfung\n\nSkripte und Abhängigkeiten sind automatisiert prüfbar; ein HOI4-Spieltest steht aus.\nDie {len(focuses)} Schwerpunkte verwenden die vorhandene Bibliothek aus 78 eigenen\nrot-goldenen DDS-Symbolen. Die 24 neuen Schwerpunkte verwenden ausdrücklich\nzugeordnete Motive dieser Bibliothek erneut. Übersicht: [Fokusbaum als SVG](focus_tree.svg).\n'
    (ROOT/'docs/FOKUSBAUM.md').write_text(docs)
    dot = ['digraph Lito {', 'graph [rankdir=TB bgcolor="#101924" pad="0.4" nodesep="0.22" ranksep="0.65" splines=polyline];', 'node [shape=box style="rounded,filled" color="#a3b2c1" fillcolor="#243345" fontcolor="white" fontname="DejaVu Sans" fontsize=11 margin="0.12,0.08"];', 'edge [color="#8fa3b6" arrowsize=0.6];']
    for item in focuses:
        label = '\n'.join(textwrap.wrap(item['de'], 24)) + f'\n{item["cost"]*7} Tage'
        color = BRANCHES.get(item['branch'], ('','#596775'))[1]
        dot.append(f'"{item["id"]}" [label={json.dumps(label,ensure_ascii=False)} fillcolor="{color}"];')
        for group in requirements(item):
            for parent in group:
                attributes = ' [style=dotted label="ODER"]' if len(group)>1 else ''
                dot.append(f'"{parent}" -> "{item["id"]}"{attributes};')
        for other in item.get('exclusive', []):
            if item['id'] < other:
                dot.append(f'"{item["id"]}" -> "{other}" [dir=none style=dashed color="#f18e90" constraint=false label="Wahl"];')
    dot.append('}')
    dot_path = ROOT/'docs/focus_tree.dot'
    dot_path.write_text('\n'.join(dot)+'\n')
    cache = Path(tempfile.gettempdir())/'lito-font-cache'
    cache.mkdir(exist_ok=True)
    subprocess.run(['dot', '-Tsvg', str(dot_path), '-o', str(ROOT/'docs/focus_tree.svg')],
                   env={**os.environ, 'XDG_CACHE_HOME': str(cache)}, check=True)
    for path in (ROOT/'soviet_renewal.mod', MOD/'descriptor.mod'):
        path.write_text(re.sub(r'(?m)^version="[^"]+"$', f'version="{VERSION}"', path.read_text()))
    print(f'Built {len(focuses)} focuses, {len(ideas)} idea definitions, {len(loc)} localized keys per language and SVG review diagram.')


if __name__ == '__main__':
    build()
