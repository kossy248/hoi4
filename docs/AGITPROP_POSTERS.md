# Agitprop-Poster in der originalen Oberfläche

Seit 0.6.0 sind die drei gelieferten Poster aus **Agitprop.rar** an die
originale sowjetische GUI angebunden. Die Originale liegen unverändert in
`artwork/agitprop/originals/`; Zuordnung, Abmessungen und SHA-256-Prüfsummen stehen
in `artwork/agitprop/manifest.json`.

| Geliefertes Motiv | Originale Kampagne | Native ID | Textur |
| --- | --- | ---: | --- |
| Lito, Volk, Partei und Einheit | `SOV_propaganda_hit_of_hammer` | 7 | `sr_agitprop_star.dds` |
| Vier Genossen und Minecraft-Motiv | `SOV_propaganda_high_yield` | 11 | `sr_agitprop_peoples.dds` |
| Soldat, Stärke, Ehre und Sieg | `SOV_propaganda_motherland_calls` | 3 | `sr_agitprop_light.dds` |

Die Bilder verwenden 150×200 Pixel, DDS/DXT5. Sie sind proportional mit
transparenten Seitenrändern eingepasst; Texte und Rahmen werden nicht
abgeschnitten. Der Installer übernimmt die originale Position und den
Vanilla-Tooltip. Während eines eigenen Bilds wird die darunterliegende
Originalgrafik ausgeblendet. Native Hintergrundbilder und Countdowntexte
bleiben bestehen. Die eigenen Bilder werden unverändert angezeigt; es werden
keine neuen gealterten Bildfassungen erzeugt.

`python3 tools/build_agitprop_posters.py` erzeugt die drei Texturen mit
ImageMagick erneut aus den gesicherten Originalen. Die fünf übrigen alten
Bildplätze sind unbenutzte Platzhalter und werden nicht als eigene Kampagnen
aktiviert. Weitere gelieferte Poster können später ebenso zugeordnet werden.

Die Freischaltung erfolgt über **„Agitprop der Völker“** und die anschließenden
Räte-/Akademie-Meilensteine. Kosten, Dauer, Kampagnenboni und Ablauf bleiben
Vanilla. Siehe [native Anbindung](NATIVE_AGITPROP.md).

## Frühere Titel- und Bonusentwürfe (nicht aktiv)

Die folgende Tabelle hält die früheren acht eigenen Entwürfe fest. Sie
beschreibt keine aktuellen Decisions und ersetzt die Vanilla-Boni nicht.

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
