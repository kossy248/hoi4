# Originales Agitprop für Lito — 0.6.0

Die Anbindung verwendet die echten sowjetischen Kampagnen, Slot-Effekte,
Scripted-GUI und GUI-Elemente der lokalen HOI4-Installation. Die frühere
Einzelbild-Nachbildung bleibt entfernt. Es wird kein eigenes Drei-Poster-System
an ihre Stelle gesetzt.

## Freischaltung

Der bisherige Fokus `sr_lito_politics_cadre_schools` heißt **„Agitprop der
Völker“**, dauert 35 Tage und folgt auf **„Ein Mandat für Lito“**. Seine ID,
Position und der vorhandene Bonus von täglich 0,05 politischer Macht bleiben.
Er setzt `sr_lito_native_agitprop_unlocked` und synchronisiert die native
Freischaltung. Der Installer setzt die Bereitschaft erst nach erfolgreicher
Prüfung der Originaldateien; vorher bleibt der Fokus gesperrt.

Der erste Platz entspricht `SOV_expand_the_agitprop`. **„Räte in den Betrieben“**
übernimmt die zusätzliche Freischaltung von `SOV_collectivist_propaganda`,
**„Die Akademien vernetzen“** die von `SOV_the_komsomol`. Die beiden Meilensteine
werden auch erkannt, wenn sie bereits vor dem Agitprop-Fokus abgeschlossen
wurden. Vorhandene Spielstände werden beim nächsten Spieltag synchronisiert.

Die Kategorie und neun Basiskampagnen akzeptieren zusätzlich den Lito-Fokus.
Eine kollektivistische und drei Komsomol-Kampagnen akzeptieren die passenden
beiden Meilensteine. Andere Vanilla-Fokusbedingungen bleiben bestehen. Damit
sind aktuell 13 der 24 Originalkampagnen an Litos Baum angebunden; die übrigen
werden nicht pauschal freigeschaltet.

## Originaler Laufzeitvertrag

Die geprüften Originale initialisieren gesperrte Frames mit 1, leere mit 2,
180 Tage Kampagnendauer, 90 Tage Abklingzeit, Alterung nach 150 Tagen und
15 politische Macht als Anfangskosten. `SOV_increase_propaganda_campaign_cost_effect`
multipliziert die jeweiligen Kosten nach Ablauf mit 2.

`SOV_pick_propaganda_campaign_slot_effect` und
`SOV_reset_propaganda_campaign_slot_effect` verwalten die echten linken,
mittleren und rechten Frames sowie Countdown- und Alterungszustände.
`SOV_unlock_propaganda_campaign_slot_effect` wird nur bei einem tatsächlich
fehlenden, gesperrten Platz aufgerufen. Sein sonst bedingungsloser rechter
Fallback darf keine laufende rechte Kampagne löschen. Bestehende Frames,
Kosten und Kampagnenzähler werden deshalb erhalten; nur fehlende Variablen
werden aus der echten Ländergeschichte ergänzt.

## Bilder in der originalen GUI

Die drei gelieferten 150×200-DDS werden bei den tatsächlichen Kampagnen-IDs
3, 7 und 11 angezeigt. Die IDs liest der Installer aus den jeweiligen
`complete_effect`-Blöcken, nicht aus den abweichenden historischen Kommentaren.

Die ursprünglichen drei Poster-Properties mit den dynamischen
`GetPropaganda…SlotAge`-Bildern und die drei Countdowntexte bleiben erhalten.
Zusätzliche Bildfelder übernehmen exakt Position und Tooltip des Originals.
Nur während einer passenden eigenen Kampagne wird das ursprüngliche Bildfeld
ausgeblendet und das gelieferte Bild angezeigt. Bei Ende, leerem/gesperrtem
Platz oder anderen Kampagnen erscheint wieder die Originalgrafik. Die Bilder
selbst werden nicht neu gezeichnet oder gealtert.

Die bereitgestellte GUI-Datei hat eine ungeschlossene äußere `guiTypes`-Klammer.
Der Installer normalisiert ausschließlich die Modkopie und nur nach Prüfung
auf genau das bekannte Fenster, vier ursprüngliche Icons und drei Zeittexte.
Die nativen Bildstreifen mit frischer und drei gealterten Fassungen werden nicht kopiert
oder ersetzt; sie bleiben im installierten Spiel.

## Installation und Prüfung

`tools/install_native_agitprop.ps1` prüft Kategorien, 24 Kampagnen,
Originaleffekte, Freischaltfokus, Startwerte und Grafikregistrierungen.
`tools/install_native_agitprop_gui.ps1` bindet die Bilder ein. Die Module
bearbeiten vorhandene Staging-Kopien, damit die Paranoia-/Trotzki-Sperren
bestehen bleiben. Ein Fehler stellt den vorherigen Staging-Zustand wieder her.
Originaldateien und Bilderstreifen werden nicht im öffentlichen Modpaket
veröffentlicht; sie werden erst lokal beim Nutzer gelesen.

Die gelieferten Originaldateien wurden anhand der SHA-256-Werte des Berichts
bytegleich rekonstruiert. Mit ihnen werden Installation, wiederholte Anwendung,
Rücksetzung bei Fehlern und die Laufzeitbedingungen offline geprüft. Ein
laufender HOI4-Spieltest ist in der Cloud nicht verfügbar. Nach Updates des
Spiels muss die lokale Anbindung erneut vorbereitet werden.
