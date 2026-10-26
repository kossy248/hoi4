# Authoritative common focus and base localization data. See tools/build_focus_tree.py.

COMMON = [{'id': 'sr_lito_course',
  'branch': 'common',
  'x': 23,
  'row': 0,
  'parents': [],
  'cost': 5,
  'de': 'Litos neuer Kurs',
  'en': 'Lito’s New Course',
  'de_desc': 'Cosif Kozs Lito ruft zum Aufbau einer sozialistischen Union gleichberechtigter Völker auf.',
  'en_desc': 'Cosif Kozs Lito calls for a socialist union of equal peoples.',
  'reward': 'add_political_power = 120'},
 {'id': 'sr_lito_congress',
  'branch': 'common',
  'x': 23,
  'row': 1,
  'parents': ['sr_lito_course'],
  'cost': 5,
  'de': 'Eine Union, viele Völker',
  'en': 'One Union, Many Peoples',
  'de_desc': 'Ein gemeinsamer Kongress eröffnet Litos föderales Regierungsprogramm: Partei, Republiken, '
             'Wirtschaft und Verteidigung müssen einen gemeinsamen Weg finden.',
  'en_desc': 'A joint congress opens Lito’s federal program: party, republics, economy and defence must find '
             'a common course.',
  'reward': 'add_stability = 0.05'}]

BASE_LOC = {'sr_lito_native_agitprop_ready_tt': {
 'de': 'Die originalen Agitprop-Dateien wurden durch den Lito-Installer erfolgreich vorbereitet.',
 'en': 'The Lito installer successfully prepared the original Agitprop files.'},
 'sr_lito_native_agitprop_councils_slot_tt': {
 'de': 'Nach „Agitprop der Völker“: ein weiterer originaler Agitprop-Posterplatz und die kollektivistische Kampagne.',
 'en': 'After Agitprop of the Peoples: one additional original Agitprop poster slot and the collectivist campaign.'},
 'sr_lito_native_agitprop_academy_slot_tt': {
 'de': 'Nach „Agitprop der Völker“: ein weiterer originaler Agitprop-Posterplatz und die Wissens- und Jugendkampagnen.',
 'en': 'After Agitprop of the Peoples: one additional original Agitprop poster slot and the knowledge and youth campaigns.'},
 'SOV_cosif_kozs_lito': {'de': 'Cosif Kozs Lito', 'en': 'Cosif Kozs Lito'},
 'SOV_cosif_kozs_lito_desc': {'de': 'Ein Revolutionär mit jugoslawischen Wurzeln, der in Russland blieb und '
                                    'die Führung der Sowjetunion übernahm. Lito will eine starke, föderale '
                                    'Union schaffen. Seine Bewährungsprobe ist der Widerspruch zwischen '
                                    'Selbstverwaltung und der Macht der Partei.',
                              'en': 'A revolutionary with Yugoslav roots who stayed in Russia and rose to '
                                    'lead the Soviet Union. Lito seeks a strong federal union. His central '
                                    'challenge is the tension between self-management and party power.'},
 'titoism': {'de': 'Titoismus', 'en': 'Titoism'},
 'titoism_desc': {'de': 'Der Titoismus verbindet sozialistisches Eigentum mit betrieblicher '
                        'Arbeiterselbstverwaltung, föderaler Mitbestimmung und außenpolitischer '
                        'Eigenständigkeit. Die Union soll durch gemeinsame Interessen zusammenhalten. Doch '
                        'Selbstverwaltung und die Macht der kommunistischen Partei stehen in einem dauernden '
                        'Spannungsverhältnis.',
                  'en': 'Titoism combines socialist ownership with workers’ self-management, federal '
                        'participation and an independent foreign policy. Shared interests should hold the '
                        'Union together, but self-management remains in tension with the power of the '
                        'communist party.'},
 'sr_soviet_tree': {'de': 'Litos Union', 'en': 'Lito’s Union'},
 'sr_industrial_research': {'de': 'Föderale Industrieforschung', 'en': 'Federal Industrial Research'},
 'sr_yugoslav_friendship': {'de': 'Litos jugoslawische Verbundenheit', 'en': 'Lito’s Yugoslav Ties'}}

IDEAS = {'sr_workers_councils': {'de': 'Arbeiterselbstverwaltung',
                         'en': 'Workers’ Self-Management',
                         'de_desc': 'Die Arbeiterräte organisieren die Produktion. Fabrikausstoß: +5 %.',
                         'en_desc': 'Workers’ councils organize production. Factory output: +5%.',
                         'modifier': 'industrial_capacity_factory = 0.05'},
 'sr_federal_planning': {'de': 'Föderale Investitionsplanung',
                         'en': 'Federal Investment Planning',
                         'de_desc': 'Abgestimmte Investitionen beschleunigen den Bau um 5 %.',
                         'en_desc': 'Coordinated investment increases construction speed by 5%.',
                         'modifier': 'production_speed_buildings_factor = 0.05'},
 'sr_federal_charter': {'de': 'Föderaler Unionsvertrag',
                        'en': 'Federal Union Charter',
                        'de_desc': 'Verbindliche Verfahren erleichtern die Zusammenarbeit. Tägliche '
                                   'politische Macht: +0,10.',
                        'en_desc': 'Binding procedures facilitate cooperation. Daily political power: +0.10.',
                        'modifier': 'political_power_gain = 0.1'},
 'sr_balkan_exchange': {'de': 'Wissenschaftlicher Austausch',
                        'en': 'Scientific Exchange',
                        'de_desc': 'Kontakte zur jugoslawischen Heimat und ihrer Diaspora beschleunigen die '
                                   'Forschung um 5 %.',
                        'en_desc': 'Ties with the Yugoslav homeland and its diaspora increase research speed '
                                   'by 5%.',
                        'modifier': 'research_speed_factor = 0.05'}}

OPINIONS = {'sr_yugoslav_friendship': {'de': 'Litos jugoslawische Verbundenheit',
                            'en': 'Lito’s Yugoslav Ties',
                            'value': 40}}
