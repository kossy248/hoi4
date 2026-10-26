"""Twenty-four later focuses: Lito's institutions, industrial society and army.

The original early focuses stay in place, including all government-project
requirements. Existing artwork is reused explicitly through icon_source.
"""
from .civil import _construction


FOCUSES = []
IDEAS = {}
LOC = {}
OPINIONS = {}


def focus(key, branch, column, row, parents, cost, de, en, de_desc, en_desc,
          reward, icon):
    FOCUSES.append(dict(id=key, branch=branch, column=column, row=row,
                        parents=parents, cost=cost, de=de, en=en,
                        de_desc=de_desc, en_desc=en_desc, reward=reward,
                        icon_source=icon))


def idea(key, de, en, de_desc, en_desc, modifier):
    IDEAS[key] = dict(de=de, en=en, de_desc=de_desc, en_desc=en_desc,
                      modifier=modifier)


def trust(points):
    return (f'add_to_variable = {{ sr_story_trust = {points} }}\n'
            'clamp_variable = { var = sr_story_trust min = 0 max = 100 }')


# Politics: institutions should outlast the man whose portrait hangs above them.
focus('sr_lito_notebook', 'politics', 0, 9, ['sr_lito_politics_mandate'], 5,
      'Die Seiten, die Lito behielt', 'The Pages Lito Kept',
      'In einem abgegriffenen Notizbuch stehen keine Staatspläne, sondern Namen von Werkstätten, Grenzbahnhöfen und Genossen. Die Redaktion möchte daraus die Geschichte der neuen Union machen. Ein Ereignis entscheidet, ob auch Zweifel und Irrtümer veröffentlicht werden.',
      'A battered notebook contains workshops, border stations and comrades’ names rather than state plans. Editors want to make it the story of the new Union. An event decides whether its doubts and mistakes will also be published.',
      'country_event = { id = sr_expansion.1 days = 1 }', 'sr_lito_course')
focus('sr_lito_translation_chambers', 'politics', 2, 9, ['sr_lito_politics_mandate'], 5,
      'Ein Rednerpult für jeden Akzent', 'A Rostrum for Every Accent',
      'Eine Rede ist noch keine Mitsprache, wenn nur die Hauptstadt ihre Sprache versteht. Dolmetscherkammern machen Anträge der Republiken unmittelbar lesbar. Für 365 Tage: +2 Prozentpunkte Stabilität, aber −0,03 tägliche politische Macht; zusätzlich +3 Vertrauen.',
      'A speech is no participation when only the capital understands its language. Translation chambers make republican petitions accessible. For 365 days: +2 percentage points stability but −0.03 daily political power; also gain 3 trust.',
      'add_timed_idea = { idea = sr_exp_translation_chambers days = 365 }\n' + trust(3), 'sr_lito_republic_congress')
focus('sr_lito_citizen_letters', 'politics', 0, 10, ['sr_lito_notebook'], 5,
      'Briefe ohne Dienstsiegel', 'Letters without an Official Seal',
      'Die Poststelle erhält einen zweiten Eingang: Beschwerden dürfen die Regierung erreichen, ohne vorher vom örtlichen Parteibüro bestätigt zu werden. Gewinne 3 Vertrauen und 2 Punkte zur Erhaltung; der neue Eingabedienst kostet für 365 Tage täglich 0,03 politische Macht.',
      'A second entrance opens at the mail office: complaints may reach government without approval from the local party bureau. Gain 3 trust and 2 preservation points; the petition service costs 0.03 political power daily for 365 days.',
      trust(3) + '\nadd_power_balance_value = { id = sr_union_balance value = 0.02 }\nadd_timed_idea = { idea = sr_exp_petition_service days = 365 }', 'sr_lito_politics_accountability')
focus('sr_lito_federal_civil_service', 'politics', 2, 10, ['sr_lito_translation_chambers'], 8,
      'Der Staat muss sich erklären', 'The State Must Explain Itself',
      'Ein kasachischer Dorfsekretär und eine georgische Lehrerin sollen dieselbe Verordnung erklären können. Eine föderale Verwaltungsschule ersetzt widersprüchliche Rundschreiben durch verständliche Verfahren. Für 730 Tage: täglich +0,05 politische Macht.',
      'A Kazakh village secretary and a Georgian teacher should be able to explain the same decree. A federal administrative school replaces contradictory circulars with comprehensible procedures. Gain 0.05 daily political power for 730 days.',
      'add_timed_idea = { idea = sr_exp_civil_service days = 730 }', 'sr_lito_politics_cadre_schools')
focus('sr_lito_succession_charter', 'politics', 0, 11, ['sr_lito_citizen_letters'], 8,
      'Eine Verfassung nach Lito', 'A Constitution after Lito',
      'Im Verfassungsentwurf fehlt ein Name: der Nachfolger. Lito muss entscheiden, ob künftige Führung aus einer kontrollierten Parteizentrale oder einem gebundenen föderalen Verfahren hervorgeht. Das Ereignis begründet Institutionen und verändert Vertrauen und politische Handlungsfähigkeit.',
      'One name is absent from the draft constitution: the successor. Lito must choose whether future leadership rests on a controlled party headquarters or a binding federal procedure. The event establishes institutions and changes trust and political capacity.',
      'country_event = { id = sr_expansion.2 days = 1 }', 'sr_lito_politics_constitution')
focus('sr_lito_oath_to_peoples', 'politics', 2, 11, ['sr_lito_federal_civil_service'], 5,
      'Ein Eid auf die Völker', 'An Oath to the Peoples',
      'Die neuen Beamten schwören weder einem Porträt noch einer einzelnen Republik Treue. Ihr Eid gilt dem gemeinsamen Vertrag. Erhalte 3 Prozentpunkte Kriegsunterstützung und 3 Punkte zur Erhaltung.',
      'New officials pledge loyalty neither to a portrait nor to one republic. Their oath concerns the shared charter. Gain 3 percentage points war support and 3 preservation points.',
      'add_war_support = 0.03\nadd_power_balance_value = { id = sr_union_balance value = 0.03 }', 'sr_lito_union_charter')
focus('sr_lito_public_memory', 'politics', 0, 12, ['sr_lito_succession_charter'], 8,
      'Das Gedächtnis der Union', 'The Memory of the Union',
      'Archive sammeln neben Regierungserklärungen auch Arbeiterbriefe und die Protokolle gescheiterter Verhandlungen. Diese Union soll ihre Geschichte nicht bei jedem Führungswechsel neu erfinden müssen. Gewinne 5 Vertrauen und 2 Prozentpunkte Stabilität.',
      'Archives collect workers’ letters and records of failed negotiations beside government declarations. The Union should not have to reinvent its history after every change of leadership. Gain 5 trust and 2 percentage points stability.',
      trust(5) + '\nadd_stability = 0.02\nset_country_flag = sr_exp_public_memory', 'sr_lito_politics_mandate')
focus('sr_lito_living_constitution', 'politics', 2, 12, ['sr_lito_oath_to_peoples'], 8,
      'Der Vertrag gehört niemandem allein', 'No One Owns the Charter',
      'Die Verfassung liegt nun auch in Schulhäusern, Kasernen und Gemeindebüros. Ihre Bedeutung muss dort ausgehandelt werden, wo Menschen auf sie angewiesen sind. Der föderale Rechtsdienst gibt für 730 Tage +3 Prozentpunkte Stabilität, kostet jedoch täglich 0,03 politische Macht.',
      'The constitution now reaches schools, barracks and local offices. Its meaning must be discussed where people depend on it. A federal legal service gives 3 percentage points stability for 730 days but costs 0.03 political power daily.',
      'add_timed_idea = { idea = sr_exp_federal_legal_service days = 730 }', 'sr_lito_constitutional_guarantees')

# Industry: development creates towns, skills and disputes as well as output.
focus('sr_lito_union_reserve', 'economy', 0, 9, ['sr_lito_shared_prosperity'], 8,
      'Ein Winter in der Staatsreserve', 'A Winter in the State Reserve',
      'Der Aufbauplan verspricht neue Werke, die Vorratsverwaltung warnt vor einem einzigen schlechten Winter. Ein Ereignis verteilt knappe Mittel zwischen einer gemeinsamen Notreserve und sofortigem Ausbau. Beide Wege tragen einen wirtschaftlichen Preis.',
      'The development plan promises new factories; reserve administrators warn of one bad winter. An event allocates scarce resources between a common emergency reserve and immediate expansion. Both courses have an economic price.',
      'country_event = { id = sr_expansion.3 days = 1 }', 'sr_lito_federal_plan')
focus('sr_lito_danube_workshops', 'economy', 2, 9, ['sr_lito_shared_prosperity'], 8,
      'Werkstätten für die große Verbindung', 'Workshops for the Great Connection',
      'Von der Donau bis zum Dnjepr arbeiten Maschinen mit inkompatiblen Ersatzteilen. Ein gemeinsames Werkstattprogramm verbindet die Produktionsräume. Erhalte einen 50-Prozent-Bonus für Industrietechnologien und 15 politische Macht.',
      'From the Danube to the Dnieper, machines use incompatible spare parts. A common workshop program connects production regions. Gain one 50% industrial research bonus and 15 political power.',
      'add_tech_bonus = { name = sr_exp_workshop_standard_bonus bonus = 0.5 uses = 1 category = industry }\nadd_political_power = 15', 'sr_lito_regional_workshops')
focus('sr_lito_industrial_towns', 'economy', 0, 10, ['sr_lito_union_reserve'], 8,
      'Ein Werk ist noch keine Stadt', 'A Factory Is Not Yet a Town',
      'Die neue Fabrik steht im Plan; Wohnungen, Schule und ein Gemeindesaal fehlen. Ein Ereignis entscheidet, ob die Siedlung sofort als Gemeinschaft gebaut wird oder zunächst allein der Produktionsauftrag zählt. Für Lito wird Entwicklung dadurch zu einer sozialen Entscheidung.',
      'The new factory appears in the plan; housing, a school and a meeting hall do not. An event decides whether the settlement becomes a community immediately or initially serves only its production order. For Lito, development becomes a social decision.',
      'country_event = { id = sr_expansion.4 days = 1 }', 'sr_lito_local_investment')
focus('sr_lito_maintenance_union', 'economy', 2, 10, ['sr_lito_danube_workshops'], 5,
      'Die Maschine soll morgen noch laufen', 'The Machine Must Run Tomorrow',
      'Wartungsbücher werden gemeinsam geführt, statt bei der nächsten Erfolgsmeldung zu verschwinden. Ersatzteile und Schulungen kosten heute Leistung, verhindern aber künftigen Stillstand. Für 730 Tage: +3 % Wachstum der Produktionseffizienz, −1 % Fabrikausstoß.',
      'Maintenance records are shared instead of disappearing behind the next success bulletin. Spares and training cost output today but prevent stoppages tomorrow. For 730 days: +3% production efficiency growth and −1% factory output.',
      'add_timed_idea = { idea = sr_exp_maintenance_union days = 730 }', 'sr_lito_industrial_union')
focus('sr_lito_common_assembly_halls', 'economy', 0, 11, ['sr_lito_industrial_towns'], 10,
      'Eine gemeinsame Montagehalle', 'A Common Assembly Hall',
      'Mehrere Republiken teilen einen Auftrag, statt parallele Kleinserien gegeneinander auszuspielen. Eine Zivilfabrik entsteht in geeignetem eigenem, kontrolliertem Kerngebiet. Gibt es keinen Bauplatz, erhalten wir 50 politische Macht.',
      'Several republics share a production order rather than competing through parallel small batches. Build a civilian factory in a suitable owned, controlled core. If there is no suitable space, gain 50 political power.',
      _construction('industrial_complex'), 'sr_lito_local_investment')
focus('sr_lito_defence_industrial_compact', 'economy', 2, 11, ['sr_lito_maintenance_union'], 10,
      'Rüstung im föderalen Auftrag', 'Armaments under Federal Contract',
      'Das Heer bestellt künftig nach gemeinsamen Standards; die Betriebe behalten ihre zivilen Vertretungen. Eine Militärfabrik entsteht in geeignetem eigenem, kontrolliertem Kerngebiet. Fehlt geeigneter Platz, gibt es 50 politische Macht.',
      'The army orders to common standards while factories retain their civilian representation. Build a military factory in a suitable owned, controlled core. If no suitable space exists, gain 50 political power.',
      _construction('arms_factory'), 'sr_lito_regional_workshops')
focus('sr_lito_development_school', 'economy', 0, 12, ['sr_lito_common_assembly_halls'], 8,
      'Der Bauplan wandert weiter', 'The Blueprint Travels On',
      'Ingenieure reisen nicht mehr nur mit einem Auftrag, sondern mit den Fehlerberichten des letzten Werks. Zwei 50-Prozent-Forschungsboni für Industrietechnologien helfen der nächsten Republik, diese Fehler nicht zu wiederholen.',
      'Engineers now travel with the previous factory’s error reports as well as its orders. Two 50% industrial research bonuses help the next republic avoid repeating those mistakes.',
      'add_tech_bonus = { name = sr_exp_development_school_bonus bonus = 0.5 uses = 2 category = industry }', 'sr_lito_research_exchange')
focus('sr_lito_workplace_charter', 'economy', 2, 12, ['sr_lito_defence_industrial_compact'], 8,
      'Die Schicht endet mit einem Recht', 'A Shift Ends with a Right',
      'Ein Vertrag über Produktion braucht auch Regeln über Unfälle, Schichtzeiten und Beschwerden. Ein gemeinsames Betriebsstatut gibt für 730 Tage +2 Prozentpunkte Stabilität und +2 % Fabrikausstoß. Sein Verwaltungsaufwand kostet täglich 0,03 politische Macht.',
      'A production contract also needs rules on accidents, shifts and complaints. A common workplace statute gives 2 percentage points stability and 2% factory output for 730 days. Its administration costs 0.03 political power daily.',
      'add_timed_idea = { idea = sr_exp_workplace_charter days = 730 }', 'sr_lito_workers_councils')

# Army: military policy is another test of the federal promise.
focus('sr_lito_army_citizens_charter', 'army', 0, 9, ['sr_lito_army_homeland_defence'], 8,
      'Der Soldat bleibt ein Bürger', 'The Soldier Remains a Citizen',
      'Der neue Soldateneid beruft sich auf die Union ihrer Völker. Der Generalstab fragt, ob deshalb auch Beschwerden gegen militärische Vorgesetzte zivil geprüft werden. Ein Ereignis bestimmt das Verhältnis zwischen Disziplin und Bürgerrechten.',
      'The new military oath invokes a Union of peoples. The general staff asks whether complaints against commanders will therefore face civilian review. An event defines the relationship between discipline and citizens’ rights.',
      'country_event = { id = sr_expansion.5 days = 1 }', 'sr_lito_shared_defence')
focus('sr_lito_signals_of_republics', 'army', 2, 9, ['sr_lito_army_homeland_defence'], 5,
      'Viele Sprachen, ein Funkspruch', 'Many Languages, One Signal',
      'Ein Befehl darf nicht am Akzent des Funkers scheitern. Gemeinsame Signaltafeln und technische Lehrgänge verbinden Einheiten aus allen Republiken. Erhalte einen 50-Prozent-Forschungsbonus für Elektronik.',
      'An order must not fail because of a radio operator’s accent. Common signal tables and technical courses connect units from all republics. Gain one 50% electronics research bonus.',
      'add_tech_bonus = { name = sr_exp_signals_bonus bonus = 0.5 uses = 1 category = electronics }', 'sr_lito_army_staff_work')
focus('sr_lito_front_and_home', 'army', 0, 10, ['sr_lito_army_citizens_charter'], 8,
      'Zwischen Front und Küchentisch', 'Between the Front and the Kitchen Table',
      'Ein Frontbrief und die Eingabe einer Arbeiterfamilie beschreiben dieselbe Lieferung aus verschiedenen Richtungen. Lito muss im Ereignis Mittel zwischen militärischer Bereitschaft und der Belastung der Familien verteilen. Beide Entscheidungen verändern zeitweise die Armee.',
      'A soldier’s letter and a worker family’s petition describe the same supply order from different directions. An event has Lito allocate resources between military readiness and burdens on families. Both choices temporarily change the army.',
      'country_event = { id = sr_expansion.6 days = 1 }', 'sr_lito_army_readiness')
focus('sr_lito_mobile_repair_columns', 'army', 2, 10, ['sr_lito_signals_of_republics'], 8,
      'Werkstätten hinter der Front', 'Workshops behind the Front',
      'Mechaniker aus den zivilen Betrieben begleiten nun die Nachschubkolonnen. Die Armee spart für 730 Tage 3 % Nachschubverbrauch, die abgeordneten Facharbeiter kosten jedoch 1 % Fabrikausstoß.',
      'Mechanics from civilian factories accompany supply columns. The army saves 3% supply consumption for 730 days, while the detached specialists cost 1% factory output.',
      'add_timed_idea = { idea = sr_exp_repair_columns days = 730 }', 'sr_lito_army_supply')
focus('sr_lito_field_hospitals_compact', 'army', 0, 11, ['sr_lito_front_and_home'], 8,
      'Niemand bleibt namenlos zurück', 'No One Is Left Nameless',
      'Sanitätsstellen gleichen Verwundetenlisten zwischen den Republiken ab und teilen ihre Erfahrungen. Für 730 Tage steigen die Personalrückführung aus Verlusten und die Erholung der Heeresorganisation jeweils um 3 %. Die Hilfe erreicht Verwundete, statt an den Verwaltungsgrenzen der Republiken zu enden.',
      'Medical posts compare casualty records across republics and share experience. For 730 days, casualty trickleback and army organization recovery increase by 3%. This affects manpower recovery rather than automatically restoring divisions.',
      'add_timed_idea = { idea = sr_exp_field_medical_network days = 730 }', 'sr_lito_army_officers')
focus('sr_lito_local_defence_registers', 'army', 2, 11, ['sr_lito_mobile_repair_columns'], 8,
      'Jedes Dorf kennt den Sammelplatz', 'Every Village Knows the Assembly Point',
      'Die Verteidigungskarte zeigt erstmals auch Schulen, Brücken und Gemeindelager. Örtliche Stellen planen gemeinsam mit dem Heer, statt erst auf den Ernstfall zu warten. Für 730 Tage: +3 % Verteidigung auf Kerngebiet und +3 % Eingrabungsgeschwindigkeit.',
      'The defence map now includes schools, bridges and communal depots. Local offices plan with the army rather than waiting for an emergency. For 730 days: +3% core-territory defence and +3% entrenchment speed.',
      'add_timed_idea = { idea = sr_exp_local_defence days = 730 }', 'sr_lito_army_homeland_defence')
focus('sr_lito_federal_officer_compact', 'army', 0, 12, ['sr_lito_field_hospitals_compact'], 10,
      'Die Schule der gemeinsamen Front', 'The School of the Common Front',
      'Das Offizierskolleg veröffentlicht die widersprüchlichen Berichte seiner Manöver. Aus ihnen entsteht eine gemeinsame Lehre, die Kritik nicht mit Illoyalität verwechselt. Erhalte zwei 50-Prozent-Boni auf die Kosten einer Landdoktrin und 10 Armeeerfahrung.',
      'The officer college publishes contradictory exercise reports. They become a common doctrine that does not confuse criticism with disloyalty. Gain two 50% land doctrine cost reductions and 10 army experience.',
      'add_doctrine_cost_reduction = { name = sr_exp_officer_compact_bonus cost_reduction = 0.5 uses = 2 category = land_doctrine }\narmy_experience = 10', 'sr_lito_army_combined_arms')
focus('sr_lito_army_in_union_service', 'army', 2, 12, ['sr_lito_local_defence_registers'], 10,
      'Die Waffen dienen dem Vertrag', 'Arms Serve the Charter',
      'Am Ende der Reform steht kein neuer militärischer Rang für Lito. Die Streitkräfte bestätigen ihre Pflichten gegenüber allen Republiken. Erhalte 3 Punkte zur Erhaltung, 3 Vertrauen und für 730 Tage +2 % Heeresorganisation.',
      'The reform ends without a new military rank for Lito. The armed forces reaffirm their duties toward every republic. Gain 3 preservation points, 3 trust and 2% army organization for 730 days.',
      'add_power_balance_value = { id = sr_union_balance value = 0.03 }\n' + trust(3) + '\nadd_timed_idea = { idea = sr_exp_charter_army days = 730 }', 'sr_lito_defence_council')


idea('sr_exp_translation_chambers', 'Dolmetscherkammern der Republiken', 'Republic Translation Chambers',
     'Stabilität: +2 Prozentpunkte; täglich −0,03 politische Macht für 365 Tage.',
     'Stability: +2 percentage points; −0.03 daily political power for 365 days.',
     'stability_factor = 0.02\npolitical_power_gain = -0.03')
idea('sr_exp_petition_service', 'Ein offener Eingabedienst', 'An Open Petition Service',
     'Die Bearbeitung direkter Eingaben kostet für 365 Tage täglich 0,03 politische Macht.',
     'Handling direct petitions costs 0.03 political power daily for 365 days.', 'political_power_gain = -0.03')
idea('sr_exp_civil_service', 'Eine verständliche Verwaltung', 'A Comprehensible Administration',
     'Täglich +0,05 politische Macht für 730 Tage.', 'Gain 0.05 daily political power for 730 days.', 'political_power_gain = 0.05')
idea('sr_exp_federal_legal_service', 'Föderaler Rechtsdienst', 'Federal Legal Service',
     'Stabilität: +3 Prozentpunkte; täglich −0,03 politische Macht für 730 Tage.',
     'Stability: +3 percentage points; −0.03 daily political power for 730 days.',
     'stability_factor = 0.03\npolitical_power_gain = -0.03')
idea('sr_exp_maintenance_union', 'Gemeinsame Wartungsbücher', 'Shared Maintenance Records',
     'Wachstum der Produktionseffizienz: +3 %; Fabrikausstoß: −1 % für 730 Tage.',
     'Production efficiency growth: +3%; factory output: −1% for 730 days.',
     'production_factory_efficiency_gain_factor = 0.03\nindustrial_capacity_factory = -0.01')
idea('sr_exp_workplace_charter', 'Föderales Betriebsstatut', 'Federal Workplace Statute',
     'Stabilität: +2 Prozentpunkte; Fabrikausstoß: +2 %; täglich −0,03 politische Macht für 730 Tage.',
     'Stability: +2 percentage points; factory output: +2%; −0.03 daily political power for 730 days.',
     'stability_factor = 0.02\nindustrial_capacity_factory = 0.02\npolitical_power_gain = -0.03')
idea('sr_exp_repair_columns', 'Mobile Reparaturkolonnen', 'Mobile Repair Columns',
     'Nachschubverbrauch: −3 %; Fabrikausstoß: −1 % für 730 Tage.',
     'Supply consumption: −3%; factory output: −1% for 730 days.',
     'supply_consumption_factor = -0.03\nindustrial_capacity_factory = -0.01')
idea('sr_exp_field_medical_network', 'Sanitätsnetz der Republiken', 'Republic Medical Network',
     'Personalrückführung: +3 %; Erholung der Heeresorganisation: +3 % für 730 Tage.',
     'Casualty trickleback: +3%; army organization recovery: +3% for 730 days.',
     'casualty_trickleback = 0.03\narmy_org_regain = 0.03')
idea('sr_exp_local_defence', 'Örtliche Verteidigungsregister', 'Local Defence Registers',
     'Verteidigung auf Kerngebiet: +3 %; Eingrabungsgeschwindigkeit: +3 % für 730 Tage.',
     'Core-territory defence: +3%; entrenchment speed: +3% for 730 days.',
     'army_core_defence_factor = 0.03\ndig_in_speed_factor = 0.03')
idea('sr_exp_charter_army', 'Armee im Dienst des Unionsvertrags', 'Army in Service of the Union Charter',
     'Heeresorganisation: +2 % für 730 Tage.', 'Army organization: +2% for 730 days.', 'army_org_factor = 0.02')

LOC.update({
    'sr_exp_workshop_standard_bonus': {'de': 'Gemeinsame Werkstattstandards', 'en': 'Common Workshop Standards'},
    'sr_exp_development_school_bonus': {'de': 'Erfahrungen des föderalen Aufbaus', 'en': 'Experience of Federal Development'},
    'sr_exp_signals_bonus': {'de': 'Gemeinsame Signaltechnik', 'en': 'Common Signals Technology'},
    'sr_exp_officer_compact_bonus': {'de': 'Lehren der gemeinsamen Front', 'en': 'Lessons of the Common Front'},
})

TERMINALS = {
    'politics': [['sr_lito_public_memory'], ['sr_lito_living_constitution']],
    'economy': [['sr_lito_development_school'], ['sr_lito_workplace_charter']],
    'army': [['sr_lito_federal_officer_compact'], ['sr_lito_army_in_union_service']],
}

assert len(FOCUSES) == 24
