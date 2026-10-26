"""Military focus data for Lito's Union; emitted by the root tree generator.

Native effects and modifier names were checked against the current CWTools HOI4
configuration (effects.cwt and modifiers.cwt). No technology category is guessed.
These data have not been executed by the HOI4 engine.
"""


FOCUSES = []
IDEAS = {}
LOC = {}
TERMINALS = {
    'army': [['sr_lito_army_homeland_defence']],
    'air': [['sr_lito_air_operational_readiness']],
    'navy': [['sr_lito_navy_joint_exercises']],
}


def focus(key, branch, column, row, parents, cost, de, en, de_desc, en_desc,
          reward, **extra):
    item = {
        'id': key, 'branch': branch, 'column': column, 'row': row,
        'parents': parents, 'cost': cost, 'de': de, 'en': en,
        'de_desc': de_desc, 'en_desc': en_desc, 'reward': reward,
    }
    item.update(extra)
    FOCUSES.append(item)


def idea(key, de, en, de_desc, en_desc, modifier):
    IDEAS[key] = {
        'de': de, 'en': en, 'de_desc': de_desc, 'en_desc': en_desc,
        'modifier': modifier,
    }


# Army: three permanent national spirits, plus limited preparation programs.
idea('sr_lito_field_logistics', 'Versorgung bis zur Front', 'Supply to the Front',
     'Einheitliche Versorgungsverfahren senken den Nachschubverbrauch um 5 %.',
     'Common supply procedures reduce supply consumption by 5%.',
     'supply_consumption_factor = -0.05')
idea('sr_lito_army_staff', 'Föderaler Generalstab', 'Federal General Staff',
     'Abgestimmte Stabsarbeit senkt die Landdoktrinkosten um 5 % und erhöht die Planungsgeschwindigkeit um 5 %.',
     'Coordinated staff work reduces land doctrine costs by 5% and increases planning speed by 5%.',
     'land_doctrine_cost_factor = -0.05\nplanning_speed = 0.05')
idea('sr_lito_combined_arms', 'Verbundene Waffen', 'Combined Arms',
     'Gemeinsame Verfahren erhöhen die Heeresorganisation um 3 % und die Divisionsgeschwindigkeit um 2 %.',
     'Joint procedures increase army organization by 3% and division speed by 2%.',
     'army_org_factor = 0.03\narmy_speed_factor = 0.02')
idea('sr_lito_officer_schools', 'Praktische Offiziersausbildung', 'Practical Officer Training',
     'Ein befristetes Ausbildungsprogramm senkt die Ausbildungszeit des Heeres um 5 %.',
     'A temporary training program reduces army training time by 5%.',
     'training_time_army_factor = -0.05')
idea('sr_lito_artillery_coordination', 'Eingespielte Artillerie', 'Coordinated Artillery',
     'Gemeinsame Feuerplanung erhöht den Artillerieangriff vorübergehend um 5 %.',
     'Joint fire planning temporarily increases artillery attack by 5%.',
     'army_artillery_attack_factor = 0.05')
idea('sr_lito_defence_preparation', 'Vorbereitete Heimatverteidigung', 'Prepared Homeland Defense',
     'Vorbereitete Verteidigungspläne erhöhen die Verteidigung auf Kerngebieten und die Eingrabungsgeschwindigkeit jeweils um 5 %.',
     'Prepared defensive plans increase defense on core territory and entrenchment speed by 5% each.',
     'army_core_defence_factor = 0.05\ndig_in_speed_factor = 0.05')

focus('sr_lito_army_review', 'army', 1, 2, ['sr_lito_congress'], 5,
      'Die Rote Armee überprüfen', 'Review the Red Army',
      'Lito lässt Ausbildung und Führung auswerten. Die Bestandsaufnahme gewährt 25 Armeeerfahrung.',
      'Lito orders a review of training and leadership, granting 25 army experience.',
      'army_experience = 25')
focus('sr_lito_army_officers', 'army', 0, 3, ['sr_lito_army_review'], 8,
      'Offiziere für die Föderation', 'Officers for the Federation',
      'Gemeinsame Offiziersschulen bringen die Republiken zusammen. Für 730 Tage sinkt die Ausbildungszeit des Heeres um 5 %.',
      'Joint officer schools bring the republics together. Army training time is reduced by 5% for 730 days.',
      'add_timed_idea = { idea = sr_lito_officer_schools days = 730 }')
focus('sr_lito_army_supply', 'army', 2, 3, ['sr_lito_army_review'], 8,
      'Versorgung bis zur Front', 'Supply to the Front',
      'Zuständigkeiten und Transportpläne werden vereinheitlicht. Der Nachschubverbrauch sinkt dauerhaft um 5 %.',
      'Responsibilities and transport plans are standardized, permanently reducing supply consumption by 5%.',
      'add_ideas = sr_lito_field_logistics')
focus('sr_lito_army_staff_work', 'army', 0, 4, ['sr_lito_army_officers'], 10,
      'Ein föderaler Generalstab', 'A Federal General Staff',
      'Der neue Generalstab senkt Landdoktrinkosten um 5 % und erhöht die Planungsgeschwindigkeit um 5 %.',
      'The new general staff reduces land doctrine costs by 5% and increases planning speed by 5%.',
      'add_ideas = sr_lito_army_staff')
focus('sr_lito_army_artillery', 'army', 2, 4, ['sr_lito_army_supply'], 8,
      'Feuerpläne statt Einzelbefehle', 'Fire Plans Instead of Isolated Orders',
      'Abgestimmtes Artilleriefeuer gewährt 20 Armeeerfahrung und 730 Tage lang 5 % Artillerieangriff.',
      'Coordinated artillery fire grants 20 army experience and 5% artillery attack for 730 days.',
      'army_experience = 20\nadd_timed_idea = { idea = sr_lito_artillery_coordination days = 730 }')
focus('sr_lito_army_combined_arms', 'army', 1, 5,
      ['sr_lito_army_staff_work', 'sr_lito_army_artillery'], 10,
      'Infanterie und Panzer gemeinsam', 'Infantry and Armor Together',
      'Gemeinsame Einsatzverfahren erhöhen die Heeresorganisation um 3 % und die Divisionsgeschwindigkeit um 2 %.',
      'Joint operational procedures increase army organization by 3% and division speed by 2%.',
      'add_ideas = sr_lito_combined_arms')
focus('sr_lito_army_readiness', 'army', 1, 6, ['sr_lito_army_combined_arms'], 8,
      'Manöver aller Republiken', 'Maneuvers of All Republics',
      'Unionsweite Manöver gewähren 25 Armeeerfahrung und 5 Prozentpunkte Kriegsunterstützung.',
      'Union-wide maneuvers grant 25 army experience and 5 percentage points of war support.',
      'army_experience = 25\nadd_war_support = 0.05')
focus('sr_lito_army_homeland_defence', 'army', 1, 7, ['sr_lito_army_readiness'], 10,
      'Jede Republik verteidigen', 'Defend Every Republic',
      'Für 1095 Tage steigen die Verteidigung auf Kerngebieten und die Eingrabungsgeschwindigkeit jeweils um 5 %.',
      'Defense on core territory and entrenchment speed increase by 5% each for 1095 days.',
      'add_timed_idea = { idea = sr_lito_defence_preparation days = 1095 }')


# Air force: interception and close support are deliberate, exclusive doctrines.
idea('sr_lito_air_maintenance', 'Verlässliche Bodenmannschaften', 'Reliable Ground Crews',
     'Gute Wartung senkt Luftunfälle um 5 % und erhöht die Luftmissionseffizienz um 2 %.',
     'Good maintenance reduces air accidents by 5% and increases air mission efficiency by 2%.',
     'air_accidents_factor = -0.05\nair_mission_efficiency = 0.02')
idea('sr_lito_air_interceptors', 'Schutz des Unionshimmels', 'Guardians of Union Skies',
     'Die Luftwaffe konzentriert sich auf Abfangen: Abfangeffizienz +5 %.',
     'The air force concentrates on interception: interception efficiency +5%.',
     'air_intercept_efficiency = 0.05')
idea('sr_lito_air_ground_support', 'Fliegende Unterstützung', 'Flying Support',
     'Die Luftwaffe konzentriert sich auf die Unterstützung der Bodentruppen: Bodenangriff +5 %.',
     'The air force concentrates on supporting ground forces: ground attack +5%.',
     'ground_attack_factor = 0.05')
idea('sr_lito_air_training', 'Gemeinsame Pilotenschulen', 'Joint Pilot Schools',
     'Ein befristetes Schulungsprogramm senkt Luftunfälle um 10 %.',
     'A temporary training program reduces air accidents by 10%.',
     'air_accidents_factor = -0.10')
idea('sr_lito_air_observation_network', 'Vernetzte Luftbeobachtung', 'Connected Air Observation',
     'Der Austausch von Beobachtungsmeldungen erhöht die Lufterkennung um 5 %.',
     'Sharing observation reports increases air detection by 5%.',
     'air_detection = 0.05')
idea('sr_lito_air_joint_command', 'Gemeinsame Luftplanung', 'Joint Air Planning',
     'Ein befristetes Planungsprogramm senkt die Luftdoktrinkosten um 5 %.',
     'A temporary planning program reduces air doctrine costs by 5%.',
     'air_doctrine_cost_factor = -0.05')
idea('sr_lito_air_readiness', 'Einsatzbereite Luftverbände', 'Operational Air Formations',
     'Vorbereitete Verbände verbrauchen 5 % weniger Treibstoff und erhalten 2 % Luftmissionseffizienz.',
     'Prepared formations consume 5% less fuel and gain 2% air mission efficiency.',
     'air_fuel_consumption_factor = -0.05\nair_mission_efficiency = 0.02')

focus('sr_lito_air_command', 'air', 1, 2, ['sr_lito_congress'], 5,
      'Eine Luftwaffe für die Union', 'An Air Force for the Union',
      'Die Bestandsaufnahme der Luftstreitkräfte gewährt 25 Luftwaffenerfahrung.',
      'A review of the air force grants 25 air experience.',
      'air_experience = 25')
focus('sr_lito_air_pilots', 'air', 0, 3, ['sr_lito_air_command'], 8,
      'Gemeinsame Pilotenschulen', 'Joint Pilot Schools',
      'Für 730 Tage senken gemeinsame Ausbildungsstandards die Luftunfälle um 10 %.',
      'Joint training standards reduce air accidents by 10% for 730 days.',
      'add_timed_idea = { idea = sr_lito_air_training days = 730 }')
focus('sr_lito_air_ground_crews', 'air', 2, 3, ['sr_lito_air_command'], 8,
      'Wartung vor Rekorden', 'Maintenance Before Records',
      'Gute Wartung senkt Luftunfälle dauerhaft um 5 % und erhöht die Luftmissionseffizienz um 2 %.',
      'Good maintenance permanently reduces air accidents by 5% and increases air mission efficiency by 2%.',
      'add_ideas = sr_lito_air_maintenance')
focus('sr_lito_air_interception', 'air', 0, 4,
      ['sr_lito_air_pilots', 'sr_lito_air_ground_crews'], 10,
      'Den Unionshimmel schützen', 'Protect Union Skies',
      'Lito priorisiert den Schutz des Luftraums: Abfangeffizienz +5 %. Dieser Schwerpunkt schließt die Spezialisierung auf Bodenunterstützung aus.',
      'Lito prioritizes airspace protection: interception efficiency +5%. This focus excludes specialization in ground support.',
      'add_ideas = sr_lito_air_interceptors',
      exclusive=['sr_lito_air_close_support'])
focus('sr_lito_air_close_support', 'air', 2, 4,
      ['sr_lito_air_pilots', 'sr_lito_air_ground_crews'], 10,
      'Über den Bodentruppen', 'Above the Ground Forces',
      'Lito priorisiert die Unterstützung an der Front: Bodenangriff +5 %. Dieser Schwerpunkt schließt die Spezialisierung auf Abfangen aus.',
      'Lito prioritizes support at the front: ground attack +5%. This focus excludes specialization in interception.',
      'add_ideas = sr_lito_air_ground_support',
      exclusive=['sr_lito_air_interception'])
focus('sr_lito_air_observation', 'air', 1, 5, [], 8,
      'Luftbeobachtung vernetzen', 'Connect Air Observation',
      'Nach der gewählten Spezialisierung verbessert ein gemeinsames Meldesystem die Lufterkennung 730 Tage lang um 5 % und gewährt 15 Luftwaffenerfahrung.',
      'Following the chosen specialization, a common reporting system improves air detection by 5% for 730 days and grants 15 air experience.',
      'air_experience = 15\nadd_timed_idea = { idea = sr_lito_air_observation_network days = 730 }',
      parent_groups=[['sr_lito_air_interception', 'sr_lito_air_close_support']])
focus('sr_lito_air_joint_planning', 'air', 1, 6, ['sr_lito_air_observation'], 8,
      'Gemeinsame Einsatzplanung', 'Joint Operational Planning',
      'Für 730 Tage sinken die Luftdoktrinkosten um 5 %. Die neue Planung gewährt außerdem 10 Luftwaffenerfahrung.',
      'Air doctrine costs are reduced by 5% for 730 days. The new planning also grants 10 air experience.',
      'air_experience = 10\nadd_timed_idea = { idea = sr_lito_air_joint_command days = 730 }')
focus('sr_lito_air_operational_readiness', 'air', 1, 7, ['sr_lito_air_joint_planning'], 10,
      'Vom Flugplatz zum Einsatz', 'From Airfield to Operation',
      'Für 1095 Tage sinkt der Treibstoffverbrauch der Luftwaffe um 5 % und ihre Missionseffizienz steigt um 2 %. Wir erhalten 20 Luftwaffenerfahrung.',
      'For 1095 days, air fuel consumption falls by 5% and air mission efficiency increases by 2%. We gain 20 air experience.',
      'air_experience = 20\nadd_timed_idea = { idea = sr_lito_air_readiness days = 1095 }')


# Navy: escorts and interdiction complement one another; no fake ship spawns.
idea('sr_lito_naval_production', 'Koordinierte Werftarbeit', 'Coordinated Dockyard Work',
     'Gemeinsame Produktionsstandards erhöhen den Werftausstoß um 5 %.',
     'Common production standards increase dockyard output by 5%.',
     'industrial_capacity_dockyard = 0.05')
idea('sr_lito_naval_escorts', 'Geschützte Seewege', 'Protected Sea Lanes',
     'Eingespielte Sicherungsverbände erhöhen die Konvoischutzeffizienz um 5 %.',
     'Experienced escort formations increase convoy escort efficiency by 5%.',
     'convoy_escort_efficiency = 0.05')
idea('sr_lito_naval_fuel', 'Sparsame Flottenführung', 'Efficient Fleet Management',
     'Abgestimmte Fahrt- und Versorgungspläne senken den Treibstoffverbrauch der Marine um 5 %.',
     'Coordinated sailing and supply plans reduce naval fuel consumption by 5%.',
     'navy_fuel_consumption_factor = -0.05')
idea('sr_lito_naval_crew_training', 'Ausgebildete Schiffsbesatzungen', 'Trained Ship Crews',
     'Ein befristetes Ausbildungsprogramm erhöht die Marineorganisation um 5 %.',
     'A temporary training program increases naval organization by 5%.',
     'navy_org_factor = 0.05')
idea('sr_lito_naval_interdiction', 'Geübte Handelsstörer', 'Trained Commerce Raiders',
     'Verbesserte Einsatzverfahren erhöhen die Konvoiüberfalleffizienz um 5 %.',
     'Improved procedures increase convoy raiding efficiency by 5%.',
     'convoy_raiding_efficiency_factor = 0.05')
idea('sr_lito_naval_observation', 'Gemeinsames Seelagebild', 'Shared Naval Situation Picture',
     'Geteilte Beobachtungen erhöhen die Marinekoordination um 3 %.',
     'Shared observations increase naval coordination by 3%.',
     'naval_coordination = 0.03')
idea('sr_lito_naval_readiness', 'Zusammenwirkende Flotten', 'Cooperating Fleets',
     'Gemeinsame Manöver erhöhen die Marineorganisation um 3 %.',
     'Joint maneuvers increase naval organization by 3%.',
     'navy_org_factor = 0.03')

focus('sr_lito_navy_review', 'navy', 1, 2, ['sr_lito_congress'], 5,
      'Die Flotten überprüfen', 'Review the Fleets',
      'Eine gemeinsame Bestandsaufnahme der Flotten gewährt 25 Marineerfahrung.',
      'A joint review of the fleets grants 25 navy experience.',
      'navy_experience = 25')
focus('sr_lito_navy_crews', 'navy', 0, 3, ['sr_lito_navy_review'], 8,
      'Seeleute gemeinsam ausbilden', 'Train Sailors Together',
      'Für 730 Tage verbessert das gemeinsame Ausbildungsprogramm die Marineorganisation um 5 %.',
      'A joint training program improves naval organization by 5% for 730 days.',
      'add_timed_idea = { idea = sr_lito_naval_crew_training days = 730 }')
focus('sr_lito_navy_dockyards', 'navy', 2, 3, ['sr_lito_navy_review'], 8,
      'Werften der Union koordinieren', 'Coordinate Union Dockyards',
      'Gemeinsame Standards erhöhen den Werftausstoß dauerhaft um 5 %.',
      'Common standards permanently increase dockyard output by 5%.',
      'add_ideas = sr_lito_naval_production')
focus('sr_lito_navy_escorts', 'navy', 0, 4, ['sr_lito_navy_crews'], 8,
      'Die Konvois schützen', 'Protect the Convoys',
      'Gemeinsame Sicherungsübungen erhöhen die Konvoischutzeffizienz dauerhaft um 5 %.',
      'Joint escort exercises permanently increase convoy escort efficiency by 5%.',
      'add_ideas = sr_lito_naval_escorts')
focus('sr_lito_navy_interdiction', 'navy', 2, 4, ['sr_lito_navy_dockyards'], 8,
      'Gegnerische Versorgung unterbrechen', 'Disrupt Enemy Supply',
      'Für 730 Tage steigt die Konvoiüberfalleffizienz um 5 %. Die Erprobung gewährt 15 Marineerfahrung.',
      'Convoy raiding efficiency increases by 5% for 730 days. Trials grant 15 navy experience.',
      'navy_experience = 15\nadd_timed_idea = { idea = sr_lito_naval_interdiction days = 730 }')
focus('sr_lito_navy_observation', 'navy', 1, 5,
      ['sr_lito_navy_escorts', 'sr_lito_navy_interdiction'], 8,
      'Ein gemeinsames Seelagebild', 'A Shared Naval Situation Picture',
      'Für 730 Tage verbessert der Austausch von Beobachtungen die Marinekoordination um 3 %.',
      'Sharing observations improves naval coordination by 3% for 730 days.',
      'add_timed_idea = { idea = sr_lito_naval_observation days = 730 }')
focus('sr_lito_navy_fuel', 'navy', 1, 6, ['sr_lito_navy_observation'], 8,
      'Treibstoff für die Flotten', 'Fuel for the Fleets',
      'Abgestimmte Fahrtpläne senken den Treibstoffverbrauch der Marine dauerhaft um 5 %.',
      'Coordinated sailing plans permanently reduce naval fuel consumption by 5%.',
      'add_ideas = sr_lito_naval_fuel')
focus('sr_lito_navy_joint_exercises', 'navy', 1, 7, ['sr_lito_navy_fuel'], 10,
      'Gemeinsame Flottenmanöver', 'Joint Fleet Maneuvers',
      'Großmanöver gewähren 35 Marineerfahrung und erhöhen die Marineorganisation 1095 Tage lang um 3 %.',
      'Major maneuvers grant 35 navy experience and increase naval organization by 3% for 1095 days.',
      'navy_experience = 35\nadd_timed_idea = { idea = sr_lito_naval_readiness days = 1095 }')
