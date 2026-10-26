# Originales Agitprop: belegter Stand und fehlende Quellen

Die bisherige Einzelbild-Nachbildung wurde in 0.5.3 entfernt. Die nächste
Anbindung soll die originalen drei Posterplätze verwenden. Ein funktionsfähiger
Ersatz ist noch nicht eingebaut.

Die vom Nutzer bereitgestellte Vorlage beginnt mit `SOV_propaganda_campaigns`
und zeigt 23 vollständige Kampagnen sowie vier Debug-Decisions. Sie endet mitten
in `SOV_propaganda_happy_life.available`. Diese abgeschnittene Vorlage wird nicht
als gültige Spieldatei übernommen und ihre fehlenden Klammern werden nicht
geraten.

## Aus der Vorlage belegte Schnittstellen

- Slotprüfung: `SOV_propaganda_poster_slot_available`.
- Start: `SOV_new_propaganda_campaign = <ID>` und
  `SOV_pick_propaganda_campaign_slot_effect = yes`.
- Ende: dieselbe ID in `SOV_propaganda_campaign_to_remove`, danach
  `SOV_reset_propaganda_campaign_slot_effect = yes`.
- Zeitfelder: `days_remove = SOV_default_propaganda_campaign_duration` und
  `days_re_enable = SOV_default_propaganda_campaign_cooldown`.
- Kosten kommen aus einer kampagnenspezifischen Variable. Die Originalroutine
  `SOV_increase_propaganda_campaign_cost_effect` erhöht sie über die temporäre
  Variable `SOV_propaganda_cost`. Die tatsächliche Formel ist nicht enthalten.
- Die Anzeige verwendet `SOV_poster_left_icon_frame`,
  `SOV_poster_center_icon_frame` und `SOV_poster_right_icon_frame`.
- Der gesperrte Frame wird über `SOV_propaganda_locked_slot_index` bestimmt.
  Sein numerischer Wert sowie der leere Frame sind noch nicht belegt.

## Benötigte Originalquellen

Es fehlen die vollständige Kategorie- und Kampagnendatei, die Definitionen der
genannten Effekte und Trigger, die Initialisierung der Slot-/Zeit-/Kostenwerte
sowie die zugehörigen Scripted-GUI-, `.gui`- und `.gfx`-Definitionen. Ohne diese
Quellen wären sichtbare Poster, Frame-Zuordnung, Slotfreischaltung und korrekte
Rücksetzung nicht verlässlich angebunden.

`collect_lito_agitprop.ps1` sucht diese Quellen anhand der belegten Symbole und
der zugehörigen GUI-/Sprite-Verweise in der lokalen Installation. Es erstellt
einen neuen UTF-8-Bericht mit relativen Pfaden, Prüfsummen und vollständigen
gefundenen Quelltexten. Fehlende Treffer oder Lesefehler werden ausgewiesen.
Der Bericht ist Diagnosematerial, kein Nachweis einer fertigen Integration.

Die Originale bleiben lokal unverändert. Das Skript liest keine Spielstände,
Kontodaten oder Zugangsdaten und lädt den Bericht nicht hoch. Er kann danach
als Datei im Chat angehängt werden; nicht nur einen Ausschnitt hineinkopieren.
Originalquellen werden nicht in das öffentliche Mod-Repository übernommen.

Die acht eigenen Kampagnentitel und Bonusentwürfe stehen in
[AGITPROP_POSTERS.md](AGITPROP_POSTERS.md). Ihre endgültige Umsetzung folgt
dem Originalvertrag, sobald die fehlenden Dateien vorliegen.
