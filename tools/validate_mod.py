"""Static mod integration checks; this is not an HOI4 engine or schema validator."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'soviet_renewal'
REPUBLICS = (
    'russia', 'ukraine', 'belarus', 'georgia', 'armenia', 'azerbaijan',
    'kazakhstan', 'uzbekistan', 'turkmenistan', 'kyrgyzstan', 'tajikistan',
    'estonia', 'latvia', 'lithuania', 'moldavia',
)
TOKEN = re.compile(r'\s+|\#[^\r\n]*|"(?:\\.|[^"\\])*"|!=|<=|>=|[{}=<>!]|[^\s{}=<>!"#]+')


def parse(text):
    tokens = []
    end = 0
    for match in TOKEN.finditer(text):
        assert match.start() == end, f'Invalid token near {text[end:end+40]!r}'
        end = match.end()
        value = match[0]
        if not value.isspace() and not value.startswith('#'):
            tokens.append(value)
    assert end == len(text), 'Unparsed input (possibly unclosed string)'
    index = 0

    def block(nested=False):
        nonlocal index
        result = []
        while index < len(tokens):
            key = tokens[index]
            index += 1
            if key == '}':
                assert nested, 'Unexpected closing brace'
                return result
            assert key not in ('{', '=', '<', '>', '<=', '>='), f'Unexpected token {key}'
            if index < len(tokens) and tokens[index] in ('=', '<', '>', '<=', '>=', '!='):
                op = tokens[index]
                index += 1
                assert index < len(tokens), 'Missing value'
                value = tokens[index]
                index += 1
                if value == '{':
                    value = block(True)
                else:
                    assert value != '}', 'Missing value before closing brace'
                result.append((key, op, value))
            else:
                result.append((key, None, None))
        assert not nested, 'Unclosed block'
        return result

    return block()


def values(nodes, key):
    return [value for name, op, value in nodes if name == key]


def one(nodes, key):
    found = values(nodes, key)
    assert len(found) == 1, f'Expected one {key}, got {len(found)}'
    return found[0]


def walk(nodes):
    for key, op, value in nodes:
        yield key, op, value
        if isinstance(value, list):
            yield from walk(value)


def check():
    scripts = {}
    for path in sorted(MOD.rglob('*.txt')):
        try:
            scripts[path.relative_to(MOD).as_posix()] = parse(path.read_text(encoding='utf-8-sig'))
        except AssertionError as exc:
            raise AssertionError(f'{path}: {exc}') from exc
    tree = one(scripts['common/national_focus/sr_soviet.txt'], 'focus_tree')
    focuses = values(tree, 'focus')
    ids = [one(focus, 'id') for focus in focuses]
    assert len(ids) == 102 and len(set(ids)) == 102
    for focus in focuses:
        node = one(focus, 'id')
        for prerequisite in values(focus, 'prerequisite'):
            for reference in values(prerequisite, 'focus'):
                assert reference in ids, f'Unknown focus {reference}'
                assert ids.index(reference) < ids.index(node), f'Cyclic dependency {reference} -> {node}'
    assert one(tree, 'default') == 'no'
    assert ('tag', '=', 'SOV') in list(walk(one(tree, 'country')))

    ideas = set()
    for path, nodes in scripts.items():
        if path.startswith('common/ideas/'):
            ideas.update(key for key, _, _ in one(one(nodes, 'ideas'), 'country'))
    for nodes in scripts.values():
        for key, _, value in walk(nodes):
            if key in ('add_ideas', 'remove_ideas') and isinstance(value, str) and value.startswith('sr_'):
                assert value in ideas, f'Unknown idea {value}'
            if key == 'add_timed_idea':
                idea = one(value, 'idea')
                assert idea in ideas, f'Unknown timed idea {idea}'
                durations = [float(number) for unit in ('days', 'months', 'years') for number in values(value, unit)]
                assert len(durations) == 1 and durations[0] > 0, f'Invalid duration for {idea}'

    character = one(scripts['common/characters/sr_lito.txt'], 'characters')
    leader = one(character, 'SOV_cosif_kozs_lito')
    assert one(one(leader, 'country_leader'), 'ideology') == 'titoism'
    assert one(one(one(leader, 'portraits'), 'civilian'), 'large') == 'GFX_sr_lito_portrait'
    startup = one(scripts['common/on_actions/sr_lito_on_actions.txt'], 'on_actions')
    monthly = one(one(startup, 'on_monthly'), 'effect')
    assert ('tag', '=', 'SOV') in list(walk(monthly)), 'Monthly effect must execute only for SOV'
    assert not values(monthly, 'SOV'), 'on_monthly must not be repeated for every country'
    assert ('ideology', '=', 'titoism') in list(walk(one(startup, 'on_startup')))

    bop = one(scripts['common/bop/sr_union_balance.txt'], 'sr_union_balance')
    side_ids = {one(side, 'id') for side in values(bop, 'side')}
    assert one(bop, 'left_side') == 'sr_union_collapse_side'
    assert one(bop, 'right_side') == 'sr_union_preservation_side'
    assert side_ids == {'sr_union_collapse_side', 'sr_union_preservation_side'}
    ranges = values(bop, 'range') + [r for side in values(bop, 'side') for r in values(side, 'range')]
    intervals = sorted((float(one(r, 'min')), float(one(r, 'max'))) for r in ranges)
    assert intervals[0][0] == -1 and intervals[-1][1] == 1
    for index, (lo, hi) in enumerate(intervals):
        assert lo < hi
        if index:
            assert intervals[index-1][1] == lo, 'BoP ranges have a gap or overlap'
    required_loc = set(ids) | ideas | side_ids | {one(r, 'id') for r in ranges}
    required_loc.update(('SOV_cosif_kozs_lito', 'SOV_cosif_kozs_lito_desc', 'titoism', 'titoism_desc', 'sr_union_balance', 'sr_union_council', 'sr_yugoslav_friendship'))
    required_loc.update(key+'_desc' for key in set(ids) | ideas)
    for path, nodes in scripts.items():
        if path.startswith('common/characters/'):
            for character_id, _, body in one(nodes, 'characters'):
                required_loc.add(one(body, 'name').strip('"'))
                for role in values(body, 'country_leader'):
                    required_loc.add(one(role, 'desc').strip('"'))
    events = {}
    for path, nodes in scripts.items():
        if path.startswith('events/'):
            namespaces = set(values(nodes, 'add_namespace'))
            for event in values(nodes, 'country_event'):
                event_id = one(event, 'id')
                assert event_id not in events, f'Duplicate event {event_id}'
                assert event_id.split('.')[0] in namespaces, f'Undeclared event namespace: {event_id}'
                events[event_id] = event
                for field in ('title', 'desc'):
                    for value in values(event, field):
                        required_loc.add(one(value, 'text') if isinstance(value, list) else value)
                for option in values(event, 'option'):
                    required_loc.add(one(option, 'name'))
                assert values(event, 'option'), f'No option in visible event {event_id}'
    for nodes in scripts.values():
        for key, _, value in walk(nodes):
            if key == 'country_event':
                # A list without id is a top-level event block already checked above.
                event_id = one(value, 'id') if isinstance(value, list) else value
                assert event_id in events, f'Undefined event reference: {event_id}'
    triggers = scripts['common/scripted_triggers/sr_union_triggers.txt']
    decisions = one(scripts['common/decisions/sr_union_decisions.txt'], 'sr_union_council')
    effects = scripts['common/scripted_effects/sr_union_effects.txt']
    effects_text = (MOD / 'common/scripted_effects/sr_union_effects.txt').read_text()
    for republic in REPUBLICS:
        trigger = f'sr_union_{republic}_represented'
        assert len(values(triggers, trigger)) == 1, f'Missing republic {republic}'
        decision_id = f'sr_union_consult_{republic}'
        decision = one(decisions, decision_id)
        assert float(one(decision, 'cost')) > 0
        assert int(one(decision, 'days_re_enable')) >= 180
        assert (trigger, '=', 'yes') in list(walk(one(decision, 'visible')))
        assert trigger in effects_text, f'No monthly influence for {republic}'
    for decision_id, _, decision in decisions:
        required_loc.update((decision_id, decision_id+'_desc'))
    defined_effects = {
        key for path, nodes in scripts.items() if path.startswith('common/scripted_effects/')
        for key, _, _ in nodes
    }
    defined_triggers = {
        key for path, nodes in scripts.items() if path.startswith('common/scripted_triggers/')
        for key, _, _ in nodes
    }
    for path, nodes in scripts.items():
        if path.startswith('common/decisions/'):
            for category_id, _, category in nodes:
                required_loc.add(category_id)
                if '/categories/' not in path:
                    for decision_id, _, decision in category:
                        required_loc.update((decision_id, decision_id+'_desc'))
    for nodes in scripts.values():
        for key, _, value in walk(nodes):
            if key == 'set_cosmetic_tag' and isinstance(value, str):
                required_loc.update((value, value+'_DEF', value+'_ADJ', value+'_communism', value+'_communism_DEF', value+'_communism_ADJ'))
    for nodes in scripts.values():
        for key, _, value in walk(nodes):
            if key.startswith('sr_') and isinstance(value, str) and value in ('yes', 'no'):
                assert key in defined_effects | defined_triggers, f'Unknown scripted effect/trigger {key}'
            if key in ('custom_effect_tooltip', 'tooltip') and isinstance(value, str) and value.startswith('sr_'):
                required_loc.add(value)
    all_keys = []
    for language in ('german', 'english'):
        keys = []
        for path in sorted((MOD / f'localisation/{language}').glob('*.yml')):
            assert path.read_bytes().startswith(b'\xef\xbb\xbf'), f'Missing UTF-8 BOM: {path}'
            text = path.read_text(encoding='utf-8-sig')
            assert text.startswith(f'l_{language}:\n')
            for line in text.splitlines()[1:]:
                assert re.fullmatch(r' [A-Za-z0-9_.]+:0 "(?:\\.|[^"\\])*"', line), f'Invalid localization: {path}: {line}'
            keys.extend(re.findall(r'^ ([A-Za-z0-9_.]+):0 ', text, re.M))
        assert len(keys) == len(set(keys)), f'Duplicate localization in {language}'
        assert required_loc <= set(keys), f'Missing {language} localization: {required_loc-set(keys)}'
        all_keys.append(set(keys))
    assert all_keys[0] == all_keys[1], 'Languages have different keys'
    for path in (ROOT/'soviet_renewal.mod', MOD/'descriptor.mod'):
        assert 'replace_path' not in path.read_text()
    installer = ROOT/'tools/install_lito.ps1'
    assert installer.is_file(), 'Local subtype/portrait preparation helper is required'
    assert 'can_be_randomly_selected = no' in installer.read_text()
    print(f'PASS: {len(scripts)} parsed scripts; {len(ids)} focuses; {len(events)} story events; Lito + Titoism integration; 15 republics; continuous BoP ranges; idea/effect references; German/English localization.')
    print('NOTE: run tools/install_lito.ps1 on a local HOI4 installation to generate the complete ideology file and generic portrait sprite. No engine validation performed.')


if __name__ == '__main__':
    check()
