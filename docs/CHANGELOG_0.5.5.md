# Litos Union — Kleine Decision-Icons in 0.5.5

Die Entscheidungszeilen verwendeten bisher 95 × 85 Pixel große Fokusgrafiken.
Im Spiel ragten diese über die Zeilenhöhe hinaus. Alle 48 kleinen
Decision-Sprites verweisen jetzt auf eigene transparente 32 × 32-DDS-Dateien.
Das Motiv wird proportional und mittig eingepasst. Die älteren
Decision-Sprite-Aliase verwenden ebenfalls die kleinen Versionen.

Die großen Kategorie-Bilder, ihre Sprite-Verweise und die gemeinsamen
Fokusgrafiken bleiben unverändert. Es werden keine Motive neu gezeichnet.
`tools/build_decision_icons.py` erzeugt die 18 Miniaturen erneut aus den
vorhandenen Quellen.

Geprüft werden Sprite-Verweise, Texturgrößen, DXT5/Transparenz und die
unveränderten Originaltexturen. Das vollständige Installationspaket wird mit
künstlichen Spieldateien geprüft; eine Darstellungskontrolle in HOI4 bleibt
erforderlich.
