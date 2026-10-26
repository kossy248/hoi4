# Litos Union — Agitprop-Nachbildung entfernt in 0.5.3

- Die eigenständige Agitprop-Entscheidungskategorie mit wechselndem Einzelbild,
  ihre acht Decisions, ihr Ein-Kampagnen-Trigger und ihre Sprite-Registrierungen
  sind auf Wunsch entfernt.
- Alte Kampagnengeister bleiben ausschließlich als nicht erwerbbare, wirkungslose
  Kompatibilitäts-IDs erhalten. Eine einmalige Bereinigung entfernt sie und alte
  Kampagnenflags bei Lito, auch beim monatlichen Einstieg eines alten Spielstands.
- Acht Titel, Bonusentwürfe und ungebundene Posterquellen bleiben für die
  spätere Einbindung in das originale Agitprop vorbereitet.
- Die verbleibenden 48 Decisions/Missionen und fünf Kategorien haben weiterhin
  eigene vollständige Sprite-Definitionen.
- Der neue PowerShell-Helfer `collect_lito_agitprop.ps1` sammelt die tatsächlichen
  Agitprop-Spielquellen in einem neuen lokalen Bericht. Er verändert keine
  Spiel- oder Moddateien und überträgt nichts.

**Das originale Agitprop ist in dieser Fassung noch nicht eingebaut.** Die
bereitgestellte Vorlage ist am Ende abgeschnitten und enthält die erforderlichen
Slot-Effekte, Initialisierung und GUI-Definitionen nicht. Für die Anbindung
werden die mit dem Helfer gesammelten Originalquellen benötigt.
