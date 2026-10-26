# Litos Union — Installerkorrektur in 0.5.1

- Kommentare werden bei LF, CRLF und älteren CR-Zeilenenden korrekt beendet.
  Dadurch entsteht bei gültigen CR-Dateien keine falsche Klammerfehlermeldung.
- Parserfehler nennen die tatsächliche Quelldatei und die betroffene Zeile.
  Historische Ereignisdateien werden nicht mehr als Ideologiedatei bezeichnet.
- Nicht lesbare oder nicht unterstützte optionale Paranoia-/Trotzki-Dateien
  verhindern nicht mehr die vollständige Modinstallation. Der Installer nennt
  die übersprungenen Dateien und meldet ausdrücklich eine nur teilweise
  erfolgte historische Abschaltung. Gültige Dateien werden weiter angepasst.
- Daten aus übersprungenen Dateien gelangen nicht in die tägliche Bereinigung.
- Die notwendige Ideologiedatei bleibt streng geprüft. Bei einem echten Fehler
  bleibt die vorhandene Mod einschließlich ihres Deskriptors erhalten.

Die konkrete beim Nutzer betroffene Datei ist aus der bisherigen allgemeinen
Fehlermeldung nicht bestimmbar. Der CR-Fall ist mit dem tatsächlichen Parser
reproduziert und korrigiert; weitere Meldungen enthalten nun den nötigen Pfad.
