"""Civilian branches for Lito's expanded tree; imported by the focus generator.

Only data is emitted here. Construction selects an owned, controlled core with
available levels and otherwise grants the explicitly advertised 50 PP fallback.
The sole research slot in these branches belongs to the university focus.
"""


def _focus(key, branch, column, row, parents, cost, de, en, de_desc, en_desc, reward, **extra):
    result = dict(id=key, branch=branch, column=column, row=row, parents=parents,
                  cost=cost, de=de, en=en, de_desc=de_desc, en_desc=en_desc,
                  reward=reward)
    result.update(extra)
    return result


def _construction(building):
    condition = f'''is_controlled_by = ROOT
                    is_core_of = ROOT
                    free_building_slots = {{ building = {building} size > 0 }}'''
    return f'''if = {{
                limit = {{ any_owned_state = {{ {condition} }} }}
                random_owned_state = {{
                    limit = {{ {condition} }}
                    add_building_construction = {{ type = {building} level = 1 instant_build = yes }}
                }}
            }}
            else = {{ add_political_power = 50 }}'''


FOCUSES = [
    # Economy: eight focuses, including the three established identifiers.
    _focus('sr_lito_workers_councils', 'economy', 1, 2, ['sr_lito_congress'], 5,
           'Räte in den Betrieben', 'Councils in the Factories',
           'Arbeiterräte organisieren die Produktion. Fabrikausstoß: +5 %.',
           'Workers’ councils organize production. Factory output: +5%.',
           'add_ideas = sr_workers_councils'),
    _focus('sr_lito_federal_plan', 'economy', 1, 3, ['sr_lito_workers_councils'], 8,
           'Gemeinsam planen, vor Ort entscheiden', 'Plan Together, Decide Locally',
           'Ein gemeinsamer Investitionsrahmen beschleunigt den Bau um 5 % und gewährt zwei 50-Prozent-Forschungsboni für Industrietechnologien.',
           'A common investment framework increases construction speed by 5% and grants two 50% industrial research bonuses.',
           'add_ideas = sr_federal_planning\n            add_tech_bonus = { name = sr_civil_industry_bonus bonus = 0.5 uses = 2 category = industry }'),
    _focus('sr_lito_local_investment', 'economy', 0, 4, ['sr_lito_federal_plan'], 10,
           'Regionale Investitionsfonds', 'Regional Investment Funds',
           'Eine Zivilfabrik entsteht in einem eigenen, kontrollierten Kerngebiet mit freiem Platz. Fehlt geeigneter Bauplatz, erhalten wir stattdessen 50 politische Macht.',
           'Build one civilian factory in an owned, controlled core state with room. If no suitable space exists, gain 50 political power instead.',
           _construction('industrial_complex')),
    _focus('sr_lito_agricultural_cooperatives', 'economy', 2, 4, ['sr_lito_federal_plan'], 8,
           'Landwirtschaftliche Genossenschaften', 'Agricultural Cooperatives',
           'Freiwillige Genossenschaften und verlässliche Lieferverträge entlasten die Versorgung. Konsumgüterfaktor: −2 Prozentpunkte.',
           'Voluntary cooperatives and reliable supply contracts ease provisioning. Consumer goods factor: −2 percentage points.',
           'add_ideas = sr_agricultural_cooperatives'),
    _focus('sr_lito_regional_workshops', 'economy', 0, 5, ['sr_lito_local_investment'], 10,
           'Werkstätten der Republiken', 'Workshops of the Republics',
           'Eine weitere Zivilfabrik entsteht in einem eigenen, kontrollierten Kerngebiet mit freiem Platz. Andernfalls erhalten wir 50 politische Macht.',
           'Build another civilian factory in an owned, controlled core state with room. Otherwise gain 50 political power.',
           _construction('industrial_complex')),
    _focus('sr_lito_supply_corridors', 'economy', 2, 5, ['sr_lito_agricultural_cooperatives'], 8,
           'Versorgungswege der Union', 'Union Supply Routes',
           'Wir bauen eine Infrastrukturstufe in einem eigenen, kontrollierten Kerngebiet aus, sofern dort eine weitere Stufe möglich ist. Andernfalls erhalten wir 50 politische Macht.',
           'Add one infrastructure level in an owned, controlled core state where another level is possible. Otherwise gain 50 political power.',
           _construction('infrastructure')),
    _focus('sr_lito_industrial_union', 'economy', 1, 6, ['sr_lito_regional_workshops', 'sr_lito_supply_corridors'], 10,
           'Eine Industrie für die Union', 'Industry for the Union',
           'Eine Militärfabrik ergänzt unsere föderale Industrie, sofern ein eigenes, kontrolliertes Kerngebiet freien Platz hat. Andernfalls erhalten wir 50 politische Macht.',
           'Add one military factory to federal industry if an owned, controlled core state has room. Otherwise gain 50 political power.',
           _construction('arms_factory')),
    _focus('sr_lito_shared_prosperity', 'economy', 1, 7, ['sr_lito_industrial_union'], 8,
           'Gemeinsamer Wohlstand', 'Shared Prosperity',
           'Sichtbare Ergebnisse festigen das Vertrauen in den neuen Wirtschaftskurs: +3 Prozentpunkte Stabilität und zwei 25-Prozent-Boni für Industrieforschung.',
           'Visible results strengthen confidence in the new economy: +3 percentage points stability and two 25% industrial research bonuses.',
           'add_stability = 0.03\n            add_tech_bonus = { name = sr_civil_industry_bonus bonus = 0.25 uses = 2 category = industry }'),

    # Federation: eight focuses; local budget autonomy and central coordination
    # are a real exclusive choice, then converge through one OR prerequisite.
    _focus('sr_lito_republic_congress', 'federation', 1, 2, ['sr_lito_congress'], 5,
           'Die Republiken anhören', 'Hear the Republics',
           'Ein gemeinsamer Kongress eröffnet die Verhandlungen: +50 politische Macht und 3 Punkte zur Erhaltung der Union.',
           'A common congress opens negotiations: +50 political power and 3 points toward preserving the Union.',
           'add_political_power = 50\n            add_power_balance_value = { id = sr_union_balance value = 0.03 }'),
    _focus('sr_lito_union_charter', 'federation', 1, 3, ['sr_lito_republic_congress'], 8,
           'Ein neuer Unionsvertrag', 'A New Union Charter',
           'Verbindliche Verfahren geben den Republiken eine Stimme. Tägliche politische Macht: +0,10; zusätzlich 5 Punkte zur Erhaltung.',
           'Binding procedures give the republics a voice. Daily political power: +0.10; also gain 5 preservation points.',
           'add_ideas = sr_federal_charter\n            add_power_balance_value = { id = sr_union_balance value = 0.05 }'),
    _focus('sr_lito_local_budgets', 'federation', 0, 4, ['sr_lito_union_charter'], 5,
           'Eigenständige Republikhaushalte', 'Autonomous Republic Budgets',
           'Regionale Haushaltsrechte stärken die Stabilität um 2,5 Prozentpunkte, verlangsamen unionsweite Bauvorhaben jedoch um 2 %. Dieser Kurs schließt zentrale Koordination aus.',
           'Regional budget rights grant 2.5 percentage points stability but slow union-wide construction by 2%. This course excludes central coordination.',
           'add_ideas = sr_local_budgets', exclusive=['sr_lito_central_coordination']),
    _focus('sr_lito_central_coordination', 'federation', 2, 4, ['sr_lito_union_charter'], 5,
           'Zentrale Koordination', 'Central Coordination',
           'Gemeinsame Produktionsvorgaben erhöhen den Fabrikausstoß um 2,5 %, binden aber täglich 0,05 politische Macht. Zusätzlich 3 Punkte zur Erhaltung. Dieser Kurs schließt eigenständige Republikhaushalte aus.',
           'Common production targets increase factory output by 2.5% but cost 0.05 political power daily. Also gain 3 preservation points. This course excludes autonomous republic budgets.',
           'add_ideas = sr_central_coordination\n            add_power_balance_value = { id = sr_union_balance value = 0.03 }',
           exclusive=['sr_lito_local_budgets']),
    _focus('sr_lito_ratify_compromise', 'federation', 1, 5, [], 8,
           'Den föderalen Kompromiss ratifizieren', 'Ratify the Federal Compromise',
           'Nach der Entscheidung über den Wirtschaftskurs bestätigen die Republiken ihre gemeinsame Ordnung. Widerstand jeder vertretenen Republik: −5; dazu 5 Punkte zur Erhaltung.',
           'After choosing an economic framework, the republics ratify their common order. Resistance in each represented republic: −5; also gain 5 preservation points.',
           'sr_lito_reduce_republic_resistance_effect = yes\n            add_power_balance_value = { id = sr_union_balance value = 0.05 }',
           parent_groups=[['sr_lito_local_budgets', 'sr_lito_central_coordination']]),
    _focus('sr_lito_constitutional_guarantees', 'federation', 0, 6, ['sr_lito_ratify_compromise'], 5,
           'Verfassungsrechte absichern', 'Secure Constitutional Rights',
           'Verlässliche Verfahren entschärfen regionale Konflikte. Widerstand jeder vertretenen Republik: −5; Stabilität: +3 Prozentpunkte.',
           'Reliable procedures ease regional conflicts. Resistance in each represented republic: −5; stability: +3 percentage points.',
           'sr_lito_reduce_republic_resistance_effect = yes\n            add_stability = 0.03'),
    _focus('sr_lito_shared_defence', 'federation', 2, 6, ['sr_lito_ratify_compromise'], 5,
           'Gemeinsame Verteidigungspflichten', 'Shared Defence Obligations',
           'Die Republiken koordinieren ihre Verteidigung: +15 Armeeerfahrung und +3 Prozentpunkte Kriegsunterstützung.',
           'The republics coordinate defence: +15 army experience and +3 percentage points war support.',
           'army_experience = 15\n            add_war_support = 0.03'),
    _focus('sr_lito_federal_unity', 'federation', 1, 7, ['sr_lito_constitutional_guarantees', 'sr_lito_shared_defence'], 8,
           'Einheit durch Mitbestimmung', 'Unity Through Participation',
           'Der Unionsvertrag bewährt sich in der Praxis. Widerstand jeder vertretenen Republik: −5; dazu 5 Punkte zur Erhaltung der Union.',
           'The Union Charter proves itself in practice. Resistance in each represented republic: −5; also gain 5 preservation points.',
           'sr_lito_reduce_republic_resistance_effect = yes\n            add_power_balance_value = { id = sr_union_balance value = 0.05 }'),

    # Research: eight focuses and exactly one new research slot.
    _focus('sr_lito_academy_network', 'research', 1, 2, ['sr_lito_congress'], 5,
           'Die Akademien vernetzen', 'Connect the Academies',
           'Ein gemeinsames Forschungsprogramm gewährt einen 50-Prozent-Bonus für Industrietechnologien.',
           'A common research program grants one 50% industrial research bonus.',
           'add_tech_bonus = { name = sr_civil_industry_bonus bonus = 0.5 uses = 1 category = industry }'),
    _focus('sr_lito_polytechnic_institutes', 'research', 0, 3, ['sr_lito_academy_network'], 8,
           'Polytechnische Institute', 'Polytechnic Institutes',
           'Die Verbindung von Lehre und angewandter Forschung erhöht unsere Forschungsgeschwindigkeit um 2,5 %.',
           'Combining teaching with applied science increases research speed by 2.5%.',
           'add_ideas = sr_polytechnic_network'),
    _focus('sr_lito_scientific_standards', 'research', 2, 3, ['sr_lito_academy_network'], 5,
           'Gemeinsame technische Standards', 'Common Technical Standards',
           'Einheitliche Verfahren erleichtern den Technologietransfer. Ein 50-Prozent-Forschungsbonus für Industrietechnologien.',
           'Common procedures ease technology transfer. Gain one 50% industrial research bonus.',
           'add_tech_bonus = { name = sr_civil_industry_bonus bonus = 0.5 uses = 1 category = industry }'),
    _focus('sr_lito_electronics_laboratories', 'research', 0, 4, ['sr_lito_polytechnic_institutes'], 8,
           'Labore für Elektronik', 'Electronics Laboratories',
           'Neue Laborplätze gewähren einen 50-Prozent-Forschungsbonus für Elektronik.',
           'New laboratory facilities grant one 50% electronics research bonus.',
           'add_tech_bonus = { name = sr_civil_electronics_bonus bonus = 0.5 uses = 1 category = electronics }'),
    _focus('sr_lito_research_exchange', 'research', 2, 4, ['sr_lito_scientific_standards'], 5,
           'Forscher zwischen den Republiken', 'Researchers Across the Republics',
           'Austauschprogramme erhöhen die Forschungsgeschwindigkeit um weitere 2,5 %.',
           'Exchange programs increase research speed by a further 2.5%.',
           'add_ideas = sr_scientific_exchange'),
    _focus('sr_lito_technical_education', 'research', 1, 5, ['sr_lito_electronics_laboratories', 'sr_lito_research_exchange'], 5,
           'Technische Bildung verbreiten', 'Expand Technical Education',
           'Breitere Bildung stützt den föderalen Gesellschaftsvertrag: +3 Prozentpunkte Stabilität und +50 politische Macht.',
           'Broader education supports the federal social contract: +3 percentage points stability and +50 political power.',
           'add_stability = 0.03\n            add_political_power = 50'),
    _focus('sr_lito_federal_universities', 'research', 1, 6, ['sr_lito_technical_education'], 10,
           'Föderale Forschungsuniversitäten', 'Federal Research Universities',
           'Das ausgebaute Hochschulnetz schafft einen zusätzlichen Forschungsplatz.',
           'The expanded university network creates one additional research slot.',
           'add_research_slot = 1'),
    _focus('sr_lito_knowledge_for_all', 'research', 1, 7, ['sr_lito_federal_universities'], 8,
           'Wissen für die Zukunft', 'Knowledge for the Future',
           'Das gemeinsame Wissen beschleunigt die nächste Technikgeneration: zwei 50-Prozent-Forschungsboni für Elektronik.',
           'Shared knowledge accelerates the next generation of technology: two 50% electronics research bonuses.',
           'add_tech_bonus = { name = sr_civil_electronics_bonus bonus = 0.5 uses = 2 category = electronics }'),
]


IDEAS = {
    'sr_workers_councils': {
        'de': 'Arbeiterselbstverwaltung', 'en': 'Workers’ Self-Management',
        'de_desc': 'Die Arbeiterräte koordinieren den Betrieb. Fabrikausstoß: +5 %.',
        'en_desc': 'Workers’ councils coordinate factory operations. Factory output: +5%.',
        'modifier': 'industrial_capacity_factory = 0.05',
    },
    'sr_federal_planning': {
        'de': 'Föderale Investitionsplanung', 'en': 'Federal Investment Planning',
        'de_desc': 'Gemeinsame Investitionen erhöhen die Baugeschwindigkeit um 5 %.',
        'en_desc': 'Joint investment increases construction speed by 5%.',
        'modifier': 'production_speed_buildings_factor = 0.05',
    },
    'sr_agricultural_cooperatives': {
        'de': 'Landwirtschaftliche Genossenschaften', 'en': 'Agricultural Cooperatives',
        'de_desc': 'Verlässliche Lieferungen senken den Konsumgüterfaktor um 2 Prozentpunkte.',
        'en_desc': 'Reliable deliveries reduce the consumer goods factor by 2 percentage points.',
        'modifier': 'consumer_goods_factor = -0.02',
    },
    'sr_federal_charter': {
        'de': 'Föderaler Unionsvertrag', 'en': 'Federal Union Charter',
        'de_desc': 'Verbindliche Verfahren erleichtern die Zusammenarbeit. Tägliche politische Macht: +0,10.',
        'en_desc': 'Binding procedures facilitate cooperation. Daily political power: +0.10.',
        'modifier': 'political_power_gain = 0.10',
    },
    'sr_local_budgets': {
        'de': 'Eigenständige Republikhaushalte', 'en': 'Autonomous Republic Budgets',
        'de_desc': 'Stabilität: +2,5 Prozentpunkte. Baugeschwindigkeit: −2 %.',
        'en_desc': 'Stability: +2.5 percentage points. Construction speed: −2%.',
        'modifier': 'stability_factor = 0.025\n                production_speed_buildings_factor = -0.02',
    },
    'sr_central_coordination': {
        'de': 'Zentrale Koordination', 'en': 'Central Coordination',
        'de_desc': 'Fabrikausstoß: +2,5 %. Tägliche politische Macht: −0,05.',
        'en_desc': 'Factory output: +2.5%. Daily political power: −0.05.',
        'modifier': 'industrial_capacity_factory = 0.025\n                political_power_gain = -0.05',
    },
    'sr_polytechnic_network': {
        'de': 'Polytechnisches Netzwerk', 'en': 'Polytechnic Network',
        'de_desc': 'Forschungsgeschwindigkeit: +2,5 %.',
        'en_desc': 'Research speed: +2.5%.',
        'modifier': 'research_speed_factor = 0.025',
    },
    'sr_scientific_exchange': {
        'de': 'Föderaler Forscheraustausch', 'en': 'Federal Researcher Exchange',
        'de_desc': 'Forschungsgeschwindigkeit: +2,5 %.',
        'en_desc': 'Research speed: +2.5%.',
        'modifier': 'research_speed_factor = 0.025',
    },
}

LOC = {
    'sr_civil_industry_bonus': {'de': 'Föderale Industrieforschung', 'en': 'Federal Industrial Research'},
    'sr_civil_electronics_bonus': {'de': 'Föderale Elektronikforschung', 'en': 'Federal Electronics Research'},
}

# Named research bonuses remain unique so completing a later focus cannot replace
# an earlier, unused research reward with the same internal name.
for _item in FOCUSES:
    for _generic in ('sr_civil_industry_bonus', 'sr_civil_electronics_bonus'):
        if _generic in _item['reward']:
            _name = _item['id'] + '_research_bonus'
            _item['reward'] = _item['reward'].replace(_generic, _name)
            LOC[_name] = {'de': _item['de'] + ': Forschungsförderung',
                          'en': _item['en'] + ': Research Support'}

TERMINALS = {
    'economy': [['sr_lito_shared_prosperity']],
    'federation': [['sr_lito_federal_unity']],
    'research': [['sr_lito_knowledge_for_all']],
}
