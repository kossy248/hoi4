# Grafiken und Bildplätze — 0.5.6

Die Mod verwendet rotes Emaille, gealtertes Gold und dunkles Metall für ihre
Abzeichen. Führerporträt, Flagge und die drei Entscheidungsbilder wurden auf
Grundlage der bereitgestellten Vorlagen aufbereitet.

## Fokus- und Balance-of-Power-Abzeichen

Unter soviet_renewal/gfx/interface/goals liegen 78 eigene Fokusmotive. Die
erweiterten 102 Schwerpunkte verwenden diese Motive thematisch erneut; die Zahl
der Foki ist deshalb größer als die Zahl der unterschiedlichen Fokusbilder.
Zwei weitere DDS-Dateien unter gfx/interface/bop zeigen Einbruch und Erhaltung.

Die Abzeichen sind 95 × 85 Pixel groß, besitzen Transparenz und verwenden DXT5.
Die Registrierung liegt in interface/sr_focus_icons.gfx. Die ursprünglichen
Motive und ihre Atlaspositionen stehen in tools/gfx_plan.json; die Zuordnung
zusätzlicher Foki folgt dem Fokusdatenmodell.

Die fünf Quellatlanten liegen in artwork/atlases, die einzelnen hochauflösenden
PNG-Dateien in artwork/focus_icons. Änderungen an einer Textur müssen Pfad und
Sprite-Verweis beibehalten oder beide gemeinsam aktualisieren.

## Icons aller Decisions und Kategorien

Alle **48 Decisions und Missionen** sowie **fünf Kategorien** besitzen einen
eigenen Icon-Schlüssel. Ihre **53 vollständigen Sprite-Blöcke** stehen zusammen
in `soviet_renewal/interface/sr_decision_icons.gfx`:

```text
spriteTypes = {
    spriteType = {
        name = "GFX_decision_sr_proclaim_slavic_union"
        texturefile = "gfx/interface/decisions/icons/focus_LITO_experts_in_camouflage.dds"
    }
    spriteType = {
        name = "GFX_decision_category_sr_formable_union"
        texturefile = "gfx/interface/decisions/icons/focus_LITO_experts_in_camouflage.dds"
    }
    spriteType = {
        name = "GFX_sr_category_focus_LITO_experts_in_camouflage"
        texturefile = "gfx/interface/decisions/focus_LITO_experts_in_camouflage_category.dds"
    }
}
```

In der Decision steht dazu `icon = sr_proclaim_slavic_union`, in ihrer
Kategorie `icon = sr_formable_union`. Das Spiel ergänzt bei Icons das jeweilige
Präfix `GFX_decision_` oder `GFX_decision_category_`. Direkte `picture`-Verweise
verwenden dagegen den vollständigen Sprite-Namen.

Für jedes Icon lässt sich `texturefile` einzeln austauschen. Der Sprite-Name
bleibt dabei bestehen. Unionsgespräche verwenden das Republikkongressmotiv,
Regierungsprojekte Werkstätten, Bildung oder Versorgung; Innenpolitik und
Unionspolitiken verwenden passende Motive des Fokusbaums. Diese Texturen
werden bewusst mehrfach verwendet. Es sind keine 53 neuen Zeichnungen.

Die **48 kleinen Decision-Symbole** verwenden seit 0.5.5 separate Texturen
unter `gfx/interface/decisions/icons/`: **32 × 32 Pixel**, DDS/DXT5, ohne
Mipmaps. Das vollständige Motiv wird proportional in 28 × 28 Pixel eingepasst
und auf der transparenten Fläche zentriert. So ragt es nicht über die Zeile.
Die 18 Motive werden weiterhin thematisch mehrfach verwendet.

Seit 0.5.6 verwenden auch die **fünf Kategorie-Symbole in den Überschriften**
die kleinen 32 × 32-Versionen. Die früheren Kategorie-Aliase verweisen ebenfalls
darauf. Die separaten großen `picture`-Sprites `GFX_sr_category_*` behalten
ihre 100 × 100 Pixel großen Bilder. So passt das Symbol auch in die
eingeklappte Kopfzeile, während das große Bild in der geöffneten Kategorie
erhalten bleibt.

`tools/build_decision_icons.py` erzeugt diese Dateien aus den vorhandenen
PNG-Quellen, ersatzweise aus den bisherigen DDS-Dateien. Gemeinsame
Fokusgrafiken und große Kategorie-Bilder werden dabei nicht überschrieben.

Die acht Agitprop-Decision-Icons und die eigene Agitprop-Kategorie wurden mit
der bisherigen Nachbildung entfernt; ihre Poster-Registrierung ist gelöscht.
Die älteren Namen der drei gelieferten Entscheidungsbilder bleiben als Aliase
in `sr_lito_decision_icons.gfx` verfügbar. Generische Spielsprites werden
dabei nicht überschrieben.

## Die drei gelieferten Entscheidungsbilder

Die gewünschten Namen sind als eigene Grafiken vorhanden:

| Name | Motiv | Verwendung |
| --- | --- | --- |
| decision_LITO_eastern_europe | Globus mit Handschlag | Meinungs- und Einflussentscheidungen |
| focus_LITO_the_molotov_line | Balkankarte, Kranz und Länderbänder | Balkanentscheidungen |
| focus_LITO_experts_in_camouflage | Karte, Raketen und Kreml | Formierungsentscheidungen |

Die Dateien liegen unter soviet_renewal/gfx/interface/decisions:

- Der jeweilige Grundname endet auf .dds und ist 95 × 85 Pixel groß.
- Die zusätzliche Variante mit dem Suffix _category.dds ist 100 × 100 Pixel groß.
- Die kleinen Decision-Versionen liegen im Unterordner `icons` und sind
  32 × 32 Pixel groß. Der gleichnamige Grundpfad bleibt unverändert erhalten.
- Beide Varianten verwenden DXT5 mit Transparenz und passen das vollständige
  Motiv ohne Streckung ein.

Die hochauflösenden PNG-Quellen und der gemeinsame transparente Atlas liegen
unter artwork/decisions. Die Gameplay-Voraussetzungen der Entscheidungen
werden durch die neuen Bilder nicht geändert.

## Ereignisbilder

Drei Szenen ergänzen die politischen Texte: Ratssitzung, Werkstatt und
Balkankonferenz. Ihre DDS-Dateien unter gfx/event_pictures heißen
sr_campaign_council.dds, sr_campaign_workshops.dds und sr_campaign_balkan.dds.
Sie verwenden 450 × 150 Pixel, DXT5 und keine Mipmaps.

Die Quellen liegen unter artwork/events. Das Fokusbauprogramm registriert die
Sprite-Namen in interface/sr_campaign_event_pictures.gfx und ordnet die Bilder
den thematisch passenden Ereignisdateien zu.

## Agitprop-Poster

Die acht geplanten Kampagnen besitzen ungebundene Texturdateien; die bisherige
Einzelbild-Kategorie wurde entfernt. Drei gelieferte Poster aus `Agitprop.rar`
ersetzen inzwischen die Bildplätze `star`, `peoples` und `light`. Die anderen
fünf Motive sind noch Platzhalter. Titel, Quellnamen und Bonusentwürfe stehen in
[AGITPROP_POSTERS.md](AGITPROP_POSTERS.md).

Für eigene Poster sind PNG-Quellen im Verhältnis **3:4** vorgesehen,
beispielsweise 600 × 800 Pixel. Die Spieltexturen verwenden **150 × 200 Pixel**
und DDS/DXT5. Das sind vorläufige Dateiformate der bisherigen Quellen. Die
endgültige Sprite-/Atlas-Zuordnung für die originale Anzeige ist noch offen und
wird erst anhand der Originaldateien festgelegt. Zunächst nur im installierten
Modordner ersetzte Bilder vor dem nächsten Update in das Quellpaket übernehmen.

Die drei neuen Original-PNGs liegen in `artwork/agitprop/originals`.
`artwork/agitprop/manifest.json` hält ihre vorläufige Zuordnung und
Prüfsummen fest. `tools/build_agitprop_posters.py` passt das vollständige Bild
proportional auf die vorbereitete Texturfläche ein. Texte, Rahmen und Motive
werden weder abgeschnitten noch neu gezeichnet. Die native Anbindung ist
weiterhin offen; die gelieferten Bilder sind für den nächsten Einbau vorbereitet.

## Porträts

Litos eigenes Porträt liegt als
gfx/leaders/SOV/Portrait_SOV_cosif_kozs_lito.dds vor: 156 × 210 Pixel, DXT5,
keine Mipmaps. Die hochauflösende Quelle ist artwork/portraits/lito.png.
interface/sr_custom_portraits.gfx verbindet es mit GFX_sr_lito_portrait.

Der Installer erhält vorhandene Sprite-Definitionen und ergänzt nur fehlende
Porträts. Die fehlenden Verweise landen in interface/sr_lito_portrait.gfx;
existiert diese Datei bereits im Quellpaket, wird
sr_generated_portrait_fallbacks.gfx verwendet.

Die drei unterstützten Namen sind:

- GFX_sr_lito_portrait für Cosif Kozs Lito;
- GFX_sr_balkan_council_portrait für den Föderalen Volksrat;
- GFX_sr_kardelj_portrait für Edvard Kardelj.

Für Kardelj sucht der Installer im lokalen Spielordner gfx/leaders/YUG nach
einer DDS-Datei mit kardelj im Namen. Andernfalls erhalten Kardelj und der
Volksrat ein tatsächlich vorhandenes generisches Europa-Porträt. Lokale
Spielgrafiken werden dafür angebunden und nicht in das Quellpaket veröffentlicht.

## Formierungsflagge

Die Slawische Union verwendet die bereitgestellte blau-weiß-rote Flagge mit
dem gold-roten Wappen. Ihre Quelle liegt unter artwork/flags/SOV_LITO_SFSU.png.

Jeweils SOV_LITO_SFSU.tga und SOV_LITO_SFSU_communism.tga liegen in:

- gfx/flags: 82 × 52 Pixel;
- gfx/flags/medium: 41 × 26 Pixel;
- gfx/flags/small: 10 × 7 Pixel.

Alle sechs Dateien sind unkomprimierte 24-Bit-RGB-TGA ohne Alpha. Beide
Namensvarianten enthalten dasselbe Motiv. Die Proklamation setzt das kosmetische
Tag SOV_LITO_SFSU und aktiviert dadurch die neue Flagge. Vorher bleibt die
sowjetische Flagge erhalten; es wird keine SOV.tga ersetzt.

Nur YUG_LITO_BALKAN verwendet vorerst noch die lokal vorhandene jugoslawische
Flagge als Platzhalter, ebenfalls in drei Größen und zwei Namensvarianten.
Quellseitig bereits mitgelieferte eigene Flaggen werden nicht überschrieben.
