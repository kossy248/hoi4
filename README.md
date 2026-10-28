# Sowjetunion: Litos Union — 0.6.1

Eine alternative Sowjetunion unter **Cosif Kozs Lito**, einem fiktiven, von Josip
Broz Tito inspirierten Staatsführer mit jugoslawischen Wurzeln. Lito blieb nach
der Revolution in Russland. Sein **Titoismus** gehört zur Hauptideologie
Kommunismus und verbindet Arbeiterselbstverwaltung, föderale Mitsprache und
außenpolitische Eigenständigkeit.

Die Geschichte steht in [LORE.md](LORE.md), die Änderungen in
[docs/CHANGELOG_0.6.1.md](docs/CHANGELOG_0.6.1.md), der vollständige Fokusbaum in
[docs/FOKUSBAUM.md](docs/FOKUSBAUM.md).

## Inhalt

- **102 Schwerpunkte:** Regierung, Republiken, Industrie, Forschung, Heer,
  Luftwaffe, Marine und Balkanpolitik. Die 24 neuen Schwerpunkte erweitern
  Politik, Industrie und militärische Politik um je acht Ziele. Die bisherigen
  vier gegenseitigen Kursentscheidungen bleiben erhalten.
- **71 Ereignisdefinitionen mit Folgewirkungen:** erste hundert Tage,
  Republikforderungen, Werkversammlungen, Forschungsfreiheit, Kriegsrechte, Kardeljs
  Verhandlungen und die Verfassung der späteren Slawischen Union.
- **Drei aktive Regierungsprojekte** mit Zwischenentscheidungen, sichtbaren
  Fristen und Abschlussbedingungen im Fokusbaum.
- **Agitprop mit drei eigenen Kampagnen und Postern:** „Agitprop der Völker“
  öffnet die native Kategorie mit ihrem ersten Posterplatz. Räte und Akademien
  ergänzen die zwei weiteren Plätze. Oberfläche, Kostensteigerung, Ablauf und
  Rücksetzung stammen aus dem lokalen Vanilla-Spiel; Titel und Boni sind Litos
  eigene. Vanilla-Kampagnen und ihre Poster werden unter Lito ausgeblendet.
- **Unionsbalance und Republikwiderstand:** fünfzehn registrierte Republiken,
  örtliche Räte, Streiks, Sabotage und acht zusätzliche politische Maßnahmen.
- **Balkanpolitik:** kommunistische Parteien beeinflussen, Regierungen
  unterstützen und fünf kommunistische Balkanstaaten als gemeinsamen
  sowjetischen Marionettenstaat vereinigen.
- **Agentur-Operation „Roter Morgen“:** Ein erfolgreicher Abschluss setzt die
  Zielregierung direkt auf Kommunismus. Die Operation hat keine
  Länder-Whitelist und benötigt die Agenturmechanik von La Résistance.
- **Abschaltung erkannter historischer Paranoia-/Trotzki-Inhalte** durch
  versionsabhängige Kopien und Schutzbedingungen aus der lokalen Installation.
- Litos eigenes Porträt, Kardelj statt Tito in einem kommunistischen
  Jugoslawien, die eigene Formierungsflagge und die drei gewünschten
  Entscheidungsabzeichen.

## Litos Regierung und spätere Kapitel

Das Fenster **„Fortgesetzte Schwerpunkte“** hat seit 0.5.4 eine eigene Position
mit Abstand unter der letzten Fokusreihe. Die normale Fokusfläche wird dadurch
freigehalten. Die genaue Darstellung hängt von der Spieloberfläche ab und muss
noch in HOI4 geprüft werden.

Das politische Vertrauen startet bei **50 von 100**. Ereignisse am Anfang sowie
nach 30 und 60 Tagen behandeln Räte, Parteizentrale und Kompromisse. Nach 100
Tagen folgt eine Bilanz mit unterschiedlichen Ergebnissen. Schnelle politische
Macht kann Vertrauen kosten; Mitsprache beansprucht Mittel und Verwaltung.

Der Republikkongress eröffnet drei auswählbare Zusagen mit sichtbarem Countdown:

| Republik | Zusage | Frist | Kosten bei Erfüllung |
| --- | --- | ---: | ---: |
| Ukraine | Eine Zivilfabrik auf kontrolliertem ukrainischem Kerngebiet | 180 Tage | 65 politische Macht |
| Georgien | Kulturelle Autonomie absichern | 150 Tage | 65 politische Macht |
| Kasachstan | Infrastruktur auf kontrolliertem kasachischem Kerngebiet | 210 Tage | 90 politische Macht |

Bauvorhaben benötigen geeignete freie Bauplätze. Erfüllung stärkt Vertrauen und
senkt örtlichen Widerstand, bindet aber vorübergehend Haushalt oder Produktion.
Gebrochene Zusagen schwächen Vertrauen und erhöhen den Widerstand. Verliert
eine Republik ihre Vertretung, endet ihre Mission ohne Friststrafe.

Die spätere Geschichte greift die tatsächlichen Entscheidungen wieder auf:
Räte streiten mit der Parteizentrale, erfüllte und gebrochene Republikzusagen
führen zu unterschiedlichen Anhörungen, und ein Krieg stellt Litos
Mitspracherechte auf die Probe. Automatische Starts dieser späteren Kapitel
teilen sich eine **60-Tage-Sperre**; vorab angekündigte Folgeberichte und selbst
gewählte Projekte haben ihre eigenen Termine.

Nach den ersten hundert Tagen stehen drei einmalige Regierungsprojekte offen.
Es kann nur eines gleichzeitig laufen:

| Projekt | Einstieg | Frist | Abschluss |
| --- | --- | ---: | --- |
| Werkstattreform | Arbeiterräte abgeschlossen; 75 politische Macht | 240 Tage | Zwischenentscheidung, regionale Werkstätten und weitere 25 politische Macht |
| Volksbildungsnetz | Akademien vernetzt; 60 politische Macht | 270 Tage | Zwischenentscheidung, technische Bildung und weitere 40 politische Macht |
| Versorgungsprogramm | Heeresnachschub oder Nachschubkorridore; 60 politische Macht | 240 Tage | Zwischenentscheidung, beide Nachschubfoki und weitere 40 politische Macht |

Nach 90 Tagen folgt jeweils eine Zwischenentscheidung. Abschluss und
Fristversäumnis haben unterschiedliche Folgen; die laufende Finanzierung wird
beim Ende des betreffenden Projekts beendet.

## Agitprop

Der **35-Tage-Fokus „Agitprop der Völker“** folgt auf „Ein Mandat für Lito“.
Er verwendet die bisherige Fokus-ID der Kaderschulen und behält deren Bonus
von täglich 0,05 politischer Macht. Nach Abschluss erscheint die originale
sowjetische Agitprop-Kategorie mit ihrem ersten Posterplatz.

| Schwerpunkt | Agitprop-Freischaltung |
| --- | --- |
| Agitprop der Völker | Erster Platz und die drei eigenen Kampagnen |
| Räte in den Betrieben | Zweiter Platz |
| Die Akademien vernetzen | Dritter Platz |

Die beiden ergänzenden Plätze werden erst nach dem Agitprop-Fokus verfügbar.
Bereits abgeschlossene Meilensteine werden dabei berücksichtigt. Bestehende
Spielstände erhalten die vorbereitete Freischaltung spätestens am nächsten
Spieltag; laufende Kampagnen, ihre Kosten und Zähler werden erhalten.

Die Mechanik verwendet **Vanilla-Effekte und die originale Oberfläche**:
180 Tage Laufzeit, anschließend 90 Tage Abklingzeit und zunächst 15 politische
Macht pro Kampagne. Die Kosten der jeweiligen Kampagne verdoppeln sich nach
Ablauf. Alle drei Kampagnen sind im Frieden und Krieg verfügbar, benötigen einen
freien Platz und können jeweils nur einmal gleichzeitig laufen.

| Eigene Kampagne | Boni während der Laufzeit |
| --- | --- |
| Solange ein Stern über uns brennt | Stabilität +4 Prozentpunkte; Kriegsunterstützung +3 Prozentpunkte |
| Elf Völker – ein gemeinsamer Morgen | Stabilität +4 Prozentpunkte; täglich +0,05 politische Macht; beim Start +5 Vertrauen und +0,02 Unionsbalance |
| Für die Union bis zum letzten Licht | Erholungsrate des Heeres +6 %; Kriegsunterstützung +5 Prozentpunkte; Nachschubverbrauch −3 % |

Jede Kampagne zeigt genau eines der drei gelieferten Poster. Texte, Motive und
Ränder bleiben erhalten. Der native Hintergrund und Countdown bleiben bestehen;
die 24 Vanilla-Kampagnen, Debug-Auswahlen und Vanilla-Postermotive erscheinen
unter Lito nicht mehr. Leere und gesperrte Plätze behalten ihre nativen Anzeigen.
Bereits laufende Vanilla-Kampagnen aus älteren Spielständen laufen ohne Abbruch
aus, ihre Postermotive werden dabei ausgeblendet. Die nativen Alterungsereignisse
laufen weiter, erzeugen aber keine neu gezeichneten Fassungen deiner Bilder.
Details: [Posterzuordnung](docs/AGITPROP_POSTERS.md).

Der Installer prüft die Originaldateien und bereitet nur lokale Modkopien vor.
Erscheint **„Originales Agitprop vorbereitet“**, ist die Anbindung eingerichtet.
Bei nicht unterstützten oder fehlenden Originaldateien nennt er den Grund und
lässt den Agitprop-Fokus gesperrt. Nach einem HOI4-Update den Installer erneut
benutzen. Deine Spielinstallation wird nicht verändert.

## Unionsrat und Balance of Power

Die gemeinsame Balance **Einbruch der Union ↔ Erhaltung der Union** reicht von
−1 bis +1 und startet bei +0,15. Elf Republiken gehören zur vorgezogenen
Föderalreform von 1936: Russland, Ukraine, Belarus, Georgien, Armenien,
Aserbaidschan, Kasachstan, Usbekistan, Turkmenistan, Kirgisistan und Tadschikistan.
Estland, Lettland, Litauen und Moldau werden nur bei tatsächlichem sowjetischem
Besitz ihrer entsprechenden Kerngebiete vertreten. Besetzung allein genügt
nicht.

Ein Republikrat kostet **35 politische Macht**, gibt **+0,03 Balance**, senkt den
örtlichen Widerstand um **15** und schützt die Republik **180 Tage** vor ihrem
Vernachlässigungsbeitrag. Der monatliche Grunddruck beträgt −0,005; jede
vertretene Republik ohne aktuellen Rat trägt weitere −0,002 bei. Krieg und
Stabilität unter 40 % geben jeweils −0,01, Stabilität über 60 % gibt +0,01.

Acht zusätzliche Maßnahmen stehen im selben Unionsrat zur Verfügung:
Delegiertenkongress, Notfallkompromiss, öffentliche Planprüfung, zentrale
Krisenvollmachten, Republikamnestie, Haushaltsreserve, Freigabe der Reserve und
gemeinsamer Kriegsrat. Sie unterscheiden sich nach Frieden oder Krieg,
Vertrauen und Krisenlage. Vorteile haben politische, wirtschaftliche oder
föderale Kosten; die Krisenvollmachten sind einmalig und verschieben die
Balance zur Seite des Einbruchs.

Jede vertretene Republik besitzt eigenen Widerstand von 0 bis 100:

| Balancezustand | Widerstandsänderung pro Monat |
| --- | ---: |
| Unter −0,60 | +10 |
| Über +0,20 | −5 |
| Dazwischen | −2 |

Ab 50 Widerstand in mindestens einer Republik entstehen Massenstreiks, ab 80
Sabotagenetzwerke und monatliche Infrastrukturschäden in passendem eigenem,
kontrolliertem Kerngebiet. Die landesweiten Mali stapeln sich nicht pro
Republik und verschwinden nach ausreichender Erholung; entstandene Schäden
müssen repariert werden. Das System entfernt keine sowjetischen Kerne und
erklärt keine automatischen Unabhängigkeiten.

## Balkanpolitik und Formierung

Fünf Einflusslinien betreffen **Jugoslawien, Albanien, Bulgarien, Griechenland
und Rumänien**. Nach dem jeweiligen Länderschwerpunkt kostet eine wiederholbare
Kampagne 50 politische Macht, erhöht kommunistische Unterstützung um acht
Prozentpunkte und legt ein 365-Tage-Netzwerk an; Wiederholung nach 180 Tagen.
Ab 60 % Unterstützung kann für 75 politische Macht eine kommunistische
Regierungsbildung unterstützt werden. Diese Entscheidungen richten sich an
geeignete, friedliche KI-Staaten ohne fremden Oberherrn.

Ein kommunistisches Jugoslawien erhält **Edvard Kardelj** anstelle Titos.
Kardelj verfolgt in den späteren Ereignissen eigene politische Interessen.
Lito bleibt sowjetischer Führer; der Föderale Volksrat des gemeinsamen
Balkanstaats bleibt von der Kardelj-Ersetzung ausgenommen.

Nach dem kooperativen Balkanabschluss können die fünf friedlichen
kommunistischen Staaten für 100 politische Macht zur **Sozialistischen
Balkanföderation** vereinigt werden. YUG ist ihr technischer Host, der Föderale
Volksrat ihre Regierung und SOV ihr Oberherr. Fraktionsführer und fremde
Untertanen sind ausgeschlossen. Nur passende, bereits eigene Gründergebiete
erhalten zusätzliche jugoslawische Kerne. Spätere Verfassungs- und
Haushaltskonflikte reagieren auf Mitsprache oder sowjetische Kontrolle.

Die **Sozialistische Föderale Slawische Union** benötigt direkten sowjetischen
Besitz und Kontrolle aller derzeit definierten Kerngebiete von Polen,
Jugoslawien, Albanien, Bulgarien, Griechenland, Rumänien und der gesamten
Türkei. Verbündete, Marionetten und reine Besetzung reichen nicht. Eine
vorherige Eingliederung der bezeichneten Balkanföderation kostet 150 politische
Macht und verlangt Frieden sowie direkten Besitz und Kontrolle der polnischen
und türkischen Kerne.

Die eigentliche Ausrufung kostet 100 politische Macht. Sie setzt Staatsname und
eigene Flagge über das kosmetische Tag SOV_LITO_SFSU und gibt +5 Prozentpunkte
Stabilität sowie +0,10 Unionsbalance. Das Länder-Tag bleibt SOV. Die Ausrufung
erobert nichts und vergibt selbst keine zusätzlichen Kerne.

## Agentur-Operation „Roter Morgen“

Mit **La Résistance**, einer eigenen Agentur und einem Netz im Zielstaat kann
Lito eine weltweite Operation vorbereiten:

- zwei Operative, 90 Tage Laufzeit und 50 Netzwerkstärke;
- 75 politische Macht, 1.000 Infanteriewaffen und fünf Zivilfabriken für 30 Tage;
- drei Phasen mit Kontaktaufnahme, der erzählten Infiltration des
  Regierungsgebäudes und der Proklamation einer sozialistischen Regierung.

Bei regulärem Abschluss und weiterhin gültigem Ziel setzt das Skript die
Zielregierung **direkt auf Kommunismus**, erhöht dort die kommunistische
Unterstützung und sperrt eine erneute Revolution für 365 Tage. Bereits
kommunistische, nicht mehr existente Ziele und SOV selbst sind ausgeschlossen.
Es gibt keine regionale Länder-Whitelist. Auch Untertanen können Ziel sein;
das Operationsskript annektiert sie nicht und ändert weder Oberherrn noch
Fraktion. Bei Jugoslawien greift anschließend die Kardelj-Regel.

Die Operation ist ausschließlich für den von Lito geführten SOV-Spieler
freigeschaltet. Ohne die Agenturmechanik des DLC erscheint sie nicht als
alternative Entscheidung. Ein abgeschlossener Auftrag garantiert den
Regierungswechsel; operative Risiken und Vorbereitung gehören weiterhin zum
nativen Agentursystem.

## Historische Paranoia und Trotzki

Litos Konflikte entstehen aus Räten, Verwaltung, Republiken und Außenpolitik.
Die historischen stalinistischen Paranoia- und Trotzki-Ketten gehören nicht zu
dieser Zeitlinie.

Der Installer untersucht die **tatsächlich lokal installierten** einschlägigen
Ereignisse, Entscheidungen, Effekte, Anzeigen, Geister und Charakterdefinitionen.
Er kopiert benötigte vollständige Dateien in die Mod und ergänzt für erkannte
historische Blöcke Schutzbedingungen gegen eine Ausführung unter Lito.
Erkannte Paranoiawerte, aktive Paranoiaflags und historische Geister werden
bereinigt; ein tatsächlich gefundener sowjetischer Trotzki-Charakter wird
zurückgezogen. Die eigentliche Spielinstallation bleibt unverändert.

Die Installationsausgabe nennt die Zahl erkannter und angepasster Blöcke.
Diese Erkennung hängt von Spielversion und vorhandenen DLC-Dateien ab.
Fehlende oder anders benannte Inhalte können weitere Anpassungen erfordern;
ein HOI4-Lauf muss deshalb bestätigen, dass keine historische Kette verbleibt.
Allgemeine sowjetische Ereignisse werden nicht pauschal abgeschaltet.

## Installation und Aktualisierung

HOI4 und Launcher schließen. Das vollständige Paket entpacken und im
Projektverzeichnis ausführen:

    powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\install_lito.ps1

Falls die Steam-Suche den Spielordner nicht findet:

    .\tools\install_lito.ps1 -GamePath 'D:\SteamLibrary\steamapps\common\Hearts of Iron IV'

Der Installer ergänzt Titoismus in einer vollständigen Kopie der installierten
Ideologiedatei. Er übernimmt Litos Porträt und die Slawische Unionsflagge,
ergänzt fehlende Rats-/Kardeljporträts und verwendet nur für die
Balkanföderationsflagge noch einen lokalen Platzhalter. Quellseitige eigene
Grafiken bleiben erhalten. Ein vorhandener Modordner und sein äußerer
Deskriptor werden vor dem Austausch mit eindeutigen Sicherungsnamen bewahrt.

Seit 0.5.1 unterstützt der Parser auch ältere CR-Zeilenenden und nennt bei
Fehlern die tatsächliche Quelldatei samt Zeile. Nicht unterstützte optionale
Paranoia-/Trotzki-Dateien werden einzeln übersprungen und mit einer Meldung
über die nur teilweise erfolgte Abschaltung aufgeführt. Ein echter Fehler
in der notwendigen Ideologiedatei stoppt die Vorbereitung weiterhin, bevor
die vorhandene Mod ausgetauscht wird.

Seit 0.5.2 verwenden die Decisions/Missionen und Kategorien eigene, vollständig
registrierte Icons. Nach Entfernung der Agitprop-Nachbildung bleiben in 0.5.3
48 Decisions/Missionen und fünf Kategorien. Die 53 Sprite-Blöcke mit `name` und
`texturefile` stehen gesammelt in
`soviet_renewal/interface/sr_decision_icons.gfx`. Die drei gelieferten Motive
bleiben für Formierung, Balkan und Einfluss erhalten; die übrigen Icons
verwenden passende vorhandene Modgrafiken.

Seit 0.5.5 verwenden die kleinen Symbole in den Entscheidungszeilen eigene
32 × 32 Pixel große Texturen. Die großen Kategorie-Bilder behalten ihre
vorherige Größe. `tools/build_decision_icons.py` erzeugt die Miniaturen mit
ImageMagick aus den vorhandenen Motiven.
Seit 0.5.6 verwenden auch die kleinen Kategorie-Symbole in den Überschriften
32 × 32 Pixel große Versionen. Große Bilder in geöffneten Kategorien behalten
ihre eigene Textur und Größe.

Der Launchername bleibt **„Sowjetunion: Litos Union“**, der Ordnername
soviet_renewal. Im Launcher aktivieren und für die vollständig geänderte
Fokus- und Ereignisstruktur eine **neue sowjetische Partie** beginnen.
Änderungen in der Cloud aktualisieren die lokale Mod nicht automatisch.
Nach HOI4-Updates den Installer erneut ausführen, damit lokale Dateikopien und
Ideologien zur Spielversion passen.

## Entwicklung und Prüfgrenzen

Statische Quellenprüfung und die vorhandenen künstlichen Skriptprüfungen:

    python3 tools/validate_mod.py
    python3 -m unittest discover -s tools -p 'test_*.py' -v

Installation und eingebetteten PowerShell-Datenblock prüfen:

    .\tools\test_install_lito.ps1
    .\tools\test_legacy_soviet.ps1
    .\tools\test_clausewitz_tokens.ps1
    python3 tools/test_paste_installer.py --pwsh /pfad/zu/pwsh

Die vorbereitete native Anbindung mit lokalen Originalquellen prüfen:

    .\tools\test_native_agitprop_install.ps1 -GameRoot 'D:\SteamLibrary\steamapps\common\Hearts of Iron IV'
    python3 tools/check_native_agitprop_runtime.py --game-root /pfad/zum/spiel --staged-mod /pfad/zur/vorbereiteten/mod

Dieser begrenzte AST-Test führt ausgewählte Originaleffekte offline aus;
er ersetzt keine HOI4-Instanz und keine Prüfung der grafischen Darstellung.

Fokusbaum und Offline-Installer aus den aktuellen Quellen erzeugen:

    python3 tools/build_focus_tree.py
    python3 tools/build_paste_installer.py

Der Diagramm-Neuaufbau benötigt zusätzlich Graphviz. Die Daten unter
tools/focus_data sind die maßgebliche Fokusquelle; generierte Skripte,
Lokalisierungen und Diagramme gehören zum selben Stand.

**Version 0.6.1 wurde in dieser Cloud nicht mit HOI4 ausgeführt.** Die native
Agitprop-Anbindung aus 0.6.0 wurde vom Nutzer im Spiel bestätigt. Quellen-
und künstliche Installationstests ersetzen keine Prüfung der Agentur, GUI,
Ereignisse, Flaggen und historischen DLC-Ketten in einer laufenden Partie.
