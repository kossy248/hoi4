"""Build the offline, self-contained PowerShell updater from current mod sources."""
from pathlib import Path
import base64
import gzip
import hashlib
import json
import textwrap

ROOT = Path(__file__).resolve().parents[1]


def build():
    paths = sorted(path for path in (ROOT / 'soviet_renewal').rglob('*') if path.is_file())
    paths.append(ROOT / 'tools/install_lito.ps1')
    paths.extend(ROOT / f'tools/{name}.ps1' for name in (
        'install_native_agitprop', 'install_native_agitprop_gui'))
    # Text preserves localization BOMs as U+FEFF; DDS and other art stay binary.
    files = {}
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        if path.suffix.lower() in ('.dds', '.tga', '.png', '.jpg', '.jpeg'):
            files[relative] = {'base64': base64.b64encode(path.read_bytes()).decode('ascii')}
        else:
            files[relative] = path.read_text(encoding='utf-8')
    raw = json.dumps(files, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    packed = gzip.compress(raw, compresslevel=9, mtime=0)
    payload = '\n'.join(textwrap.wrap(base64.b64encode(packed).decode('ascii'), 120))
    checksum = hashlib.sha256(packed).hexdigest()
    script = r'''# HOI4 und Launcher vorher schliessen. Keine Downloads oder Administratorrechte noetig.
# Leer lassen fuer die automatische Steam-Suche; bei Bedarf den Spielordner eintragen.
$litoGamePath = ''
# Leer lassen fuer den HOI4-Modordner unter Dokumente.
$litoModDirectory = ''
$ErrorActionPreference = 'Stop'
$litoPayload = @'
__PAYLOAD__
'@
$litoBytes = [Convert]::FromBase64String($litoPayload)
$litoHasher = [Security.Cryptography.SHA256]::Create()
try {
    $litoHash = ([BitConverter]::ToString($litoHasher.ComputeHash($litoBytes))).Replace('-', '').ToLowerInvariant()
} finally {
    $litoHasher.Dispose()
}
if ($litoHash -ne '__CHECKSUM__') {
    throw 'Der kopierte Datenblock ist unvollstaendig. Bitte den gesamten Block erneut kopieren.'
}
$litoMemory = [IO.MemoryStream]::new($litoBytes)
$litoGzip = [IO.Compression.GZipStream]::new($litoMemory, [IO.Compression.CompressionMode]::Decompress)
$litoReader = [IO.StreamReader]::new($litoGzip, [Text.Encoding]::UTF8)
try {
    $litoFiles = ConvertFrom-Json -InputObject $litoReader.ReadToEnd()
} finally {
    $litoReader.Dispose()
    $litoMemory.Dispose()
}
$litoTempRoot = Join-Path ([IO.Path]::GetTempPath()) ('lito-update-' + [guid]::NewGuid().ToString('N'))
try {
    New-Item -ItemType Directory -Path $litoTempRoot | Out-Null
    foreach ($litoEntry in $litoFiles.PSObject.Properties) {
        if ((-not $litoEntry.Name.StartsWith('soviet_renewal/')) -and
            ($litoEntry.Name -notin @('tools/install_lito.ps1', 'tools/install_native_agitprop.ps1', 'tools/install_native_agitprop_gui.ps1'))) {
            throw 'Unerwarteter Dateipfad im Modpaket.'
        }
        if ($litoEntry.Name -match '(^|/)\.\.(/|$)|[:\\]') {
            throw 'Ungueltiger Dateipfad im Modpaket.'
        }
        $litoTarget = Join-Path $litoTempRoot $litoEntry.Name
        New-Item -ItemType Directory -Path (Split-Path -Parent $litoTarget) -Force | Out-Null
        if ($litoEntry.Value -is [string]) {
            [IO.File]::WriteAllText($litoTarget, $litoEntry.Value, [Text.UTF8Encoding]::new($false))
        } elseif ($null -ne $litoEntry.Value.PSObject.Properties['base64']) {
            [IO.File]::WriteAllBytes($litoTarget, [Convert]::FromBase64String($litoEntry.Value.base64))
        } else {
            throw 'Unbekanntes Dateiformat im Modpaket.'
        }
    }
    $litoArguments = @{ SourceRoot = $litoTempRoot }
    if (-not [string]::IsNullOrWhiteSpace($litoGamePath)) { $litoArguments.GamePath = $litoGamePath }
    if (-not [string]::IsNullOrWhiteSpace($litoModDirectory)) { $litoArguments.ModDirectory = $litoModDirectory }
    $litoHelperPath = Join-Path $litoTempRoot 'tools/install_lito.ps1'
    $litoHelper = [ScriptBlock]::Create([IO.File]::ReadAllText($litoHelperPath))
    & $litoHelper @litoArguments
    Write-Host 'Fertig. Im Launcher "Sowjetunion: Litos Union" aktivieren und eine neue sowjetische Partie starten.' -ForegroundColor Green
} finally {
    try {
        if (Test-Path -LiteralPath $litoTempRoot) { Remove-Item -LiteralPath $litoTempRoot -Recurse -Force }
    } catch {
        Write-Warning "Temporaere Dateien verblieben unter $litoTempRoot. $($_.Exception.Message)"
    }
}
'''
    script = script.replace('__PAYLOAD__', payload).replace('__CHECKSUM__', checksum)
    output = ROOT / 'install_lito_copy_paste.ps1'
    output.write_text(script, encoding='utf-8')
    print(f'Built {output.name}: {len(files)} files, {len(packed)} compressed bytes, SHA-256 {checksum}')
    return output, files


if __name__ == '__main__':
    build()
