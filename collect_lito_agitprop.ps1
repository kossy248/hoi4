# Read-only source collection for Lito's native Soviet agitprop integration.
# Windows PowerShell 5.1 / PowerShell 7. No game or mod files are changed.
[CmdletBinding()]
param(
    [string]$GamePath,
    [string]$OutputDirectory = (Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Paradox Interactive\Hearts of Iron IV\Lito_Diagnose'),
    [switch]$CreateZip
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Find-LitoCollectorGame {
    param([string]$ExplicitPath)
    if (-not [string]::IsNullOrWhiteSpace($ExplicitPath)) {
        $resolved = (Resolve-Path -LiteralPath $ExplicitPath).Path
        if (-not (Test-Path -LiteralPath (Join-Path $resolved 'common/ideologies/00_ideologies.txt') -PathType Leaf)) {
            throw "Kein HOI4-Spielordner: $resolved. Erwartet: common/ideologies/00_ideologies.txt"
        }
        return $resolved.TrimEnd([char[]]'\/')
    }
    $steamRoots = [Collections.Generic.List[string]]::new()
    foreach ($key in @('HKCU:\Software\Valve\Steam', 'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam', 'HKLM:\SOFTWARE\Valve\Steam')) {
        $properties = Get-ItemProperty -LiteralPath $key -ErrorAction SilentlyContinue
        if ($null -eq $properties) { continue }
        foreach ($name in @('SteamPath', 'InstallPath')) {
            $property = $properties.PSObject.Properties[$name]
            if (($null -ne $property) -and $property.Value) { $steamRoots.Add([string]$property.Value) }
        }
    }
    foreach ($base in @(${env:ProgramFiles(x86)}, $env:ProgramFiles)) {
        if ($base) { $steamRoots.Add((Join-Path $base 'Steam')) }
    }
    $libraries = [Collections.Generic.List[string]]::new()
    foreach ($steamRoot in ($steamRoots | Select-Object -Unique)) {
        $libraries.Add($steamRoot)
        $vdf = Join-Path $steamRoot 'steamapps/libraryfolders.vdf'
        if (Test-Path -LiteralPath $vdf -PathType Leaf) {
            foreach ($match in [regex]::Matches([IO.File]::ReadAllText($vdf), '"path"\s+"([^"\r\n]+)"')) {
                $libraries.Add($match.Groups[1].Value.Replace('\\', '\'))
            }
        }
    }
    foreach ($library in ($libraries | Select-Object -Unique)) {
        $candidate = Join-Path $library 'steamapps/common/Hearts of Iron IV'
        if (Test-Path -LiteralPath (Join-Path $candidate 'common/ideologies/00_ideologies.txt') -PathType Leaf) {
            return (Resolve-Path -LiteralPath $candidate).Path.TrimEnd([char[]]'\/')
        }
    }
    throw "HOI4 wurde nicht gefunden. Mit -GamePath 'D:\SteamLibrary\steamapps\common\Hearts of Iron IV' und dem tatsaechlichen Spielordner erneut ausfuehren."
}

function Get-LitoCollectorBlocks {
    param([string]$Text)
    # Tolerant indexing only, not validation: an incomplete original is still
    # collected in full so that its actual problem can be diagnosed.
    $pattern = '#[^\r\n]*|"(?:\\.|[^"\\])*"|[{}=]|[^\s{}=#"]+'
    $tokens = @([regex]::Matches($Text, $pattern) | Where-Object { -not $_.Value.StartsWith('#') })
    $blocks = [Collections.Generic.List[object]]::new()
    $stack = [Collections.Generic.Stack[int]]::new()
    for ($i = 0; $i -lt $tokens.Count; $i++) {
        $token = $tokens[$i]
        if ($token.Value -eq '{') {
            $key = ''; $start = $token.Index
            if (($i -ge 2) -and ($tokens[$i - 1].Value -eq '=')) {
                $key = $tokens[$i - 2].Value.Trim('"'); $start = $tokens[$i - 2].Index
            }
            $parent = -1
            if ($stack.Count -gt 0) { $parent = $stack.Peek() }
            $blocks.Add([pscustomobject]@{ Key = $key; Start = $start; End = $Text.Length; Parent = $parent })
            $stack.Push($blocks.Count - 1)
        } elseif (($token.Value -eq '}') -and ($stack.Count -gt 0)) {
            $blocks[$stack.Pop()].End = $token.Index + $token.Length
        }
    }
    return ,$blocks.ToArray()
}

function Get-LitoCollectorNamedContainers {
    param([string]$Text, [string]$Name)
    $namePattern = '(?m)\bname\s*=\s*(?:"' + [regex]::Escape($Name) + '"|' + [regex]::Escape($Name) + '(?![\w]))'
    $matchingContainers = [Collections.Generic.List[object]]::new()
    foreach ($block in (Get-LitoCollectorBlocks -Text $Text)) {
        if ($block.Key -notin @('containerWindowType', 'windowType')) { continue }
        $part = $Text.Substring($block.Start, $block.End - $block.Start)
        if ($part -match $namePattern) { $matchingContainers.Add([pscustomobject]@{ Start = $block.Start; End = $block.End; Text = $part }) }
    }
    # A parent container may contain the named child's assignment. Select the
    # smallest matching container(s), not every unrelated sibling in the file.
    return @($matchingContainers | Where-Object {
        $outer = $_
        -not @($matchingContainers | Where-Object { ($_.Start -gt $outer.Start) -and ($_.End -le $outer.End) }).Count
    })
}

$gameRoot = Find-LitoCollectorGame -ExplicitPath $GamePath
$outputRoot = [IO.Path]::GetFullPath($OutputDirectory).TrimEnd([char[]]'\/')
$separators = [char[]]'\/'
$insideGame = ($outputRoot -ieq $gameRoot) -or $outputRoot.StartsWith($gameRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)
$insideMod = $false
$documents = [Environment]::GetFolderPath('MyDocuments')
if (-not [string]::IsNullOrWhiteSpace($documents)) {
    $defaultModRoot = [IO.Path]::GetFullPath((Join-Path $documents 'Paradox Interactive\Hearts of Iron IV\mod')).TrimEnd($separators)
    $insideMod = ($outputRoot -ieq $defaultModRoot) -or $outputRoot.StartsWith($defaultModRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)
}
if ($insideGame -or $insideMod) { throw 'Der Diagnoseordner muss ausserhalb des Spielordners und des HOI4-Modordners liegen.' }

$seed = '\b(?:GFX_)?SOV_(?:expand_the_agitprop|propaganda_[A-Za-z0-9_]*|new_propaganda_campaign|poster_(?:left|center|right)_icon_frame|default_propaganda_[A-Za-z0-9_]*|(?:pick|reset|unlock)_propaganda_campaign_slot_effect|increase_propaganda_campaign_cost_effect|achievement_propaganda_counter_effect)\b'
$selected = @{}
$warnings = [Collections.Generic.List[string]]::new()
$warnings.Add('DLC-Unterordner und DLC-Archive wurden nicht durchsucht. Falls benoetigte Originaldateien dort liegen, muessen sie zusaetzlich bereitgestellt werden.')
$asciiIndex = @{}
$utf8 = [Text.UTF8Encoding]::new($false, $true)
$candidateFiles = [Collections.Generic.List[object]]::new()
foreach ($relativeFolder in @('common/decisions', 'common/national_focus', 'common/scripted_effects', 'common/scripted_triggers', 'common/scripted_guis', 'common/scripted_variables', 'common/on_actions', 'history/countries', 'interface')) {
    $folder = Join-Path $gameRoot $relativeFolder
    if (-not (Test-Path -LiteralPath $folder -PathType Container)) { continue }
    foreach ($file in @(Get-ChildItem -LiteralPath $folder -File -Recurse)) {
        if ((($relativeFolder -eq 'interface') -and ($file.Extension -in @('.gui', '.gfx'))) -or
            (($relativeFolder -ne 'interface') -and ($file.Extension -eq '.txt'))) {
            $candidateFiles.Add($file)
        }
    }
}

function Add-LitoCollectorFile {
    param([object]$File)
    if ($selected.ContainsKey($File.FullName)) { return $selected[$File.FullName] }
    $relative = $File.FullName.Substring($gameRoot.Length).TrimStart([char[]]'\/').Replace('\', '/')
    try {
        $bytes = [IO.File]::ReadAllBytes($File.FullName)
        $bom = ($bytes.Length -ge 3) -and ($bytes[0] -eq 239) -and ($bytes[1] -eq 187) -and ($bytes[2] -eq 191)
        $offset = 0; if ($bom) { $offset = 3 }
        $sourceText = $utf8.GetString($bytes, $offset, $bytes.Length - $offset)
        $hasher = [Security.Cryptography.SHA256]::Create()
        try { $hash = ([BitConverter]::ToString($hasher.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant() }
        finally { $hasher.Dispose() }
        $lineEnds = @()
        if ($sourceText.Contains("`r`n")) { $lineEnds += 'CRLF' }
        if ([regex]::IsMatch($sourceText, '(?<!\r)\n')) { $lineEnds += 'LF' }
        if ([regex]::IsMatch($sourceText, '\r(?!\n)')) { $lineEnds += 'CR' }
        if ($lineEnds.Count -eq 0) { $lineEnds += 'keine' }
        $entry = [pscustomobject]@{ Relative = $relative; Text = $sourceText; Hash = $hash; Bom = $bom; LineEnds = ($lineEnds -join ', '); Size = $bytes.Length }
        $selected[$File.FullName] = $entry
        return $entry
    } catch {
        $message = "$relative : $($_.Exception.Message)"
        if (-not $warnings.Contains($message)) { $warnings.Add($message) }
        return $null
    }
}

foreach ($file in $candidateFiles) {
    try {
        $ascii = [Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($file.FullName))
        if ($file.Extension -in @('.gui', '.gfx')) { $asciiIndex[$file.FullName] = $ascii }
        if ($ascii -match $seed) { $null = Add-LitoCollectorFile -File $file }
    } catch { $warnings.Add(($file.FullName.Substring($gameRoot.Length).TrimStart($separators) + ' : ' + $_.Exception.Message)) }
}

# Follow only relevant scripted-GUI panels, then their named containers and
# literal GFX references. Whole selected files go in the report, but unrelated
# sibling panels/sprites do not fan out into the entire interface inventory.
$windows = @{}; $sprites = @{}
function Add-LitoCollectorReferences {
    param([string]$Text)
    foreach ($match in [regex]::Matches($Text, '\bwindow_name\s*=\s*(?:"([^"\r\n]+)"|([\w]+))')) {
        $name = $match.Groups[1].Value; if (-not $name) { $name = $match.Groups[2].Value }
        $windows[$name] = $true
    }
    foreach ($match in [regex]::Matches($Text, '\bGFX_[A-Za-z0-9_]+\b')) { $sprites[$match.Value] = $true }
}
foreach ($entry in @($selected.Values)) {
    if ($entry.Relative.StartsWith('common/scripted_guis/')) {
        $blocks = Get-LitoCollectorBlocks -Text $entry.Text
        foreach ($block in $blocks) {
            if (($block.Parent -ge 0) -and ($blocks[$block.Parent].Key -eq 'scripted_gui')) {
                $part = $entry.Text.Substring($block.Start, $block.End - $block.Start)
                if ($part -match $seed) { Add-LitoCollectorReferences -Text $part }
            }
        }
    } elseif ($entry.Relative.StartsWith('interface/') -and $entry.Relative.EndsWith('.gui')) {
        foreach ($block in (Get-LitoCollectorBlocks -Text $entry.Text)) {
            if ($block.Key -in @('containerWindowType', 'windowType')) {
                $part = $entry.Text.Substring($block.Start, $block.End - $block.Start)
                if ($part -match $seed) { Add-LitoCollectorReferences -Text $part }
            }
        }
    }
}
$foundWindows = @{}; $foundSprites = @{}
foreach ($name in @($windows.Keys)) {
    foreach ($file in @($candidateFiles | Where-Object { $_.Extension -eq '.gui' })) {
        if (-not $asciiIndex.ContainsKey($file.FullName) -or -not $asciiIndex[$file.FullName].Contains($name)) { continue }
        $wasSelected = $selected.ContainsKey($file.FullName)
        $entry = Add-LitoCollectorFile -File $file
        if ($null -eq $entry) { continue }
        $parts = @(Get-LitoCollectorNamedContainers -Text $entry.Text -Name $name)
        if ($parts.Count -gt 0) {
            $foundWindows[$name] = $true
            foreach ($part in $parts) { Add-LitoCollectorReferences -Text $part.Text }
        } else {
            # A prefilter hit is not a confirmed definition or dependency.
            if (-not $wasSelected -and -not ($entry.Text -match $seed)) { $selected.Remove($file.FullName) }
        }
    }
    if (-not $foundWindows.ContainsKey($name)) { $warnings.Add("GUI-Fensterdefinition nicht gefunden: $name") }
}
foreach ($name in @($sprites.Keys)) {
    $definition = '\bname\s*=\s*(?:"' + [regex]::Escape($name) + '"|' + [regex]::Escape($name) + '(?![\w]))'
    foreach ($file in @($candidateFiles | Where-Object { $_.Extension -eq '.gfx' })) {
        if (-not $asciiIndex.ContainsKey($file.FullName) -or -not $asciiIndex[$file.FullName].Contains($name)) { continue }
        $wasSelected = $selected.ContainsKey($file.FullName)
        $entry = Add-LitoCollectorFile -File $file
        if ($null -eq $entry) { continue }
        if ($entry.Text -match $definition) { $foundSprites[$name] = $true }
        elseif (-not $wasSelected -and -not ($entry.Text -match $seed)) { $selected.Remove($file.FullName) }
    }
    if (-not $foundSprites.ContainsKey($name)) { $warnings.Add("Sprite-Definition nicht gefunden: $name") }
}

# Read dimensions of referenced DDS textures without collecting their pixels.
# This distinguishes a multi-frame native atlas from individual poster images.
$textureMetadata = @{}
foreach ($entry in @($selected.Values | Where-Object { $_.Relative.EndsWith('.gfx') })) {
    foreach ($block in (Get-LitoCollectorBlocks -Text $entry.Text)) {
        if ($block.Key -notin @('spriteType', 'quadTextureSprite')) { continue }
        $part = $entry.Text.Substring($block.Start, $block.End - $block.Start)
        $nameMatch = [regex]::Match($part, '\bname\s*=\s*"?(GFX_[A-Za-z0-9_]+)"?')
        if (-not $nameMatch.Success -or -not $sprites.ContainsKey($nameMatch.Groups[1].Value)) { continue }
        $textureMatch = [regex]::Match($part, '\btexturefile\s*=\s*"([^"\r\n]+)"')
        if (-not $textureMatch.Success) { continue }
        $texture = $textureMatch.Groups[1].Value.Replace('\', '/')
        if ($textureMetadata.ContainsKey($texture)) { continue }
        try {
            if ([IO.Path]::IsPathRooted($texture) -or -not $texture.EndsWith('.dds', [StringComparison]::OrdinalIgnoreCase)) { continue }
            $path = [IO.Path]::GetFullPath((Join-Path $gameRoot $texture))
            if (-not $path.StartsWith($gameRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Texturpfad liegt ausserhalb des Spiels.' }
            if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw 'Textur nicht als lose Datei gefunden; eventuell in einem DLC-Archiv.' }
            $stream = [IO.File]::OpenRead($path)
            try {
                $header = New-Object byte[] 128
                $read = $stream.Read($header, 0, $header.Length)
            } finally { $stream.Dispose() }
            if ($read -ne 128 -or [Text.Encoding]::ASCII.GetString($header, 0, 4) -cne 'DDS ') { throw 'Kein vollstaendiger DDS-Header.' }
            $textureMetadata[$texture] = ('{0} | {1}x{2} | FourCC {3} | Mipmaps {4}' -f $texture,
                [BitConverter]::ToUInt32($header, 16), [BitConverter]::ToUInt32($header, 12),
                [Text.Encoding]::ASCII.GetString($header, 84, 4).Trim([char]0), [BitConverter]::ToUInt32($header, 28))
        } catch {
            $textureMetadata[$texture] = ($texture + ' | keine Headerdaten: ' + $_.Exception.Message)
        }
    }
}

$inventory = @(
    @{ Name = 'Kampagnenentscheidungen'; Prefix = 'common/decisions/'; Exclude = 'common/decisions/categories/' },
    @{ Name = 'Entscheidungskategorie'; Prefix = 'common/decisions/categories/'; Exclude = '' },
    @{ Name = 'Originaler Agitprop-Fokus / Freischaltung'; Prefix = 'common/national_focus/'; Exclude = '' },
    @{ Name = 'Scripted Effects / Initialisierung'; Prefix = 'common/scripted_effects/'; Exclude = '' },
    @{ Name = 'Scripted Triggers'; Prefix = 'common/scripted_triggers/'; Exclude = '' },
    @{ Name = 'Scripted GUI'; Prefix = 'common/scripted_guis/'; Exclude = '' },
    @{ Name = 'GUI-Dateien'; Prefix = 'interface/'; Suffix = '.gui'; Exclude = '' },
    @{ Name = 'Sprite-Registrierungen'; Prefix = 'interface/'; Suffix = '.gfx'; Exclude = '' }
)
$report = [Text.StringBuilder]::new()
$null = $report.AppendLine('LITO: ORIGINALDATEIEN FUER NATIVES SOWJETISCHES AGITPROP')
$null = $report.AppendLine('Nur lokale Quelldateien gelesen. Spiel und Mod wurden nicht veraendert.')
$null = $report.AppendLine('Dieser Bericht bestaetigt keine vollstaendige oder funktionierende Integration.')
$null = $report.AppendLine('Keine Speicherstaende, Protokolle, Zugangsdaten oder Texturbinaerdateien enthalten.')
$null = $report.AppendLine('Die folgenden Dateiinhalte sind vollstaendig; nicht als Chattext kuerzen.')
$null = $report.AppendLine('')
$null = $report.AppendLine('BESTAND')
foreach ($group in $inventory) {
    $matchingGroupFiles = @($selected.Values | Where-Object {
        $_.Relative.StartsWith($group.Prefix) -and (-not $group.Exclude -or -not $_.Relative.StartsWith($group.Exclude)) -and
        (-not $group.ContainsKey('Suffix') -or $_.Relative.EndsWith($group.Suffix))
    })
    $null = $report.AppendLine(('{0}: {1} Datei(en)' -f $group.Name, $matchingGroupFiles.Count))
    if ($matchingGroupFiles.Count -eq 0) { $warnings.Add(('Keine passenden Dateien: ' + $group.Name)) }
}
$null = $report.AppendLine('')
$null = $report.AppendLine('DATEIVERZEICHNIS')
foreach ($entry in @($selected.Values | Sort-Object Relative)) {
    $null = $report.AppendLine(('{0} | {1} Bytes | SHA256 {2} | UTF8-BOM {3} | Zeilenenden {4}' -f $entry.Relative, $entry.Size, $entry.Hash, $entry.Bom, $entry.LineEnds))
}
$null = $report.AppendLine('')
$null = $report.AppendLine('DDS-TEXTURMETADATEN OHNE BILDDATEN')
foreach ($key in @($textureMetadata.Keys | Sort-Object)) { $null = $report.AppendLine($textureMetadata[$key]) }
$null = $report.AppendLine('')
$null = $report.AppendLine('HINWEISE / NICHT GEFUNDENE TEILE')
if ($warnings.Count -eq 0) { $null = $report.AppendLine('Keine Lesefehler oder fehlenden Dateigruppen erkannt. Die native Abhaengigkeitspruefung bleibt erforderlich.') }
foreach ($warning in $warnings) { $null = $report.AppendLine($warning); Write-Warning $warning }
foreach ($entry in @($selected.Values | Sort-Object Relative)) {
    $null = $report.AppendLine('')
    $null = $report.AppendLine(('===== BEGIN FILE: {0} =====' -f $entry.Relative))
    $null = $report.Append($entry.Text)
    $null = $report.AppendLine('')
    $null = $report.AppendLine(('===== END FILE: {0} =====' -f $entry.Relative))
}
New-Item -ItemType Directory -Path $outputRoot -Force | Out-Null
$stem = 'Lito_Agitprop_Originaldateien_' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '_' + [guid]::NewGuid().ToString('N')
$reportPath = Join-Path $outputRoot ($stem + '.txt')
[IO.File]::WriteAllText($reportPath, $report.ToString(), [Text.UTF8Encoding]::new($true))
Write-Host ("Agitprop-Bericht erstellt: $reportPath") -ForegroundColor Green
Write-Host 'Bitte diese TXT-Datei als Datei an den Chat anhaengen; ihren Inhalt nicht kuerzen oder nur teilweise kopieren.'
$zipPath = $null
if ($CreateZip) {
    $zipPath = Join-Path $outputRoot ($stem + '.zip')
    Compress-Archive -LiteralPath $reportPath -DestinationPath $zipPath
    Write-Host ("ZIP-Kopie: $zipPath")
}
[pscustomobject]@{ ReportPath = $reportPath; ZipPath = $zipPath; FileCount = $selected.Count; WarningCount = $warnings.Count }
