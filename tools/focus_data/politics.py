"""Lito's political and diplomatic focus data; no filesystem side effects."""


def focus(id, branch, column, row, parents, de, en, de_desc, en_desc, reward, cost=5, **extra):
    return dict(id=id, branch=branch, column=column, row=row, parents=parents,
                de=de, en=en, de_desc=de_desc, en_desc=en_desc,
                reward=reward, cost=cost, **extra)


FOCUSES = [
    focus('sr_lito_politics_party_congress', 'politics', 1, 2, ['sr_lito_congress'],
          'Ein Mandat für Lito', 'A Mandate for Lito',
          'Ein Parteikongress bestätigt Cosif Kozs Litos Führungsanspruch. Seine Autorität soll auf einem erklärten Programm beruhen. Erhalte 75 politische Macht.',
          'A party congress endorses Cosif Kozs Lito’s leadership and an explicit political program. Gain 75 political power.',
          'add_political_power = 75'),
    focus('sr_lito_politics_cadre_schools', 'politics', 1, 3, ['sr_lito_politics_party_congress'],
          'Agitprop der Völker', 'Agitprop of the Peoples',
          'Lito bündelt politische Bildung und Plakatkampagnen in einem gemeinsamen Agitprop-Büro. Die Sprachen und Erfahrungen der Republiken sollen die öffentliche Arbeit prägen. Öffnet die sowjetischen Agitprop-Kampagnen und gewährt täglich 0,05 politische Macht.',
          'Lito brings political education and poster campaigns together in a common Agitprop bureau. The republics’ languages and experiences shape its public work. Opens the Soviet Agitprop campaigns and grants 0.05 daily political power.',
          '''add_ideas = sr_lito_cadre_schools
set_country_flag = sr_lito_native_agitprop_unlocked
sr_lito_native_agitprop_sync_effect = yes
unlock_decision_category_tooltip = SOV_propaganda_campaigns''',
          available='custom_trigger_tooltip = { tooltip = sr_lito_native_agitprop_ready_tt has_country_flag = sr_lito_native_agitprop_ready }'),
    focus('sr_lito_politics_council_mandate', 'politics', 0, 4, ['sr_lito_politics_cadre_schools'],
          'Ein Mandat der Räte', 'A Mandate from the Councils',
          'Lito bindet seine Führung an die Zustimmung der Räte. Das kostet 50 politische Macht, stärkt die Unionsbalance um 5 Punkte und senkt den Widerstand aller vertretenen Republiken um 5. Der nationale Geist erhöht die Stabilität um 2,5 Prozentpunkte. Dieser Kurs schließt das zentrale Parteimandat aus.',
          'Lito binds his leadership to council consent. Spend 50 political power, gain 5 preservation points and reduce resistance in every represented republic by 5. The national spirit adds 2.5 percentage points of stability. This excludes a central party mandate.',
          '''add_political_power = -50
add_power_balance_value = { id = sr_union_balance value = 0.05 }
sr_lito_reduce_republic_resistance_effect = yes
add_ideas = sr_lito_council_mandate''',
          exclusive=['sr_lito_politics_central_mandate']),
    focus('sr_lito_politics_central_mandate', 'politics', 2, 4, ['sr_lito_politics_cadre_schools'],
          'Ein Mandat der Parteizentrale', 'A Mandate from Party Headquarters',
          'Eine straffe Zentrale beschleunigt politische Entscheidungen. Erhalte 50 politische Macht und täglich weitere 0,10. Der Preis sind 5 Punkte zur Seite des Einbruchs und ein Stabilitätsmalus von 2,5 Prozentpunkten. Dieser Kurs schließt das Rätemandat aus.',
          'A strong headquarters speeds political decisions. Gain 50 political power and another 0.10 daily. The price is 5 points toward breakdown and a stability penalty of 2.5 percentage points. This excludes the council mandate.',
          '''add_political_power = 50
add_power_balance_value = { id = sr_union_balance value = -0.05 }
add_ideas = sr_lito_central_mandate''',
          exclusive=['sr_lito_politics_council_mandate']),
    focus('sr_lito_politics_accountability', 'politics', 1, 5, [],
          'Rechenschaft vor der Union', 'Accountability to the Union',
          'Die Führung legt öffentlich Rechenschaft über ihre Zusagen ab. Die Aussprache erhöht die Stabilität um 3 Prozentpunkte, senkt aber die Kriegsunterstützung um 2 Prozentpunkte.',
          'The leadership publicly accounts for its promises. Debate adds 3 percentage points of stability but reduces war support by 2 percentage points.',
          'add_stability = 0.03\nadd_war_support = -0.02',
          parent_groups=[['sr_lito_politics_council_mandate', 'sr_lito_politics_central_mandate']]),
    focus('sr_lito_politics_anti_corruption', 'politics', 1, 6, ['sr_lito_politics_accountability'],
          'Die Privilegien überprüfen', 'Review the Privileges',
          'Eine Überprüfung von Amtsmissbrauch kostet politische Unterstützung, stärkt aber das Vertrauen in die Verwaltung. Verliere 50 politische Macht und erhalte 5 Prozentpunkte Stabilität.',
          'Reviewing abuses of office costs political support but strengthens trust in the administration. Lose 50 political power and gain 5 percentage points of stability.',
          'add_political_power = -50\nadd_stability = 0.05', cost=8),
    focus('sr_lito_politics_constitution', 'politics', 1, 7, ['sr_lito_politics_anti_corruption'],
          'Die föderale Verfassung', 'The Federal Constitution',
          'Ein verbindlicher Verfassungsrahmen ordnet die Rechte von Partei, Räten und Republiken. Gewinne 5 Punkte zur Erhaltung und senke den Widerstand jeder vertretenen Republik um 5.',
          'A binding constitutional framework defines the rights of the party, councils and republics. Gain 5 preservation points and reduce each represented republic’s resistance by 5.',
          '''add_power_balance_value = { id = sr_union_balance value = 0.05 }
sr_lito_reduce_republic_resistance_effect = yes''', cost=8),
    focus('sr_lito_politics_mandate', 'politics', 1, 8, ['sr_lito_politics_constitution'],
          'Litos politisches Vermächtnis', 'Lito’s Political Legacy',
          'Litos Regierung hat eine eigene institutionelle Grundlage geschaffen. Erhalte je 2,5 Prozentpunkte Stabilität und Kriegsunterstützung.',
          'Lito’s government has established its own institutional foundation. Gain 2.5 percentage points each of stability and war support.',
          'add_stability = 0.025\nadd_war_support = 0.025', cost=10),

    focus('sr_lito_homeland', 'diplomacy', 1, 2, ['sr_lito_congress'],
          'Die Heimat nicht vergessen', 'Remember the Homeland',
          'Litos jugoslawische Herkunft prägt seine Außenpolitik. Besteht Jugoslawien noch, verbessert sich die gegenseitige Meinung um 40. Erhalte außerdem 50 politische Macht.',
          'Lito’s Yugoslav origins shape his foreign policy. If Yugoslavia exists, mutual opinion improves by 40. Also gain 50 political power.',
          '''if = {
    limit = { exists = YUG }
    add_opinion_modifier = { target = YUG modifier = sr_yugoslav_friendship }
    YUG = { add_opinion_modifier = { target = SOV modifier = sr_yugoslav_friendship } }
}
add_political_power = 50'''),
    focus('sr_lito_belgrade', 'diplomacy', 1, 3, ['sr_lito_homeland'],
          'Brücken nach Belgrad', 'Bridges to Belgrade',
          'Wissenschaftliche und kulturelle Kontakte zur Heimat und ihrer Diaspora bereichern unsere Institute. Der wissenschaftliche Austausch gewährt 5 Prozent Forschungsgeschwindigkeit.',
          'Scientific and cultural ties with the homeland and its diaspora enrich our institutes. Scientific exchange grants 5 percent research speed.',
          'add_ideas = sr_balkan_exchange'),
    focus('sr_lito_independent_socialism', 'diplomacy', 1, 4, ['sr_lito_belgrade'],
          'Ein eigenständiger Sozialismus', 'An Independent Socialism',
          'Die Union bestimmt ihren außenpolitischen Kurs selbst. Ein gemeinsamer Stab bewertet unsere Sicherheitslage. Erhalte 15 Armeeerfahrung und 3 Prozentpunkte Kriegsunterstützung.',
          'The Union determines its own foreign policy. A joint staff reviews our security situation. Gain 15 army experience and 3 percentage points of war support.',
          'army_experience = 15\nadd_war_support = 0.03'),
    focus('sr_lito_balkan_partnership', 'diplomacy', 0, 5, ['sr_lito_independent_socialism'],
          'Partnerschaft auf Augenhöhe', 'A Partnership of Equals',
          'Wir werben bei Jugoslawien, Bulgarien und Griechenland um Zusammenarbeit. Bestehende Staaten erhalten gegenseitig 25 Meinungspunkte. Diplomatische Kontakte kosten 10 Prozent weniger Unterhalt. Der Kurs schließt regionalen Zwang aus; er annektiert oder unterwirft niemanden.',
          'We seek cooperation with Yugoslavia, Bulgaria and Greece. Existing countries gain 25 mutual opinion points. Maintaining improved relations costs 10 percent less. This excludes regional coercion and does not annex or subordinate anyone.',
          '''if = {
    limit = { exists = YUG }
    add_opinion_modifier = { target = YUG modifier = sr_lito_balkan_solidarity }
    YUG = { add_opinion_modifier = { target = SOV modifier = sr_lito_balkan_solidarity } }
}
if = {
    limit = { exists = BUL }
    add_opinion_modifier = { target = BUL modifier = sr_lito_balkan_solidarity }
    BUL = { add_opinion_modifier = { target = SOV modifier = sr_lito_balkan_solidarity } }
}
if = {
    limit = { exists = GRE }
    add_opinion_modifier = { target = GRE modifier = sr_lito_balkan_solidarity }
    GRE = { add_opinion_modifier = { target = SOV modifier = sr_lito_balkan_solidarity } }
}
add_ideas = sr_lito_balkan_diplomacy''', cost=8,
          exclusive=['sr_lito_regional_pressure']),
    focus('sr_lito_regional_pressure', 'diplomacy', 2, 5, ['sr_lito_independent_socialism'],
          'Regionalen Druck aufbauen', 'Build Regional Pressure',
          'Lito bereitet einen offensiveren Kurs vor. Erhalte 50 politische Macht und 5 Prozentpunkte Kriegsunterstützung, verliere aber 3 Prozentpunkte Stabilität. Kriegsrechtfertigungen dauern 5 Prozent kürzer. Der Kurs schließt die Partnerschaft auf Augenhöhe aus und erklärt keinen Krieg.',
          'Lito prepares a more assertive course. Gain 50 political power and 5 percentage points of war support but lose 3 percentage points of stability. War justifications take 5 percent less time. This excludes a partnership of equals and declares no war.',
          '''add_political_power = 50
add_war_support = 0.05
add_stability = -0.03
add_ideas = sr_lito_pressure_doctrine''', cost=8,
          exclusive=['sr_lito_balkan_partnership']),
    focus('sr_lito_influence_yugoslavia', 'diplomacy', 0, 6, ['sr_lito_balkan_partnership'],
          'Verbindungen zur jugoslawischen Arbeiterbewegung', 'Ties with the Yugoslav Workers’ Movement',
          'Politische Verbindungen zu Jugoslawien stärken die dortige kommunistische Partei um bis zu 10 Prozentpunkte. Für 365 Tage unterstützen Netzwerke ihre tägliche ideologische Entwicklung. Die gegenseitige Meinung steigt um 25. Dieser Schwerpunkt wechselt keine Regierung und erzwingt weder Putsch noch Bündnisbeitritt.',
          'Political ties with Yugoslavia strengthen its communist party by up to 10 percentage points. For 365 days, networks support its daily ideological development. Mutual opinion increases by 25. This focus changes no government and forces neither a coup nor faction membership.',
          'if = {\n    limit = { exists = YUG NOT = { has_war_with = YUG } }\n    YUG = {\n        add_popularity = { ideology = communism popularity = 0.10 }\n        add_timed_idea = { idea = sr_lito_balkan_influence_network days = 365 }\n        add_opinion_modifier = { target = SOV modifier = sr_lito_political_contacts }\n    }\n    add_opinion_modifier = { target = YUG modifier = sr_lito_political_contacts }\n}', cost=5,
          available='exists = YUG\nNOT = { has_war_with = YUG }',
          bypass='NOT = { exists = YUG }'),
    focus('sr_lito_influence_albania', 'diplomacy', 1, 6, ['sr_lito_balkan_partnership'],
          'Politische Kontakte in Albanien', 'Political Contacts in Albania',
          'Politische Verbindungen zu Albanien stärken die dortige kommunistische Partei um bis zu 10 Prozentpunkte. Für 365 Tage unterstützen Netzwerke ihre tägliche ideologische Entwicklung. Die gegenseitige Meinung steigt um 25. Dieser Schwerpunkt wechselt keine Regierung und erzwingt weder Putsch noch Bündnisbeitritt.',
          'Political ties with Albania strengthen its communist party by up to 10 percentage points. For 365 days, networks support its daily ideological development. Mutual opinion increases by 25. This focus changes no government and forces neither a coup nor faction membership.',
          'if = {\n    limit = { exists = ALB NOT = { has_war_with = ALB } }\n    ALB = {\n        add_popularity = { ideology = communism popularity = 0.10 }\n        add_timed_idea = { idea = sr_lito_balkan_influence_network days = 365 }\n        add_opinion_modifier = { target = SOV modifier = sr_lito_political_contacts }\n    }\n    add_opinion_modifier = { target = ALB modifier = sr_lito_political_contacts }\n}', cost=5,
          available='exists = ALB\nNOT = { has_war_with = ALB }',
          bypass='NOT = { exists = ALB }'),
    focus('sr_lito_influence_bulgaria', 'diplomacy', 0, 7, ['sr_lito_balkan_partnership'],
          'Die bulgarische Linke stärken', 'Strengthen the Bulgarian Left',
          'Politische Verbindungen zu Bulgarien stärken die dortige kommunistische Partei um bis zu 10 Prozentpunkte. Für 365 Tage unterstützen Netzwerke ihre tägliche ideologische Entwicklung. Die gegenseitige Meinung steigt um 25. Dieser Schwerpunkt wechselt keine Regierung und erzwingt weder Putsch noch Bündnisbeitritt.',
          'Political ties with Bulgaria strengthen its communist party by up to 10 percentage points. For 365 days, networks support its daily ideological development. Mutual opinion increases by 25. This focus changes no government and forces neither a coup nor faction membership.',
          'if = {\n    limit = { exists = BUL NOT = { has_war_with = BUL } }\n    BUL = {\n        add_popularity = { ideology = communism popularity = 0.10 }\n        add_timed_idea = { idea = sr_lito_balkan_influence_network days = 365 }\n        add_opinion_modifier = { target = SOV modifier = sr_lito_political_contacts }\n    }\n    add_opinion_modifier = { target = BUL modifier = sr_lito_political_contacts }\n}', cost=5,
          available='exists = BUL\nNOT = { has_war_with = BUL }',
          bypass='NOT = { exists = BUL }'),
    focus('sr_lito_influence_greece', 'diplomacy', 1, 7, ['sr_lito_balkan_partnership'],
          'Die griechische Arbeiterbewegung fördern', 'Support the Greek Workers’ Movement',
          'Politische Verbindungen zu Griechenland stärken die dortige kommunistische Partei um bis zu 10 Prozentpunkte. Für 365 Tage unterstützen Netzwerke ihre tägliche ideologische Entwicklung. Die gegenseitige Meinung steigt um 25. Dieser Schwerpunkt wechselt keine Regierung und erzwingt weder Putsch noch Bündnisbeitritt.',
          'Political ties with Greece strengthen its communist party by up to 10 percentage points. For 365 days, networks support its daily ideological development. Mutual opinion increases by 25. This focus changes no government and forces neither a coup nor faction membership.',
          'if = {\n    limit = { exists = GRE NOT = { has_war_with = GRE } }\n    GRE = {\n        add_popularity = { ideology = communism popularity = 0.10 }\n        add_timed_idea = { idea = sr_lito_balkan_influence_network days = 365 }\n        add_opinion_modifier = { target = SOV modifier = sr_lito_political_contacts }\n    }\n    add_opinion_modifier = { target = GRE modifier = sr_lito_political_contacts }\n}', cost=5,
          available='exists = GRE\nNOT = { has_war_with = GRE }',
          bypass='NOT = { exists = GRE }'),
    focus('sr_lito_influence_romania', 'diplomacy', 0, 8, ['sr_lito_balkan_partnership'],
          'Sozialistische Netzwerke in Rumänien', 'Socialist Networks in Romania',
          'Politische Verbindungen zu Rumänien stärken die dortige kommunistische Partei um bis zu 10 Prozentpunkte. Für 365 Tage unterstützen Netzwerke ihre tägliche ideologische Entwicklung. Die gegenseitige Meinung steigt um 25. Dieser Schwerpunkt wechselt keine Regierung und erzwingt weder Putsch noch Bündnisbeitritt.',
          'Political ties with Romania strengthen its communist party by up to 10 percentage points. For 365 days, networks support its daily ideological development. Mutual opinion increases by 25. This focus changes no government and forces neither a coup nor faction membership.',
          'if = {\n    limit = { exists = ROM NOT = { has_war_with = ROM } }\n    ROM = {\n        add_popularity = { ideology = communism popularity = 0.10 }\n        add_timed_idea = { idea = sr_lito_balkan_influence_network days = 365 }\n        add_opinion_modifier = { target = SOV modifier = sr_lito_political_contacts }\n    }\n    add_opinion_modifier = { target = ROM modifier = sr_lito_political_contacts }\n}', cost=5,
          available='exists = ROM\nNOT = { has_war_with = ROM }',
          bypass='NOT = { exists = ROM }'),
    focus('sr_lito_balkan_forum', 'diplomacy', 0, 9, [
              'sr_lito_influence_yugoslavia', 'sr_lito_influence_albania',
              'sr_lito_influence_bulgaria', 'sr_lito_influence_greece', 'sr_lito_influence_romania'],
          'Ein Forum für den Balkan', 'A Forum for the Balkans',
          'Auch Albanien und Rumänien werden zur Zusammenarbeit eingeladen. Bei bestehenden Staaten steigt die gegenseitige Meinung um 25. Die Union erhält 2,5 Prozentpunkte Stabilität und 3 Punkte zur Erhaltung. Die Einladung erzwingt weder einen Beitritt noch einen Gebietswechsel.',
          'Albania and Romania are invited to cooperate. Mutual opinion with existing countries increases by 25. Gain 2.5 percentage points of stability and 3 preservation points. Invitations force neither membership nor territorial change.',
          '''if = {
    limit = { exists = ALB }
    add_opinion_modifier = { target = ALB modifier = sr_lito_balkan_solidarity }
    ALB = { add_opinion_modifier = { target = SOV modifier = sr_lito_balkan_solidarity } }
}
if = {
    limit = { exists = ROM }
    add_opinion_modifier = { target = ROM modifier = sr_lito_balkan_solidarity }
    ROM = { add_opinion_modifier = { target = SOV modifier = sr_lito_balkan_solidarity } }
}
add_stability = 0.025
add_power_balance_value = { id = sr_union_balance value = 0.03 }''', cost=10),
    focus('sr_lito_balkan_cooperation', 'diplomacy', 1, 10, ['sr_lito_balkan_forum'],
          'Die Balkanbewegungen koordinieren', 'Coordinate the Balkan Movements',
          'Die politischen Verbindungen bilden ein gemeinsames Forum für wissenschaftlichen und organisatorischen Austausch. Erhalte 5 Punkte zur Erhaltung und einen Forschungsbonus von 50 Prozent für eine Industrietechnologie. Die beteiligten Länder behalten ihre eigenen Regierungen und Bündnisse.',
          'Political contacts form a joint forum for scientific and organizational exchange. Gain 5 preservation points and one 50 percent research bonus for industrial technology. Participating countries retain their own governments and factions.',
          '''add_power_balance_value = { id = sr_union_balance value = 0.05 }
add_tech_bonus = { name = sr_lito_balkan_research bonus = 0.5 uses = 1 category = industry }''', cost=10),
    focus('sr_lito_polish_frontier', 'diplomacy', 2, 6, ['sr_lito_regional_pressure'],
          'Die polnische Grenzfrage', 'The Polish Frontier Question',
          'Wir bereiten eine gewaltsame Neuordnung im Westen vor. Gegen ein weiterhin bestehendes Polen, das kein eigener Untertan ist, erhalten wir ein 730 Tage gültiges Annexionskriegsziel. Der Schwerpunkt erklärt keinen Krieg und ist nicht während eines bereits laufenden Krieges gegen Polen verfügbar.',
          'We prepare a forcible reordering in the west. Gain a 730-day annexation war goal against an existing Poland that is not our subject. This declares no war and is unavailable during an ongoing war with Poland.',
          '''if = {
    limit = {
        exists = POL
        NOT = { has_war_with = POL }
        POL = { NOT = { is_subject_of = ROOT } }
    }
    create_wargoal = { type = annex_everything target = POL expire = 730 }
}''', cost=10,
          available='exists = POL\nNOT = { has_war_with = POL }\nPOL = { NOT = { is_subject_of = ROOT } }',
          bypass='OR = { NOT = { exists = POL } sr_formable_controls_poland = yes POL = { is_subject_of = ROOT } }'),
    focus('sr_lito_straits_question', 'diplomacy', 2, 7, ['sr_lito_polish_frontier'],
          'Die Meerengenfrage', 'The Straits Question',
          'Der offensive Kurs richtet sich nun auf die Türkei. Gegen eine weiterhin bestehende Türkei, die kein eigener Untertan ist, entsteht ein 730 Tage gültiges Annexionskriegsziel. Es umfasst die Türkei, nicht nur die Meerengen, und erklärt keinen Krieg.',
          'Our assertive course now turns toward Turkey. Gain a 730-day annexation war goal against an existing Turkey that is not our subject. It covers Turkey rather than only the straits and declares no war.',
          '''if = {
    limit = {
        exists = TUR
        NOT = { has_war_with = TUR }
        TUR = { NOT = { is_subject_of = ROOT } }
    }
    create_wargoal = { type = annex_everything target = TUR expire = 730 }
}''', cost=10,
          available='exists = TUR\nNOT = { has_war_with = TUR }\nTUR = { NOT = { is_subject_of = ROOT } }',
          bypass='OR = { NOT = { exists = TUR } sr_formable_controls_turkey = yes TUR = { is_subject_of = ROOT } }'),
]

IDEAS = {
    'sr_lito_cadre_schools': {
        'de': 'Kader für die Föderation', 'en': 'Cadres for the Federation',
        'de_desc': 'Verwaltungsnachwuchs erleichtert die Koordination: täglich +0,05 politische Macht.',
        'en_desc': 'Trained administrators facilitate coordination: +0.05 daily political power.',
        'modifier': 'political_power_gain = 0.05',
    },
    'sr_lito_council_mandate': {
        'de': 'Mandat der Räte', 'en': 'Mandate from the Councils',
        'de_desc': 'Die Einbindung der Räte stärkt die Stabilität um 2,5 Prozentpunkte.',
        'en_desc': 'Council participation adds 2.5 percentage points of stability.',
        'modifier': 'stability_factor = 0.025',
    },
    'sr_lito_central_mandate': {
        'de': 'Mandat der Parteizentrale', 'en': 'Mandate from Party Headquarters',
        'de_desc': 'Tägliche politische Macht: +0,10. Stabilität: −2,5 Prozentpunkte.',
        'en_desc': 'Daily political power: +0.10. Stability: −2.5 percentage points.',
        'modifier': 'political_power_gain = 0.10\nstability_factor = -0.025',
    },
    'sr_balkan_exchange': {
        'de': 'Wissenschaftlicher Austausch', 'en': 'Scientific Exchange',
        'de_desc': 'Kontakte zur jugoslawischen Heimat und ihrer Diaspora erhöhen die Forschungsgeschwindigkeit um 5 Prozent.',
        'en_desc': 'Ties with the Yugoslav homeland and its diaspora increase research speed by 5 percent.',
        'modifier': 'research_speed_factor = 0.05',
    },
    'sr_lito_balkan_diplomacy': {
        'de': 'Diplomatie auf Augenhöhe', 'en': 'Diplomacy Among Equals',
        'de_desc': 'Die Pflege verbesserter Beziehungen kostet 10 Prozent weniger politische Macht.',
        'en_desc': 'Maintaining improved relations costs 10 percent less political power.',
        'modifier': 'improve_relations_maintain_cost_factor = -0.10',
    },
    'sr_lito_pressure_doctrine': {
        'de': 'Regionaler Druck', 'en': 'Regional Pressure',
        'de_desc': 'Kriegsrechtfertigungen dauern 5 Prozent kürzer.',
        'en_desc': 'War justifications take 5 percent less time.',
        'modifier': 'justify_war_goal_time = -0.05',
    },
    'sr_lito_balkan_influence_network': {
        'de': 'Sozialistische Kontaktnetzwerke', 'en': 'Socialist Contact Networks',
        'de_desc': 'Politische Kontakte und organisatorische Unterstützung stärken für 365 Tage den kommunistischen Einfluss. Tägliche kommunistische Unterstützung: +0,02. Keine automatische Regierungsänderung.',
        'en_desc': 'Political contacts and organizational support strengthen communist influence for 365 days. Daily communist support: +0.02. No automatic change of government.',
        'modifier': 'communism_drift = 0.02',
    },

}

OPINIONS = {
    'sr_yugoslav_friendship': {'de': 'Litos jugoslawische Verbundenheit', 'en': 'Lito’s Yugoslav Ties', 'value': 40},
    'sr_lito_balkan_solidarity': {'de': 'Föderale Gesprächsbereitschaft', 'en': 'Willingness to Cooperate', 'value': 25},
    'sr_lito_political_contacts': {'de': 'Sozialistische politische Kontakte', 'en': 'Socialist Political Contacts', 'value': 25},
}

LOC = {'sr_lito_balkan_research': {'de': 'Gemeinsame industrielle Forschung', 'en': 'Joint Industrial Research'}}

TERMINALS = {
    'politics': [['sr_lito_politics_mandate']],
    'diplomacy': [['sr_lito_balkan_cooperation', 'sr_lito_straits_question']],
}
