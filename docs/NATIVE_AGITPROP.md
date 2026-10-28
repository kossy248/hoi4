# Originales Agitprop mit eigenen Kampagnen — 0.6.1

Die Anbindung verwendet die echten sowjetischen Slot-Effekte, Scripted-GUI und
GUI-Elemente der lokalen HOI4-Installation. Innerhalb dieses Systems stehen unter
Lito ausschließlich drei eigene Kampagnen mit den drei gelieferten Postern zur
Auswahl. Die frühere Einzelbild-Nachbildung bleibt entfernt.

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

Der Agitprop-Fokus öffnet alle drei eigenen Kampagnen. Jede benötigt einen freien
Platz und darf nur einmal gleichzeitig laufen; alle drei sind im Frieden und
Krieg verfügbar. Die beiden weiteren Foki ergänzen ausschließlich Plätze.
Sämtliche 24 Vanilla-Kampagnen und die nativen Debug-Auswahlen werden für die von
Lito geführte Sowjetunion ausgeblendet. Außerhalb dieses Szenarios bleiben ihre
ursprünglichen Bedingungen erhalten.

| Kampagne | Eigene Boni während der Laufzeit |
| --- | --- |
| Solange ein Stern über uns brennt | Stabilität +4 Prozentpunkte; Kriegsunterstützung +3 Prozentpunkte |
| Elf Völker – ein gemeinsamer Morgen | Stabilität +4 Prozentpunkte; täglich +0,05 politische Macht; zusätzlich beim Start +5 Vertrauen, höchstens 100, und +0,02 Unionsbalance |
| Für die Union bis zum letzten Licht | Erholungsrate des Heeres +6 %; Kriegsunterstützung +5 Prozentpunkte; Nachschubverbrauch −3 % |

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

Auch noch aktive Vanilla-Kampagnen aus älteren Spielständen werden nicht
abgebrochen oder durch neue Boni ersetzt. Sie laufen regulär aus; bis dahin
bleibt ihr Platz belegt und ihr Countdown sichtbar. Ihre Vanilla-Postermotive
werden unter Lito bereits ausgeblendet. Eine eigene Kampagne mit derselben
nativen Frame-ID wartet auf das Ende der bisherigen Kampagne, damit die
Rücksetzung keinen anderen laufenden Platz treffen kann.

## Bilder in der originalen GUI

Die drei gelieferten 150×200-DDS werden bei den tatsächlichen Kampagnen-IDs
3, 7 und 11 angezeigt. Die IDs liest der Installer aus den jeweiligen
`complete_effect`-Blöcken, nicht aus den abweichenden historischen Kommentaren.

Die ursprünglichen drei Poster-Properties mit den dynamischen
`GetPropaganda…SlotAge`-Bildern und die drei Countdowntexte bleiben erhalten.
Zusätzliche Bildfelder übernehmen die Position des Originals und zeigen
eigene Tooltips mit Kampagnentiteln und Boni.
Die passenden eigenen Kampagnen zeigen jeweils das gelieferte Bild. Unter Lito
bleiben die ursprünglichen Bildfelder nur für leere oder gesperrte Plätze
sichtbar; andere Vanilla-Postermotive werden nicht mehr angezeigt. Die Bilder
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
Rücksetzung bei Fehlern, die Auswahl eigener Kampagnen und die Laufzeitbedingungen
offline geprüft. Die native Anbindung aus 0.6.0 wurde vom Nutzer im Spiel
bestätigt. Ein laufender HOI4-Spieltest von 0.6.1 ist in der Cloud nicht
verfügbar. Nach Updates des Spiels muss die lokale Anbindung erneut vorbereitet
werden. Weitere Poster werden erst ergänzt, sobald der Nutzer sie fertig hat.
