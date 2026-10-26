# Agitprop: Entwürfe für die originalen Posterplätze

Die bisherige eigenständige Entscheidungskategorie mit einem wechselnden Bild
ist seit **0.5.3 entfernt**. Sie war keine Anbindung an die originalen drei
Agitprop-Posterplätze. Es gibt derzeit noch keinen eingebauten nativen Ersatz.

Die acht Titel und Bonusentwürfe bleiben als Designvorlage erhalten. Die Motive
werden später vom Nutzer geliefert. Als Quellen eignen sich **3:4**-Bilder,
beispielsweise 600 × 800 Pixel. Die bisherigen 150 × 200 DDS/DXT5-Platzhalter
liegen weiterhin vor, sind aber nicht an eine aktive Oberfläche gebunden.

Die endgültigen Frame-IDs, Texturdateien, Freischaltungen und die mögliche
gleichzeitige Belegung werden anhand der vollständigen Original-GUI und ihrer
Effekte verbunden. Die bisherige Beschränkung auf eine Kampagne wird nicht als
vorgebliches Originalsystem weitergeführt. Auch die folgenden Kosten und
Laufzeiten sind Entwürfe, keine derzeit auswählbaren Entscheidungen.

| Titel | Politische Macht | Dauer | Boni und Freischaltung | Bilddatei |
| --- | ---: | ---: | --- | --- |
| Solange ein Stern über uns brennt | 70 | 180 Tage | Stabilität +4 Prozentpunkte; Kriegsunterstützung +3 Prozentpunkte. Fokus: `sr_lito_congress`. | `sr_agitprop_star.dds` |
| Elf Völker – ein gemeinsamer Morgen | 75 | 180 Tage | Stabilität +4 Prozentpunkte; tägliche politische Macht +0,05. Zusätzlich +5 Vertrauen und +0,02 Unionsbalance. Fokus: `sr_lito_republic_congress`. | `sr_agitprop_peoples.dds` |
| Aus Stahl wird Zukunft | 90 | 180 Tage | Fabrikausstoß +6 %; Baugeschwindigkeit +3 %. Fokus: `sr_lito_federal_plan`. | `sr_agitprop_steel.dds` |
| Die Räte vergessen nicht | 75 | 180 Tage | Fabrikausstoß +3 %; Stabilität +3 Prozentpunkte. Zusätzlich +6 Vertrauen; aktive Republiken verlieren je 5 Widerstand. Fokus: `sr_lito_workers_councils`. | `sr_agitprop_councils.dds` |
| Kein Himmel gehört den Tyrannen | 80 | 180 Tage | Luftmissionseffizienz +4 %; Luftunfälle −5 %. Fokus: `sr_lito_air_command`. | `sr_agitprop_sky.dds` |
| Unser Morgen kennt keine Grenzen | 80 | 180 Tage | Forschungsgeschwindigkeit +4 %. Fokus: `sr_lito_technical_education`. | `sr_agitprop_horizon.dds` |
| Die Erde gehört den Arbeitenden | 85 | 180 Tage | Unterhaltskosten verbesserter Beziehungen −20 %; tägliche politische Macht +0,10. Nur im Frieden verfügbar. Fokus: `sr_lito_balkan_partnership`. | `sr_agitprop_earth.dds` |
| Für die Union bis zum letzten Licht | 90 | 90 Tage | Erholungsrate des Heeres +6 %; Kriegsunterstützung +5 Prozentpunkte; Nachschubverbrauch −3 %. Nur im Krieg verfügbar. Fokus: `sr_lito_army_homeland_defence`. | `sr_agitprop_light.dds` |

Die acht ungebundenen Dateien liegen unter
`soviet_renewal/gfx/interface/agitprop/`. Die alte Registrierung
`interface/sr_agitprop_icons.gfx` und ihre Decision-Icons wurden entfernt.

Für den Originalabgleich erstellt `collect_lito_agitprop.ps1` lokal einen
Textbericht mit den passenden Spielquellen. Der Bericht wird nicht automatisch
übertragen. Siehe [NATIVE_AGITPROP.md](NATIVE_AGITPROP.md).

Die Unionsrats-Erweiterung ergänzt acht Aktionen im bestehenden Balance-Menü:
Delegiertenkongress, Krisenkompromiss, öffentliche Planprüfung, einmalige
zentrale Kriegsvollmacht, Amnestie, Haushaltsreserve anlegen, Reserve auslösen
und gemeinsamer Kriegsrat. Ihre Kosten und zeitlich begrenzten Nachteile sind
in den Entscheidungstexten angegeben. Die Reserve gibt beim Anlegen keinen
Sofortbonus und kann nur einmal während einer Krise freigegeben werden.
