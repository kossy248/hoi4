# Eigene Agitprop-Poster in der originalen Oberfläche

Seit 0.6.1 verwendet Litos Agitprop ausschließlich die drei gelieferten Poster
aus **Agitprop.rar** und drei eigene Kampagnen. Die originale sowjetische
Drei-Platz-Oberfläche mit Kostenmechanik, Countdown und Rücksetzung bleibt
erhalten. Vanilla-Kampagnen und deren Postermotive sind unter Lito ausgeblendet.

Die Originalbilder liegen unverändert in `artwork/agitprop/originals/`;
Abmessungen und SHA-256-Prüfsummen stehen in `artwork/agitprop/manifest.json`.

| Geliefertes Motiv | Eigene Kampagne | Native Frame-ID | Textur |
| --- | --- | ---: | --- |
| Lito, Volk, Partei und Einheit | Solange ein Stern über uns brennt | 7 | `sr_agitprop_star.dds` |
| Vier Genossen und Minecraft-Motiv | Elf Völker – ein gemeinsamer Morgen | 11 | `sr_agitprop_peoples.dds` |
| Soldat, Stärke, Ehre und Sieg | Für die Union bis zum letzten Licht | 3 | `sr_agitprop_light.dds` |

Die Frame-IDs und Kostenvariablen der bisherigen Vanilla-Zuordnungen werden für
die native Mechanik weiterverwendet. Die ursprünglichen Kampagnen werden unter
Lito nicht mehr angeboten. Die Kampagnen besitzen eigene Texte und Boni:

| Kampagne | Boni während der Laufzeit |
| --- | --- |
| Solange ein Stern über uns brennt | Stabilität +4 Prozentpunkte; Kriegsunterstützung +3 Prozentpunkte |
| Elf Völker – ein gemeinsamer Morgen | Stabilität +4 Prozentpunkte; täglich +0,05 politische Macht; beim Start +5 Vertrauen und +0,02 Unionsbalance |
| Für die Union bis zum letzten Licht | Erholungsrate des Heeres +6 %; Kriegsunterstützung +5 Prozentpunkte; Nachschubverbrauch −3 % |

Alle drei laufen 180 Tage mit anschließend 90 Tagen Abklingzeit und sind im
Frieden wie im Krieg verfügbar. Sie kosten anfangs jeweils 15 politische Macht;
die Kosten der betreffenden Kampagne verdoppeln sich nach ihrem Ablauf.

Die Bilder verwenden 150×200 Pixel, DDS/DXT5. Sie sind proportional mit
transparenten Seitenrändern eingepasst; Texte und Rahmen werden nicht
abgeschnitten. Der Installer übernimmt die originale Position und ergänzt
Tooltips mit den eigenen Titeln und Boni. Der native Hintergrund sowie leere und gesperrte Plätze bleiben
sichtbar. Es entstehen keine neu gezeichneten oder gealterten Bildfassungen.

`python3 tools/build_agitprop_posters.py` erzeugt die drei Texturen mit
ImageMagick erneut aus den gesicherten Originalen. Die fünf übrigen alten
Bildplätze bleiben unbenutzt. Weitere Poster werden erst ergänzt, wenn der
Nutzer sie fertig hat.

Die Freischaltung erfolgt über **„Agitprop der Völker“**, der zweite und dritte
Platz über die Räte-/Akademie-Meilensteine. Bereits laufende Vanilla-Kampagnen
aus älteren Spielständen laufen ohne Abbruch aus; ihre alten Motive bleiben
ausgeblendet. Details: [native Anbindung](NATIVE_AGITPROP.md).
