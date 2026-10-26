# Run in Windows PowerShell 5.1 or PowerShell 7 from the extracted project:
# .\tools\install_lito.ps1
# If Steam cannot be detected:
# .\tools\install_lito.ps1 -GamePath 'D:\SteamLibrary\steamapps\common\Hearts of Iron IV'
# No network access or administrator rights are needed. Game files are only read.
[CmdletBinding()]
param(
    [string]$GamePath,
    [string]$ModDirectory = (Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Paradox Interactive\Hearts of Iron IV\mod'),
    [string]$SourceRoot = (Split-Path -Parent $PSScriptRoot)
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-ClausewitzTokens {
    param([Parameter(Mandatory = $true)][string]$Text, [string]$SourceName = 'Skripttext')
    $tokens = [Collections.Generic.List[object]]::new()
    $i = 0
    while ($i -lt $Text.Length) {
        $c = $Text[$i]
        if ([char]::IsWhiteSpace($c)) { $i++; continue }
        if ($c -eq '#') {
            while (($i -lt $Text.Length) -and ($Text[$i] -ne "`n") -and ($Text[$i] -ne "`r")) { $i++ }
            continue
        }
        $start = $i
        if ($c -eq '"') {
            $i++
            $closed = $false
            while ($i -lt $Text.Length) {
                if ($Text[$i] -eq '\') { $i += 2; continue }
                if ($Text[$i] -eq '"') { $i++; $closed = $true; break }
                $i++
            }
            if (-not $closed) {
                $line = [regex]::Matches($Text.Substring(0, $start), "`r`n|`r|`n").Count + 1
                throw "Nicht abgeschlossene Zeichenfolge in '$SourceName' (Zeile $line)."
            }
            $tokens.Add([pscustomobject]@{
                Kind = 'String'; Value = $Text.Substring($start, $i - $start)
                Start = $start; End = $i
            })
            continue
        }
        if ('{}='.IndexOf($c) -ge 0) {
            $i++
            $tokens.Add([pscustomobject]@{ Kind = 'Symbol'; Value = [string]$c; Start = $start; End = $i })
            continue
        }
        while ($i -lt $Text.Length) {
            $c = $Text[$i]
            if ([char]::IsWhiteSpace($c) -or ('{}=#"'.IndexOf($c) -ge 0)) { break }
            $i++
        }
        $tokens.Add([pscustomobject]@{
            Kind = 'Word'; Value = $Text.Substring($start, $i - $start)
            Start = $start; End = $i
        })
    }
    $openBraces = [Collections.Generic.Stack[int]]::new()
    foreach ($token in $tokens) {
        if ($token.Kind -ne 'Symbol') { continue }
        if ($token.Value -eq '{') { $openBraces.Push([int]$token.Start) }
        if ($token.Value -eq '}') {
            if ($openBraces.Count -eq 0) {
                $line = [regex]::Matches($Text.Substring(0, $token.Start), "`r`n|`r|`n").Count + 1
                throw "Unerwartete schliessende Klammer in '$SourceName' (Zeile $line)."
            }
            $null = $openBraces.Pop()
        }
    }
    if ($openBraces.Count -ne 0) {
        $line = [regex]::Matches($Text.Substring(0, $openBraces.Peek()), "`r`n|`r|`n").Count + 1
        throw "Nicht abgeschlossene Klammer in '$SourceName' (geoeffnet in Zeile $line)."
    }
    return ,$tokens.ToArray()
}

function Get-ClosingBrace {
    param([object[]]$Tokens, [int]$Open)
    $depth = 0
    for ($i = $Open; $i -lt $Tokens.Count; $i++) {
        if ($Tokens[$i].Kind -ne 'Symbol') { continue }
        if ($Tokens[$i].Value -eq '{') { $depth++ }
        if ($Tokens[$i].Value -eq '}') {
            $depth--
            if ($depth -eq 0) { return $i }
        }
    }
    throw 'Klammerpaar wurde nicht gefunden.'
}

function Get-DirectBlock {
    param([object[]]$Tokens, [int]$Open = -1, [int]$Close, [string]$Name)
    $matches = [Collections.Generic.List[object]]::new()
    $i = $Open + 1
    while ($i -lt $Close) {
        if (($Tokens[$i].Kind -eq 'Word') -and ($Tokens[$i].Value -ceq $Name) -and
            (($i + 2) -lt $Close) -and ($Tokens[$i + 1].Value -eq '=') -and
            ($Tokens[$i + 2].Value -eq '{')) {
            $end = Get-ClosingBrace -Tokens $Tokens -Open ($i + 2)
            $matches.Add([pscustomobject]@{ Open = $i + 2; Close = $end })
        }
        if (($Tokens[$i].Kind -eq 'Symbol') -and ($Tokens[$i].Value -eq '{')) {
            $i = (Get-ClosingBrace -Tokens $Tokens -Open $i) + 1
        } else {
            $i++
        }
    }
    if ($matches.Count -ne 1) {
        throw "Erwartet wurde genau ein Block '$Name'; gefunden: $($matches.Count). Keine Dateien wurden im Spiel geaendert."
    }
    return $matches[0]
}

function Get-LitoScriptEntries {
    param([object[]]$Tokens, [int]$Open = -1, [int]$Close = -1)
    if ($Close -lt 0) { $Close = $Tokens.Count }
    $entries = [Collections.Generic.List[object]]::new()
    $i = $Open + 1
    while (($i + 2) -lt $Close) {
        if (($Tokens[$i + 1].Value -eq '=') -and ($Tokens[$i].Kind -in @('Word', 'String'))) {
            $valueIndex = $i + 2
            $isBlock = ($Tokens[$valueIndex].Value -eq '{')
            $end = $valueIndex
            if ($isBlock) { $end = Get-ClosingBrace -Tokens $Tokens -Open $valueIndex }
            $entries.Add([pscustomobject]@{
                Name = $Tokens[$i].Value.Trim('"'); Value = $Tokens[$valueIndex].Value.Trim('"')
                Start = $Tokens[$i].Start; Open = $valueIndex; Close = $end
                IsBlock = $isBlock; End = $Tokens[$end].End
            })
            $i = $end + 1
        } elseif ($Tokens[$i].Value -eq '{') {
            $i = (Get-ClosingBrace -Tokens $Tokens -Open $i) + 1
        } else { $i++ }
    }
    return $entries.ToArray()
}

function Test-LitoLegacyName {
    param([string]$Name)
    # Concrete script identifiers, not comments or translated prose. Covers the
    # historical spellings used by both older Soviet and NSB content.
    return $Name -match '(?i)(paranoi|trotsk|trotzk|SOV_(?:the_)?(?:great_purge|left_opposition|moscow_trials))'
}

function Add-LitoLegacyGuard {
    param([object[]]$Tokens, [object]$Entry, [string]$Field, [object]$Edits, [string]$Newline)
    $children = Get-LitoScriptEntries -Tokens $Tokens -Open $Entry.Open -Close $Entry.Close
    $blocks = @($children | Where-Object { $_.Name -eq $Field -and $_.IsBlock })
    if ($blocks.Count -gt 1) { throw "Mehrere '$Field'-Bloecke in $($Entry.Name); Legacy-Anpassung abgebrochen." }
    $guard = 'NOT = { SOV = { has_country_flag = sr_lito_initialized } }'
    if ($blocks.Count -eq 1) {
        $Edits.Add([pscustomobject]@{ Position = $Tokens[$blocks[0].Open].End; Text = $Newline + '        ' + $guard + $Newline })
    } else {
        $Edits.Add([pscustomobject]@{ Position = $Tokens[$Entry.Open].End; Text = $Newline + '    ' + $Field + ' = { ' + $guard + ' }' + $Newline })
    }
}

function Add-LitoLegacyDecisionGuards {
    param([object[]]$Tokens, [object]$Entry, [object]$Edits, [string]$Newline)
    Add-LitoLegacyGuard -Tokens $Tokens -Entry $Entry -Field 'visible' -Edits $Edits -Newline $Newline
    $children = Get-LitoScriptEntries -Tokens $Tokens -Open $Entry.Open -Close $Entry.Close
    # Active vanilla missions in an existing save must disappear without firing
    # their purge/assassination penalties. Preserve the old cancel condition as
    # the other branch of an OR, and guard every delayed result as well.
    $cancel = @($children | Where-Object { $_.Name -eq 'cancel_trigger' -and $_.IsBlock })
    if ($cancel.Count -gt 1) { throw "Mehrere cancel_trigger in $($Entry.Name)." }
    if ($cancel.Count -eq 1) {
        $Edits.Add([pscustomobject]@{ Position = $Tokens[$cancel[0].Open].End; Text = $Newline + '        OR = { SOV = { has_country_flag = sr_lito_initialized } AND = {' + $Newline })
        $Edits.Add([pscustomobject]@{ Position = $Tokens[$cancel[0].Close].Start; Text = $Newline + '        } }' + $Newline })
    } else {
        $Edits.Add([pscustomobject]@{ Position = $Tokens[$Entry.Open].End; Text = $Newline + '    cancel_trigger = { SOV = { has_country_flag = sr_lito_initialized } }' + $Newline })
    }
    foreach ($result in @($children | Where-Object { $_.IsBlock -and $_.Name -in @('complete_effect', 'remove_effect', 'timeout_effect', 'cancel_effect') })) {
        $Edits.Add([pscustomobject]@{ Position = $Tokens[$result.Open].End; Text = $Newline + '        if = { limit = { NOT = { SOV = { has_country_flag = sr_lito_initialized } } }' + $Newline })
        $Edits.Add([pscustomobject]@{ Position = $Tokens[$result.Close].Start; Text = $Newline + '        }' + $Newline })
    }
}

function Add-LitoLegacyEventEffects {
    param([object[]]$Tokens, [object]$Entry, [object]$Edits, [string]$Newline)
    $children = Get-LitoScriptEntries -Tokens $Tokens -Open $Entry.Open -Close $Entry.Close
    $prefix = $Newline + '        if = { limit = { NOT = { SOV = { has_country_flag = sr_lito_initialized } } }' + $Newline
    $suffix = $Newline + '        }' + $Newline
    # Also protect effects of events already queued in an old save or fired by
    # another effect. The trigger is the first gate; the result gates make a
    # forced historical event harmless even if the engine bypasses that gate.
    foreach ($effect in @($children | Where-Object { $_.IsBlock -and $_.Name -in @('immediate', 'after') })) {
        $Edits.Add([pscustomobject]@{ Position = $Tokens[$effect.Open].End; Text = $prefix })
        $Edits.Add([pscustomobject]@{ Position = $Tokens[$effect.Close].Start; Text = $suffix })
    }
    foreach ($option in @($children | Where-Object { $_.IsBlock -and $_.Name -eq 'option' })) {
        $fields = @(Get-LitoScriptEntries -Tokens $Tokens -Open $option.Open -Close $option.Close)
        $runStart = -1
        $runEnd = -1
        foreach ($field in $fields) {
            if ($field.Name -in @('name', 'trigger', 'ai_chance')) {
                if ($runStart -ge 0) {
                    $Edits.Add([pscustomobject]@{ Position = $runStart; Text = $prefix })
                    $Edits.Add([pscustomobject]@{ Position = $runEnd; Text = $suffix })
                    $runStart = -1
                }
            } else {
                if ($runStart -lt 0) { $runStart = $field.Start }
                $runEnd = $field.End
            }
        }
        if ($runStart -ge 0) {
            $Edits.Add([pscustomobject]@{ Position = $runStart; Text = $prefix })
            $Edits.Add([pscustomobject]@{ Position = $runEnd; Text = $suffix })
        }
    }
    # A harmless exit remains visible if an already queued event is forced
    # open after changing its trigger; no historical option must be selected.
    $exitOption = $Newline + '    option = { name = OK trigger = { SOV = { has_country_flag = sr_lito_initialized } } ai_chance = { base = 100 } }' + $Newline
    $Edits.Add([pscustomobject]@{ Position = $Tokens[$Entry.Close].Start; Text = $exitOption })
}

function Protect-LitoLegacySoviet {
    param([string]$GameRoot, [string]$StagedMod)
    $totals = @{
        Stats = @{ Events = 0; Decisions = 0; Categories = 0; Effects = 0; Guis = 0; Files = 0 }
        Variables = @{}; Flags = @{}; Ideas = @{}; Characters = @{}
    }
    $skippedFiles = [Collections.Generic.List[string]]::new()
    foreach ($relativeFolder in @('events', 'common/decisions', 'common/scripted_effects', 'common/scripted_guis', 'common/ideas', 'common/characters', 'common/on_actions')) {
        $folder = Join-Path $GameRoot $relativeFolder
        if (-not (Test-Path -LiteralPath $folder -PathType Container)) { continue }
        foreach ($gameFile in @(Get-ChildItem -LiteralPath $folder -Filter '*.txt' -File -Recurse)) {
            $relative = $gameFile.FullName.Substring($GameRoot.Length).TrimStart([char[]]'\/')
            $stagedFile = Join-Path $StagedMod $relative
            # Optional historical patches are isolated transactions. Commit
            # discovered IDs and counters only after this file is verified.
            $stats = @{ Events = 0; Decisions = 0; Categories = 0; Effects = 0; Guis = 0; Files = 0 }
            $paranoiaVariables = @{}
            $paranoiaFlags = @{}
            $legacyIdeas = @{}
            $trotskyCharacters = @{}
            try {
            # Respect an explicitly supplied override instead of silently
            # replacing it with a different local vanilla version.
            $readFile = $gameFile.FullName
            if (Test-Path -LiteralPath $stagedFile -PathType Leaf) { $readFile = $stagedFile }
            $bytes = [IO.File]::ReadAllBytes($readFile)
            # Relevant Clausewitz identifiers are ASCII. Skip unrelated files
            # before strict UTF-8 decoding, including old non-UTF8 mod files.
            $asciiPreview = [Text.Encoding]::ASCII.GetString($bytes)
            if (-not (Test-LitoLegacyName -Name ($gameFile.Name + ' ' + $asciiPreview))) { continue }
            $bom = $bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191
            $offset = 0
            if ($bom) { $offset = 3 }
            $text = [Text.UTF8Encoding]::new($false, $true).GetString($bytes, $offset, $bytes.Length - $offset)
            if (-not (Test-LitoLegacyName -Name ($gameFile.Name + ' ' + $text))) { continue }
            $tokens = Get-ClausewitzTokens -Text $text -SourceName $relative
            $entries = Get-LitoScriptEntries -Tokens $tokens
            $edits = [Collections.Generic.List[object]]::new()
            $newline = "`n"
            if ($text.Contains("`r`n")) { $newline = "`r`n" }
            elseif ($text.Contains("`r")) { $newline = "`r" }
            $dedicatedFile = Test-LitoLegacyName -Name $gameFile.BaseName
            # Collect only actually used variable/flag identifiers, never guessed
            # DLC-specific names. Quoted comments and narrative strings do not
            # contribute identifiers to the generated daily cleanup.
            for ($i = 0; ($i + 2) -lt $tokens.Count; $i++) {
                if ($tokens[$i].Kind -ne 'Word' -or $tokens[$i + 1].Value -ne '=') { continue }
                if ($tokens[$i].Value -in @('set_variable', 'add_to_variable', 'subtract_from_variable', 'clamp_variable')) {
                    if ($tokens[$i + 2].Value -ne '{') { continue }
                    $end = Get-ClosingBrace -Tokens $tokens -Open ($i + 2)
                    $varEntries = Get-LitoScriptEntries -Tokens $tokens -Open ($i + 2) -Close $end
                    foreach ($var in $varEntries) {
                        $name = $var.Name
                        if ($name -in @('var', 'variable')) { $name = $var.Value }
                        if ($name -match '(?i)^(?:SOV_\w*paranoi\w*|paranoia|political_paranoia)$') { $paranoiaVariables[$name] = $true }
                    }
                } elseif ($tokens[$i].Value -eq 'set_country_flag') {
                    $name = $tokens[$i + 2].Value.Trim('"')
                    if ($name -eq '{') {
                        $end = Get-ClosingBrace -Tokens $tokens -Open ($i + 2)
                        $flagEntries = Get-LitoScriptEntries -Tokens $tokens -Open ($i + 2) -Close $end
                        $flagEntry = @($flagEntries | Where-Object { $_.Name -eq 'flag' })
                        if ($flagEntry.Count -eq 1) { $name = $flagEntry[0].Value }
                    }
                    if ($name -match '(?i)^SOV_\w*paranoi\w*$' -and $name -notmatch '(?i)(disable|finish|ended|remove|stop|no_paranoia)') { $paranoiaFlags[$name] = $true }
                }
            }
            if ($relativeFolder -eq 'events') {
                foreach ($entry in @($entries | Where-Object { $_.IsBlock -and $_.Name -in @('country_event', 'news_event', 'state_event', 'unit_leader_event', 'operative_leader_event') })) {
                    $fields = Get-LitoScriptEntries -Tokens $tokens -Open $entry.Open -Close $entry.Close
                    $identity = (@($fields | Where-Object { $_.Name -in @('id', 'title', 'desc') -and -not $_.IsBlock } | ForEach-Object { $_.Value }) -join ' ')
                    $bodyTokens = ($tokens[($entry.Open)..($entry.Close)] | Where-Object { $_.Kind -eq 'Word' } | ForEach-Object { $_.Value }) -join ' '
                    if ($dedicatedFile -or (Test-LitoLegacyName -Name ($identity + ' ' + $bodyTokens))) {
                        Add-LitoLegacyGuard -Tokens $tokens -Entry $entry -Field 'trigger' -Edits $edits -Newline $newline
                        Add-LitoLegacyEventEffects -Tokens $tokens -Entry $entry -Edits $edits -Newline $newline
                        $stats.Events++
                    }
                }
            } elseif ($relativeFolder -eq 'common/decisions') {
                $categoryFile = $relative.Replace('\', '/') -match '/categories/'
                foreach ($category in @($entries | Where-Object { $_.IsBlock })) {
                    if ($categoryFile) {
                        if ($dedicatedFile -or (Test-LitoLegacyName -Name $category.Name)) {
                            Add-LitoLegacyGuard -Tokens $tokens -Entry $category -Field 'visible' -Edits $edits -Newline $newline
                            $stats.Categories++
                        }
                    } else {
                        $categoryLegacy = $dedicatedFile -or (Test-LitoLegacyName -Name $category.Name)
                        foreach ($decision in @(Get-LitoScriptEntries -Tokens $tokens -Open $category.Open -Close $category.Close | Where-Object { $_.IsBlock })) {
                            $bodyWords = ($tokens[($decision.Open)..($decision.Close)] | Where-Object { $_.Kind -eq 'Word' } | ForEach-Object { $_.Value }) -join ' '
                            if ($categoryLegacy -or (Test-LitoLegacyName -Name ($decision.Name + ' ' + $bodyWords))) {
                                Add-LitoLegacyDecisionGuards -Tokens $tokens -Entry $decision -Edits $edits -Newline $newline
                                $stats.Decisions++
                            }
                        }
                    }
                }
            } elseif ($relativeFolder -eq 'common/scripted_effects') {
                foreach ($entry in @($entries | Where-Object { $_.IsBlock })) {
                    if (Test-LitoLegacyName -Name $entry.Name) {
                        $edits.Add([pscustomobject]@{ Position = $tokens[$entry.Open].End; Text = $newline + '    if = { limit = { NOT = { SOV = { has_country_flag = sr_lito_initialized } } }' + $newline })
                        $edits.Add([pscustomobject]@{ Position = $tokens[$entry.Close].Start; Text = $newline + '    }' + $newline })
                        $stats.Effects++
                    }
                }
            } elseif ($relativeFolder -eq 'common/scripted_guis') {
                foreach ($root in @($entries | Where-Object { $_.Name -eq 'scripted_gui' -and $_.IsBlock })) {
                    foreach ($entry in @(Get-LitoScriptEntries -Tokens $tokens -Open $root.Open -Close $root.Close | Where-Object { $_.IsBlock })) {
                        $bodyWords = ($tokens[($entry.Open)..($entry.Close)] | Where-Object { $_.Kind -eq 'Word' } | ForEach-Object { $_.Value }) -join ' '
                        if ((Test-LitoLegacyName -Name $entry.Name) -or (Test-LitoLegacyName -Name $bodyWords)) {
                            Add-LitoLegacyGuard -Tokens $tokens -Entry $entry -Field 'visible' -Edits $edits -Newline $newline
                            $stats.Guis++
                        }
                    }
                }
            } elseif ($relativeFolder -eq 'common/ideas') {
                foreach ($root in @($entries | Where-Object { $_.Name -eq 'ideas' -and $_.IsBlock })) {
                    foreach ($group in @(Get-LitoScriptEntries -Tokens $tokens -Open $root.Open -Close $root.Close | Where-Object { $_.IsBlock })) {
                        foreach ($idea in @(Get-LitoScriptEntries -Tokens $tokens -Open $group.Open -Close $group.Close | Where-Object { $_.IsBlock })) {
                            if ($idea.Name -match '(?i)^SOV_' -and (Test-LitoLegacyName -Name $idea.Name)) { $legacyIdeas[$idea.Name] = $true }
                        }
                    }
                }
            } elseif ($relativeFolder -eq 'common/characters') {
                foreach ($root in @($entries | Where-Object { $_.Name -eq 'characters' -and $_.IsBlock })) {
                    foreach ($character in @(Get-LitoScriptEntries -Tokens $tokens -Open $root.Open -Close $root.Close | Where-Object { $_.IsBlock })) {
                        $fields = Get-LitoScriptEntries -Tokens $tokens -Open $character.Open -Close $character.Close
                        $nameFields = @($fields | Where-Object { $_.Name -eq 'name' -and -not $_.IsBlock } | ForEach-Object { $_.Value }) -join ' '
                        if ($character.Name -match '^SOV_' -and ($character.Name + ' ' + $nameFields) -match '(?i)(trotsk|trotzk)') { $trotskyCharacters[$character.Name] = $true }
                    }
                }
            }
            if ($edits.Count -gt 0) {
                $changed = $text
                $applied = @($edits | Sort-Object -Property Position -Descending)
                foreach ($edit in $applied) { $changed = $changed.Insert($edit.Position, $edit.Text) }
                # The patch is insertion-only. Removing those exact insertions
                # must recover every original character, including comments.
                $recovered = $changed
                for ($n = $applied.Count - 1; $n -ge 0; $n--) {
                    $edit = $applied[$n]
                    if ($recovered.Substring($edit.Position, $edit.Text.Length) -cne $edit.Text) { throw 'Legacy-Patch konnte nicht verlustfrei geprueft werden.' }
                    $recovered = $recovered.Remove($edit.Position, $edit.Text.Length)
                }
                if ($recovered -cne $text) { throw 'Legacy-Patch wuerde fremden Spielinhalt veraendern.' }
                $null = Get-ClausewitzTokens -Text $changed -SourceName "$relative (vorbereitete Modkopie)"
                New-Item -ItemType Directory -Path (Split-Path -Parent $stagedFile) -Force | Out-Null
                [IO.File]::WriteAllText($stagedFile, $changed, [Text.UTF8Encoding]::new($bom))
                $stats.Files++
            }
            foreach ($key in $stats.Keys) { $totals.Stats[$key] += $stats[$key] }
            foreach ($name in $paranoiaVariables.Keys) { $totals.Variables[$name] = $true }
            foreach ($name in $paranoiaFlags.Keys) { $totals.Flags[$name] = $true }
            foreach ($name in $legacyIdeas.Keys) { $totals.Ideas[$name] = $true }
            foreach ($name in $trotskyCharacters.Keys) { $totals.Characters[$name] = $true }
            } catch {
                # Disk/permission failures still abort safely in staging.
                $cause = $_.Exception
                while ($null -ne $cause) {
                    if ($cause -is [IO.IOException] -or $cause -is [UnauthorizedAccessException]) { throw }
                    $cause = $cause.InnerException
                }
                $skippedFiles.Add($relative)
                Write-Warning "Optionale Paranoia-/Trotzki-Anpassung uebersprungen: $relative. $($_.Exception.Message)"
            }
        }
    }
    $stats = $totals.Stats
    $paranoiaVariables = $totals.Variables
    $paranoiaFlags = $totals.Flags
    $legacyIdeas = $totals.Ideas
    $trotskyCharacters = $totals.Characters
    if ($stats.Files -gt 0 -or $paranoiaVariables.Count -gt 0 -or $legacyIdeas.Count -gt 0 -or $trotskyCharacters.Count -gt 0) {
        $cleanup = "on_actions = {`n    on_daily = {`n        effect = {`n            if = {`n                limit = { tag = SOV has_country_flag = sr_lito_initialized }`n"
        foreach ($name in @($paranoiaVariables.Keys | Sort-Object)) { $cleanup += "                set_variable = { $name = 0 }`n" }
        foreach ($name in @($paranoiaFlags.Keys | Sort-Object)) { $cleanup += "                clr_country_flag = $name`n" }
        foreach ($name in @($legacyIdeas.Keys | Sort-Object)) { $cleanup += "                remove_ideas = $name`n" }
        foreach ($name in @($trotskyCharacters.Keys | Sort-Object)) { $cleanup += "                if = { limit = { has_character = $name } retire_character = $name }`n" }
        $cleanup += "            }`n        }`n    }`n}`n"
        $onActions = Join-Path $StagedMod 'common/on_actions'
        New-Item -ItemType Directory -Path $onActions -Force | Out-Null
        [IO.File]::WriteAllText((Join-Path $onActions 'zz_sr_legacy_soviet_shutdown.txt'), $cleanup, [Text.UTF8Encoding]::new($false))
    }
    Write-Host ("Historische Paranoia/Trotzki fuer Lito angepasst: {0} Ereignisse, {1} Entscheidungen, {2} Kategorien, {3} Effekte, {4} Anzeigen; {5} lokale Dateikopien." -f $stats.Events, $stats.Decisions, $stats.Categories, $stats.Effects, $stats.Guis, $stats.Files)
    if ($skippedFiles.Count -gt 0) {
        Write-Warning ("Paranoia/Trotzki nur teilweise gesperrt: {0} optionale Datei(en) konnten nicht angepasst werden. Die oben genannten Dateipfade fuer die Fehleranalyse aufbewahren." -f $skippedFiles.Count)
    }
}

function Find-GamePath {
    param([string]$ExplicitPath)
    if (-not [string]::IsNullOrWhiteSpace($ExplicitPath)) {
        $resolved = (Resolve-Path -LiteralPath $ExplicitPath).Path
        if (-not (Test-Path -LiteralPath (Join-Path $resolved 'common\ideologies\00_ideologies.txt') -PathType Leaf)) {
            throw "Kein HOI4-Spielordner: $resolved. Erwartet: common\ideologies\00_ideologies.txt"
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
        $vdf = Join-Path $steamRoot 'steamapps\libraryfolders.vdf'
        if (Test-Path -LiteralPath $vdf -PathType Leaf) {
            $text = [IO.File]::ReadAllText($vdf)
            foreach ($match in [regex]::Matches($text, '"path"\s+"([^"\r\n]+)"')) {
                $libraries.Add($match.Groups[1].Value.Replace('\\', '\'))
            }
        }
    }
    foreach ($library in ($libraries | Select-Object -Unique)) {
        $candidate = Join-Path $library 'steamapps\common\Hearts of Iron IV'
        if (Test-Path -LiteralPath (Join-Path $candidate 'common\ideologies\00_ideologies.txt') -PathType Leaf) {
            return (Resolve-Path -LiteralPath $candidate).Path.TrimEnd([char[]]'\/')
        }
    }
    throw "HOI4 wurde nicht gefunden. Erneut ausfuehren mit -GamePath 'D:\SteamLibrary\steamapps\common\Hearts of Iron IV' und den tatsaechlichen Spielordner einsetzen."
}

$gameRoot = Find-GamePath -ExplicitPath $GamePath
$sourceMod = Join-Path ([IO.Path]::GetFullPath($SourceRoot)) 'soviet_renewal'
if (-not (Test-Path -LiteralPath (Join-Path $sourceMod 'descriptor.mod') -PathType Leaf)) {
    throw "Moddateien fehlen: $sourceMod. Das Skript muss zusammen mit dem vollstaendig entpackten Projekt vorliegen; alternativ -SourceRoot angeben."
}
$destinationRoot = [IO.Path]::GetFullPath($ModDirectory).TrimEnd([char[]]'\/')
if (($destinationRoot -ieq $gameRoot) -or
    $destinationRoot.StartsWith($gameRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Der Modordner darf nicht innerhalb der Spielinstallation liegen. Die Spielinstallation wird nur gelesen.'
}
$targetMod = Join-Path $destinationRoot 'soviet_renewal'
$targetDescriptor = Join-Path $destinationRoot 'soviet_renewal.mod'
if ((Test-Path -LiteralPath $targetMod) -and (-not (Test-Path -LiteralPath $targetMod -PathType Container))) {
    throw "Am vorgesehenen Modordner liegt eine Datei: $targetMod"
}
if ((Test-Path -LiteralPath $targetDescriptor) -and (-not (Test-Path -LiteralPath $targetDescriptor -PathType Leaf))) {
    throw "Am vorgesehenen Deskriptorpfad liegt ein Ordner: $targetDescriptor"
}

$ideologyPath = Join-Path $gameRoot 'common\ideologies\00_ideologies.txt'
$originalBytes = [IO.File]::ReadAllBytes($ideologyPath)
$hasBom = ($originalBytes.Length -ge 3) -and ($originalBytes[0] -eq 239) -and
    ($originalBytes[1] -eq 187) -and ($originalBytes[2] -eq 191)
$utf8 = [Text.UTF8Encoding]::new($false, $true)
$offset = 0
if ($hasBom) { $offset = 3 }
$original = $utf8.GetString($originalBytes, $offset, $originalBytes.Length - $offset)
$tokens = Get-ClausewitzTokens -Text $original -SourceName $ideologyPath
foreach ($token in $tokens) {
    if (($token.Value -ieq 'titoism') -or ($token.Value -ieq '"titoism"')) {
        throw 'Die installierte Ideologiedatei enthaelt bereits titoism. Abbruch, damit keine andere Definition ueberschrieben wird.'
    }
}
$ideologies = Get-DirectBlock -Tokens $tokens -Close $tokens.Count -Name 'ideologies'
$communism = Get-DirectBlock -Tokens $tokens -Open $ideologies.Open -Close $ideologies.Close -Name 'communism'
$types = Get-DirectBlock -Tokens $tokens -Open $communism.Open -Close $communism.Close -Name 'types'
$newline = "`n"
if ($original.Contains("`r`n")) { $newline = "`r`n" }
elseif ($original.Contains("`r")) { $newline = "`r" }
$insertion = $newline + '            titoism = { can_be_randomly_selected = no }' + $newline
$prepared = $original.Insert($tokens[$types.Open].End, $insertion)
$preparedTokens = Get-ClausewitzTokens -Text $prepared -SourceName "$ideologyPath (vorbereitete Modkopie)"
$checkRoot = Get-DirectBlock -Tokens $preparedTokens -Close $preparedTokens.Count -Name 'ideologies'
$checkCommunism = Get-DirectBlock -Tokens $preparedTokens -Open $checkRoot.Open -Close $checkRoot.Close -Name 'communism'
$checkTypes = Get-DirectBlock -Tokens $preparedTokens -Open $checkCommunism.Open -Close $checkCommunism.Close -Name 'types'
$null = Get-DirectBlock -Tokens $preparedTokens -Open $checkTypes.Open -Close $checkTypes.Close -Name 'titoism'
if ($prepared.Remove($tokens[$types.Open].End, $insertion.Length) -cne $original) {
    throw 'Die Vollstaendigkeit der uebernommenen Ideologiedatei konnte nicht bestaetigt werden.'
}

$portraitFolder = Join-Path $gameRoot 'gfx\leaders\Europe'
$portraits = @(Get-ChildItem -LiteralPath $portraitFolder -File -Filter '*.dds' |
    Where-Object { $_.Name -match '(?i)generic' } | Sort-Object Name)
if ($portraits.Count -eq 0) {
    throw "Kein generisches Europa-Portraet gefunden: $portraitFolder. Es wurden keine Moddateien installiert."
}
$civilianPortraits = @($portraits | Where-Object { $_.Name -notmatch '(?i)(land|navy|army)' })
$portrait = $portraits[0]
if ($civilianPortraits.Count -gt 0) { $portrait = $civilianPortraits[0] }
$portraitRelative = $portrait.FullName.Substring($gameRoot.Length).TrimStart([char[]]'\/').Replace('\', '/')

$workDirectory = Join-Path ([IO.Path]::GetTempPath()) ('lito-install-' + [guid]::NewGuid().ToString('N'))
$stagedMod = Join-Path $workDirectory 'soviet_renewal'
$stamp = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
$backupMod = $targetMod + '.backup-' + $stamp
$backupDescriptor = $targetDescriptor + '.backup-' + $stamp
$oldModMoved = $false
$oldDescriptorMoved = $false
$newModStarted = $false
$newDescriptorStarted = $false
try {
    New-Item -ItemType Directory -Path $workDirectory | Out-Null
    Copy-Item -LiteralPath $sourceMod -Destination $stagedMod -Recurse
    Protect-LitoLegacySoviet -GameRoot $gameRoot -StagedMod $stagedMod
    $nativeAgitpropModule = Join-Path $SourceRoot 'tools/install_native_agitprop.ps1'
    $nativeAgitpropGuiModule = Join-Path $SourceRoot 'tools/install_native_agitprop_gui.ps1'
    if ((Test-Path -LiteralPath $nativeAgitpropModule -PathType Leaf) -and
        (Test-Path -LiteralPath $nativeAgitpropGuiModule -PathType Leaf)) {
        . ([ScriptBlock]::Create([IO.File]::ReadAllText($nativeAgitpropGuiModule, [Text.Encoding]::UTF8)))
        . ([ScriptBlock]::Create([IO.File]::ReadAllText($nativeAgitpropModule, [Text.Encoding]::UTF8)))
        $null = Install-LitoNativeAgitprop -GameRoot $gameRoot -StagedMod $stagedMod
    }
    # Cosmetic tags need their own flag filenames. Reuse local national assets
    # until custom art is supplied. Normal flags live directly in gfx/flags.
    foreach ($flagSize in @(
        @{ Name = 'normal'; RelativePath = 'gfx\flags' },
        @{ Name = 'medium'; RelativePath = 'gfx\flags\medium' },
        @{ Name = 'small'; RelativePath = 'gfx\flags\small' }
    )) {
        foreach ($flagCountry in @(
            @{ OriginalTag = 'SOV'; CosmeticTag = 'SOV_LITO_SFSU' },
            @{ OriginalTag = 'YUG'; CosmeticTag = 'YUG_LITO_BALKAN' }
        )) {
            $stagedFlagDirectory = Join-Path $stagedMod $flagSize.RelativePath
            $cosmeticTag = $flagCountry.CosmeticTag
            $neededFlags = @(@("$cosmeticTag.tga", "${cosmeticTag}_communism.tga") | Where-Object {
                -not (Test-Path -LiteralPath (Join-Path $stagedFlagDirectory $_))
            })
            if ($neededFlags.Count -eq 0) { continue }
            $gameFlagDirectory = Join-Path $gameRoot $flagSize.RelativePath
            $sourceFlag = $null
            $originalTag = $flagCountry.OriginalTag
            foreach ($candidateName in @("${originalTag}_communism.tga", "$originalTag.tga")) {
                $candidateFlag = Join-Path $gameFlagDirectory $candidateName
                if (Test-Path -LiteralPath $candidateFlag -PathType Leaf) {
                    $sourceFlag = $candidateFlag
                    break
                }
            }
            if ($null -eq $sourceFlag) {
                Write-Warning "Keine $originalTag-Flagge ($($flagSize.Name)) in $gameFlagDirectory gefunden. Platzhalter fuer $cosmeticTag fehlen in dieser Groesse; vorhandene eigene Flaggen bleiben erhalten."
                continue
            }
            New-Item -ItemType Directory -Path $stagedFlagDirectory -Force | Out-Null
            foreach ($flagName in $neededFlags) {
                Copy-Item -LiteralPath $sourceFlag -Destination (Join-Path $stagedFlagDirectory $flagName)
            }
        }
    }
    $stagedIdeologies = Join-Path $stagedMod 'common\ideologies'
    $stagedInterface = Join-Path $stagedMod 'interface'
    New-Item -ItemType Directory -Path $stagedIdeologies -Force | Out-Null
    New-Item -ItemType Directory -Path $stagedInterface -Force | Out-Null
    [IO.File]::WriteAllText((Join-Path $stagedIdeologies '00_ideologies.txt'), $prepared, [Text.UTF8Encoding]::new($hasBom))
    # Supplied portrait definitions, including Lito's custom photo, take priority.
    # Only add missing fallback names; never redefine a supplied custom sprite.
    $suppliedSprites = @{}
    foreach ($gfxFile in @(Get-ChildItem -LiteralPath $stagedInterface -Filter '*.gfx' -File -Recurse)) {
        $gfxText = [IO.File]::ReadAllText($gfxFile.FullName)
        foreach ($spriteName in @('GFX_sr_lito_portrait', 'GFX_sr_balkan_council_portrait', 'GFX_sr_kardelj_portrait')) {
            if ($gfxText -match ('(?m)^[ \t]*name[ \t]*=[ \t]*"?' + [regex]::Escape($spriteName) + '"?[ \t]*(?:#.*)?$')) {
                $suppliedSprites[$spriteName] = $true
            }
        }
    }
    $sprite = "spriteTypes = {`n"
    foreach ($spriteName in @('GFX_sr_lito_portrait', 'GFX_sr_balkan_council_portrait', 'GFX_sr_kardelj_portrait')) {
        if (-not $suppliedSprites.ContainsKey($spriteName)) {
            $spritePortrait = $portraitRelative
            if ($spriteName -eq 'GFX_sr_kardelj_portrait') {
                $yugoslavPortraitFolder = Join-Path $gameRoot 'gfx\leaders\YUG'
                if (Test-Path -LiteralPath $yugoslavPortraitFolder -PathType Container) {
                    $kardeljPortraits = @(Get-ChildItem -LiteralPath $yugoslavPortraitFolder -File -Filter '*.dds' |
                        Where-Object { $_.Name -match '(?i)kardelj' } | Sort-Object Name)
                    if ($kardeljPortraits.Count -gt 0) {
                        $spritePortrait = $kardeljPortraits[0].FullName.Substring($gameRoot.Length).TrimStart([char[]]'\/').Replace('\', '/')
                    }
                }
            }
            $sprite += "    spriteType = {`n        name = `"$spriteName`"`n        texturefile = `"$spritePortrait`"`n    }`n"
        }
    }
    $sprite += "}`n"
    $fallbackSpriteFile = Join-Path $stagedInterface 'sr_lito_portrait.gfx'
    if (Test-Path -LiteralPath $fallbackSpriteFile) {
        $fallbackSpriteFile = Join-Path $stagedInterface 'sr_generated_portrait_fallbacks.gfx'
    }
    [IO.File]::WriteAllText($fallbackSpriteFile, $sprite, $utf8)
    $descriptor = [IO.File]::ReadAllText((Join-Path $stagedMod 'descriptor.mod'))
    if ($descriptor -match '(?m)^\s*replace_path\s*=') {
        throw 'Der Quelldeskriptor enthaelt replace_path. Bitte vor der Installation pruefen.'
    }
    $descriptor = [regex]::Replace($descriptor, '(?m)^[ \t]*path[ \t]*=[^\r\n]*(?:\r?\n|$)', '')
    $descriptor = $descriptor.TrimEnd() + "`r`npath=`"" + $targetMod.Replace('\', '/') + "`"`r`n"
    $stagedDescriptor = Join-Path $workDirectory 'soviet_renewal.mod'
    [IO.File]::WriteAllText($stagedDescriptor, $descriptor, $utf8)
    if (-not (Test-Path -LiteralPath (Join-Path $stagedMod 'common\characters') -PathType Container)) {
        throw 'Im Quellpaket fehlt common\characters. Bitte das Lito-Paket verwenden.'
    }

    New-Item -ItemType Directory -Path $destinationRoot -Force | Out-Null
    try {
        if (Test-Path -LiteralPath $targetMod) {
            Move-Item -LiteralPath $targetMod -Destination $backupMod
            $oldModMoved = $true
        }
        if (Test-Path -LiteralPath $targetDescriptor) {
            Move-Item -LiteralPath $targetDescriptor -Destination $backupDescriptor
            $oldDescriptorMoved = $true
        }
        $newModStarted = $true
        Copy-Item -LiteralPath $stagedMod -Destination $targetMod -Recurse
        $newDescriptorStarted = $true
        Copy-Item -LiteralPath $stagedDescriptor -Destination $targetDescriptor
        if ([IO.File]::ReadAllText((Join-Path $targetMod 'common\ideologies\00_ideologies.txt')) -cne $prepared) {
            throw 'Die installierte Ideologiedatei stimmt nicht mit der Vorbereitung ueberein.'
        }
    } catch {
        $installationError = $_
        try {
            if ($newDescriptorStarted -and (Test-Path -LiteralPath $targetDescriptor)) {
                Remove-Item -LiteralPath $targetDescriptor -Force
            }
            if ($oldDescriptorMoved) { Move-Item -LiteralPath $backupDescriptor -Destination $targetDescriptor }
        } catch { Write-Warning "Deskriptor nicht automatisch wiederhergestellt. Sicherung: $backupDescriptor. $($_.Exception.Message)" }
        try {
            if ($newModStarted -and (Test-Path -LiteralPath $targetMod)) {
                Remove-Item -LiteralPath $targetMod -Recurse -Force
            }
            if ($oldModMoved) { Move-Item -LiteralPath $backupMod -Destination $targetMod }
        } catch { Write-Warning "Modordner nicht automatisch wiederhergestellt. Sicherung: $backupMod. $($_.Exception.Message)" }
        throw $installationError
    }
    Write-Host "Lito-Mod installiert: $targetMod" -ForegroundColor Green
    Write-Host 'Die Spielinstallation blieb unveraendert. Titoismus wurde ausschliesslich in der Mod ergaenzt.'
    if ($oldModMoved) { Write-Host "Vorheriger Modordner: $backupMod" }
    if ($oldDescriptorMoved) { Write-Host "Vorheriger Deskriptor: $backupDescriptor" }
    Write-Host 'Im Launcher aktivieren und eine NEUE Partie starten. Nach HOI4-Updates dieses Skript erneut ausfuehren.'
} finally {
    try {
        if (Test-Path -LiteralPath $workDirectory) { Remove-Item -LiteralPath $workDirectory -Recurse -Force }
    } catch {
        Write-Warning "Temporaere Dateien konnten nicht entfernt werden: $workDirectory. $($_.Exception.Message)"
    }
}
