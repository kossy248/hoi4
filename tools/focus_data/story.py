"""Narrative rewards for the existing focus tree; keeps its layout and IDs stable."""

ENCOUNTERS = {
    'sr_lito_workers_councils': (1, 'Eine Werkversammlung gerät zum Streit über Litos Versprechen: Entscheiden die Beschäftigten selbst, oder behält der Direktor das letzte Wort? Die Arbeiterselbstverwaltung bleibt bestehen; ihre praktische Ausgestaltung bestimmen wir im Ereignis. Nach drei Monaten folgt die erste Bilanz.', 'A factory assembly disputes Lito’s promise: do workers decide, or does the director retain the final word? Workers’ self-management remains; an event determines its practical form. A first report follows after three months.'),
    'sr_lito_agricultural_cooperatives': (2, 'Die Genossenschaften stehen bereit, doch die Gemeinden wollen wissen, wer über das Getreide verfügt. Wir wählen zwischen bezahlten Lieferverträgen und einer zentralen Abnahmequote. Beide Wege schaffen das Versorgungsnetz, aber Vertrauen und kurzfristige Erträge unterscheiden sich.', 'The cooperatives are ready, but villages want to know who controls their grain. Choose paid delivery contracts or a central procurement quota. Both establish the supply network, with different effects on trust and short-term output.'),
    'sr_lito_electronics_laboratories': (3, 'Die neuen Labore bringen zivile Forscher und den Nachrichtendienst an einen Tisch. Der Elektronikbonus bleibt erhalten; entscheiden müssen wir, ob veröffentlichte Forschung oder militärische Geheimhaltung Vorrang erhält. Vier Monate später meldet sich die Laborleitung erneut.', 'The new laboratories bring civilian researchers and intelligence officers together. The electronics bonus remains; we must choose between open research and military secrecy. Laboratory directors report again four months later.'),
    'sr_lito_army_officers': (4, 'Ein Manöverbericht widerspricht der Erfolgsmeldung des Generalstabs. Die Offiziersschulen werden eingerichtet; Lito entscheidet, ob Initiative an der Front oder die Verlässlichkeit zentraler Einsatzpläne den Unterricht prägt.', 'An exercise report contradicts the general staff’s success bulletin. Officer schools will open; Lito must decide whether frontline initiative or reliable central operational plans shape their teaching.'),
    'sr_lito_air_command': (5, 'Zwischen zwei Rekordmeldungen liegt ein Unfallbericht. Die Luftwaffenprüfung gewährt weiterhin Erfahrung; anschließend verteilen wir knappe Mittel zwischen Ersatzteilen und zusätzlichen Ausbildungsflügen. Beides gleichzeitig ist nicht finanziert.', 'Between two record-breaking bulletins lies an accident report. The air force review still grants experience; we then allocate scarce resources between spare parts and additional training flights. Funding does not cover both.'),
    'sr_lito_navy_review': (6, 'Die Admiräle legen Lito zwei unterschiedliche Karten vor: eine für den Auftritt der Union auf See und eine für bedrohte Handelsschiffe. Die Flottenprüfung gewährt Erfahrung; ihre politische Priorität entscheidet sich im anschließenden Gespräch.', 'The admirals present two maps: one showing the Union’s presence at sea, the other threatened merchant routes. The fleet review grants experience; the following discussion sets its political priority.'),
    'sr_lito_politics_anti_corruption': (7, 'Ein versiegeltes Dossier nennt ausgerechnet Genossen, die Litos Aufstieg ermöglicht haben. Eine unabhängige Untersuchung kostet politische Macht und bindet die Verwaltung. Ein begrenztes Verfahren schützt die Parteiführung, beschädigt aber das Vertrauen in die versprochene Gleichheit.', 'A sealed dossier names the very comrades who enabled Lito’s rise. An independent investigation costs political power and burdens administration. A limited inquiry protects party leadership but damages trust in its promise of equality.'),
}


def enrich(focuses):
    """Replace seven flat payouts with choices and append a narrative epilogue."""
    by_id = {item['id']: item for item in focuses}
    assert len(by_id) == len(focuses)
    for key, (number, de, en) in ENCOUNTERS.items():
        assert key in by_id and by_id[key]['reward'].strip(), f'Missing source reward: {key}'
        item = by_id[key]
        item['reward'] = f'country_event = {{ id = sr_focus_story.{number} days = 1 }}'
        item['de_desc'], item['en_desc'] = de, en
    ending = by_id['sr_lito_union_future']
    ending['reward'] += '\ncountry_event = { id = sr_focus_story.8 days = 1 }'
    ending['de_desc'] += ' Ein abschließender Bericht erinnert an die Entscheidungen, auf denen diese Union beruht.'
    ending['en_desc'] += ' A final report recalls the decisions on which this Union rests.'
    by_id['sr_lito_republic_congress']['reward'] += '\nsr_story_republic_petitions_effect = yes'
    by_id['sr_lito_republic_congress']['de_desc'] += ' Die Delegationen aus Ukraine, Georgien und Kasachstan legen anschließend konkrete Forderungen vor.'
    by_id['sr_lito_republic_congress']['en_desc'] += ' Delegations from Ukraine, Georgia and Kazakhstan subsequently present specific demands.'
    by_id['sr_lito_balkan_partnership']['reward'] += '\nsr_story_balkan_contacts_effect = yes'
    by_id['sr_lito_balkan_partnership']['de_desc'] += ' Ein anschließender Briefwechsel prüft, wie ernst wir es mit der Gleichberechtigung meinen.'
    by_id['sr_lito_balkan_partnership']['en_desc'] += ' A subsequent exchange of letters tests our commitment to equality.'
