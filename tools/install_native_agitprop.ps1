# Build the Lito-to-Vanilla Agitprop bridge from the user's installed game.
# No original game source is embedded here, and the game directory is read-only.
function Install-LitoNativeAgitprop {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$GameRoot,
          [Parameter(Mandatory = $true)][string]$StagedMod)

    $transactionRoot = $null
    $workMod = $null
    $committed = [Collections.Generic.List[object]]::new()
    $rollbackError = $null
    $utf8Strict = [Text.UTF8Encoding]::new($false, $true)

    function Read-LitoNativeSource {
        param([string]$Relative)
        $path = Join-Path $StagedMod $Relative
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { $path = Join-Path $GameRoot $Relative }
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Originaldatei fehlt: $Relative" }
        $bytes = [IO.File]::ReadAllBytes($path)
        $bom = $bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191
        $offset = 0; if ($bom) { $offset = 3 }
        $text = $utf8Strict.GetString($bytes, $offset, $bytes.Length - $offset)
        $tokens = Get-ClausewitzTokens -Text $text -SourceName $Relative
        return [pscustomobject]@{ Relative = $Relative; Text = $text; Tokens = $tokens; Bom = $bom }
    }

    function Get-LitoNativeChildren {
        param([object]$Source, [object]$Entry)
        return @(Get-LitoScriptEntries -Tokens $Source.Tokens -Open $Entry.Open -Close $Entry.Close)
    }

    function Get-LitoNativeRoot {
        param([object]$Source, [string]$Name)
        $found = @(Get-LitoScriptEntries -Tokens $Source.Tokens | Where-Object { $_.Name -ceq $Name -and $_.IsBlock })
        if ($found.Count -ne 1) { throw "Erwartet genau ein '$Name' in $($Source.Relative), gefunden: $($found.Count)." }
        return $found[0]
    }

    function Get-LitoNativeChild {
        param([object]$Source, [object]$Entry, [string]$Name)
        $found = @(Get-LitoNativeChildren -Source $Source -Entry $Entry | Where-Object { $_.Name -ceq $Name })
        if ($found.Count -ne 1) { throw "Erwartet genau ein '$Name' in $($Entry.Name), gefunden: $($found.Count)." }
        return $found[0]
    }

    function New-LitoNativeAlias {
        param([string]$Original)
        $extra = ''
        if ($Original -ceq 'SOV_collectivist_propaganda') { $extra = ' has_completed_focus = sr_lito_workers_councils' }
        elseif ($Original -ceq 'SOV_the_komsomol') { $extra = ' has_completed_focus = sr_lito_academy_network' }
        return ('OR = { has_completed_focus = ' + $Original +
            ' AND = { tag = SOV has_country_flag = sr_lito_initialized has_country_flag = sr_lito_native_agitprop_ready has_country_flag = sr_lito_native_agitprop_unlocked' + $extra + ' } }')
    }

    function Add-LitoNativeAliases {
        param([object]$Source, [object]$Entry, [object]$Edits, [object]$Counts, [bool]$Negative = $false)
        foreach ($field in @(Get-LitoNativeChildren -Source $Source -Entry $Entry)) {
            if ($field.IsBlock) {
                $snippet = $Source.Text.Substring($field.Start, $field.End - $field.Start)
                $alreadyPatched = $false
                foreach ($key in @('SOV_expand_the_agitprop', 'SOV_collectivist_propaganda', 'SOV_the_komsomol')) {
                    if ($snippet -ceq (New-LitoNativeAlias -Original $key)) {
                        $Counts[$key] = [int]$Counts[$key] + 1
                        $alreadyPatched = $true
                        break
                    }
                }
                if (-not $alreadyPatched) {
                    Add-LitoNativeAliases -Source $Source -Entry $field -Edits $Edits -Counts $Counts -Negative ($Negative -or $field.Name -ieq 'NOT')
                }
            } elseif (-not $Negative -and $field.Name -ceq 'has_completed_focus' -and
                $field.Value -cin @('SOV_expand_the_agitprop', 'SOV_collectivist_propaganda', 'SOV_the_komsomol')) {
                $Edits.Add([pscustomobject]@{ Start = $field.Start; End = $field.End; Text = (New-LitoNativeAlias -Original $field.Value) })
                $Counts[$field.Value] = [int]$Counts[$field.Value] + 1
            }
        }
    }

    function Write-LitoNativePatched {
        param([object]$Source, [object]$Edits)
        $text = $Source.Text
        foreach ($edit in @($Edits | Sort-Object Start -Descending)) {
            $text = $text.Remove($edit.Start, $edit.End - $edit.Start).Insert($edit.Start, $edit.Text)
        }
        $null = Get-ClausewitzTokens -Text $text -SourceName ($Source.Relative + ' (Lito-Modkopie)')
        $path = Join-Path $workMod $Source.Relative
        New-Item -ItemType Directory -Path (Split-Path -Parent $path) -Force | Out-Null
        [IO.File]::WriteAllText($path, $text, [Text.UTF8Encoding]::new($Source.Bom))
    }

    try {
        $GameRoot = [IO.Path]::GetFullPath($GameRoot).TrimEnd([char[]]'\/')
        $StagedMod = [IO.Path]::GetFullPath($StagedMod).TrimEnd([char[]]'\/')
        if (-not (Test-Path -LiteralPath $StagedMod -PathType Container)) { throw 'Der vorbereitete Modordner fehlt.' }

        $categories = Read-LitoNativeSource 'common/decisions/categories/SOV_decision_categories.txt'
        $decisions = Read-LitoNativeSource 'common/decisions/SOV.txt'
        $effects = Read-LitoNativeSource 'common/scripted_effects/SOV_scripted_effects.txt'
        $history = Read-LitoNativeSource 'history/countries/SOV - Soviet union.txt'
        $originalFocus = Read-LitoNativeSource 'common/national_focus/soviet.txt'
        $scriptedGui = Read-LitoNativeSource 'common/scripted_guis/SOV_propaganda_campaigns_scripted_gui.txt'
        $graphics = Read-LitoNativeSource 'interface/propaganda.gfx'
        $guiRelative = 'interface/sov_propaganda_campaigns_scripted_gui.gui'
        if (-not (Test-Path -LiteralPath (Join-Path $StagedMod $guiRelative) -PathType Leaf) -and
            -not (Test-Path -LiteralPath (Join-Path $GameRoot $guiRelative) -PathType Leaf)) { throw "Originaldatei fehlt: $guiRelative" }

        foreach ($name in @('SOV_pick_propaganda_campaign_slot_effect', 'SOV_reset_propaganda_campaign_slot_effect',
                'SOV_unlock_propaganda_campaign_slot_effect', 'SOV_increase_propaganda_campaign_cost_effect')) {
            $null = Get-LitoNativeRoot -Source $effects -Name $name
        }
        $category = Get-LitoNativeRoot -Source $categories -Name 'SOV_propaganda_campaigns'
        if ((Get-LitoNativeChild -Source $categories -Entry $category -Name 'scripted_gui').Value -cne 'sov_propaganda_campaigns_ui') {
            throw 'Die originale Agitprop-Kategorie verwendet eine unbekannte Scripted-GUI.'
        }
        $guiRoot = Get-LitoNativeRoot -Source $scriptedGui -Name 'scripted_gui'
        $gui = Get-LitoNativeChild -Source $scriptedGui -Entry $guiRoot -Name 'sov_propaganda_campaigns_ui'
        if ((Get-LitoNativeChild -Source $scriptedGui -Entry $gui -Name 'context_type').Value -cne 'decision_category' -or
            (Get-LitoNativeChild -Source $scriptedGui -Entry $gui -Name 'window_name').Value -cne 'sov_propaganda_campaigns_ui_window') {
            throw 'Die originale Agitprop-GUI hat einen unbekannten Kontext oder Fensternamen.'
        }
        $spriteRoot = Get-LitoNativeRoot -Source $graphics -Name 'spriteTypes'
        foreach ($name in @('GFX_propaganda_bg', 'GFX_SOV_propaganda_strip', 'GFX_SOV_propaganda_strip_aged_1',
                'GFX_SOV_propaganda_strip_aged_2', 'GFX_SOV_propaganda_strip_aged_3')) {
            $foundSprites = @(Get-LitoNativeChildren -Source $graphics -Entry $spriteRoot | Where-Object {
                $_.IsBlock -and (Get-LitoNativeChild -Source $graphics -Entry $_ -Name 'name').Value -ceq $name
            })
            if ($foundSprites.Count -ne 1) { throw "Native Agitprop-Grafik '$name' ist nicht eindeutig registriert." }
            if ($name -cne 'GFX_propaganda_bg' -and
                (Get-LitoNativeChild -Source $graphics -Entry $foundSprites[0] -Name 'noOfFrames').Value -cne '26') {
                throw "Die native Posterleiste '$name' hat eine unbekannte Frame-Anzahl."
            }
        }

        $tree = Get-LitoNativeRoot -Source $originalFocus -Name 'focus_tree'
        $expand = @(Get-LitoNativeChildren -Source $originalFocus -Entry $tree | Where-Object {
            $_.Name -ceq 'focus' -and $_.IsBlock -and
            (Get-LitoNativeChild -Source $originalFocus -Entry $_ -Name 'id').Value -ceq 'SOV_expand_the_agitprop'
        })
        if ($expand.Count -ne 1) { throw 'Der originale Freischaltfokus SOV_expand_the_agitprop fehlt oder ist mehrfach vorhanden.' }
        $reward = Get-LitoNativeChild -Source $originalFocus -Entry $expand[0] -Name 'completion_reward'
        $unlockCalls = 0
        for ($i = $reward.Open + 1; $i + 2 -lt $reward.Close; $i++) {
            if ($originalFocus.Tokens[$i].Value -ceq 'SOV_unlock_propaganda_campaign_slot_effect' -and
                $originalFocus.Tokens[$i + 1].Value -ceq '=' -and $originalFocus.Tokens[$i + 2].Value -ceq 'yes') { $unlockCalls++ }
        }
        if ($unlockCalls -ne 1) { throw 'Der originale Agitprop-Fokus hat einen unbekannten Slot-Freischaltvertrag.' }

        $defaults = [Collections.Generic.List[object]]::new()
        $values = @{}
        foreach ($entry in @(Get-LitoScriptEntries -Tokens $history.Tokens)) {
            if ($entry.Name -cne 'set_variable' -or -not $entry.IsBlock) { continue }
            $fields = @(Get-LitoNativeChildren -Source $history -Entry $entry)
            if ($fields.Count -ne 1 -or $fields[0].IsBlock -or $fields[0].Name -cnotmatch '^SOV_(?:new_propaganda_campaign|propaganda_[A-Za-z0-9_]+|poster_(?:left|center|right)_icon_frame|default_propaganda_[A-Za-z0-9_]+)$') { continue }
            $variable = $fields[0].Name; $value = $fields[0].Value
            if ($values.ContainsKey($variable)) { throw "Mehrere Startwerte fuer $variable in der nativen Laendergeschichte." }
            if ($value -notmatch '^-?\d+(?:\.\d+)?$' -and -not $values.ContainsKey($value)) {
                throw "Unbekannte Startwert-Abhaengigkeit $variable = $value."
            }
            $values[$variable] = $value
            $defaults.Add([pscustomobject]@{ Name = $variable; Text = $history.Text.Substring($entry.Start, $entry.End - $entry.Start) })
        }
        $expected = @{
            SOV_propaganda_locked_slot_index = '1'; SOV_propaganda_empty_slot_index = '2'
            SOV_default_propaganda_campaign_duration = '180'; SOV_default_propaganda_campaign_cooldown = '90'
            SOV_default_propaganda_campaign_old_days = '150'; SOV_propaganda_cost = '15'; SOV_propaganda_cost_increase = '2'
        }
        foreach ($name in $expected.Keys) {
            if (-not $values.ContainsKey($name) -or $values[$name] -cne $expected[$name]) { throw "Unbekannter nativer Agitprop-Startwert: $name." }
        }
        foreach ($side in @('left', 'center', 'right')) {
            $name = 'SOV_poster_' + $side + '_icon_frame'
            if (-not $values.ContainsKey($name) -or $values[$name] -cne 'SOV_propaganda_locked_slot_index') { throw "Unbekannte native Slotinitialisierung: $name." }
        }

        $campaignRoot = Get-LitoNativeRoot -Source $decisions -Name 'SOV_propaganda_campaigns'
        $campaigns = @(Get-LitoNativeChildren -Source $decisions -Entry $campaignRoot | Where-Object { $_.Name -clike 'SOV_propaganda_*' -and $_.IsBlock })
        if ($campaigns.Count -ne 24) { throw "Erwartet 24 originale Agitprop-Kampagnen, gefunden: $($campaigns.Count)." }
        foreach ($campaign in $campaigns) {
            $cost = Get-LitoNativeChild -Source $decisions -Entry $campaign -Name 'cost'
            if ($cost.IsBlock -or -not $values.ContainsKey($cost.Value)) { throw "Kein nativer Startwert fuer Kampagnenkosten: $($campaign.Name)." }
        }

        $transactionRoot = Join-Path ([IO.Path]::GetTempPath()) ('lito-native-agitprop-' + [guid]::NewGuid().ToString('N'))
        $workMod = Join-Path $transactionRoot 'soviet_renewal'
        New-Item -ItemType Directory -Path $transactionRoot | Out-Null
        Copy-Item -LiteralPath $StagedMod -Destination $workMod -Recurse
        $categoryEdits = [Collections.Generic.List[object]]::new()
        $categoryCounts = @{ SOV_expand_the_agitprop = 0; SOV_collectivist_propaganda = 0; SOV_the_komsomol = 0 }
        $visible = Get-LitoNativeChild -Source $categories -Entry $category -Name 'visible'
        Add-LitoNativeAliases -Source $categories -Entry $visible -Edits $categoryEdits -Counts $categoryCounts
        if ($categoryCounts.SOV_expand_the_agitprop -lt 1) { throw 'Die native Kategorie hat keine bekannte positive Agitprop-Fokusbedingung.' }
        Write-LitoNativePatched -Source $categories -Edits $categoryEdits

        $decisionEdits = [Collections.Generic.List[object]]::new()
        $decisionCounts = @{ SOV_expand_the_agitprop = 0; SOV_collectivist_propaganda = 0; SOV_the_komsomol = 0 }
        foreach ($campaign in $campaigns) {
            $visible = Get-LitoNativeChild -Source $decisions -Entry $campaign -Name 'visible'
            Add-LitoNativeAliases -Source $decisions -Entry $visible -Edits $decisionEdits -Counts $decisionCounts
        }
        # Keep the native mechanics and any running save-game campaigns, while
        # removing every original campaign/debug choice from Lito's selection.
        # Other Soviet starts retain their original visibility conditions.
        $hideOriginal = 'NOT = { AND = { tag = SOV has_country_flag = sr_lito_initialized } }'
        $originalChoices = @(Get-LitoNativeChildren -Source $decisions -Entry $campaignRoot | Where-Object { $_.IsBlock })
        if ($originalChoices.Count -ne 28) { throw 'Die originale Agitprop-Auswahl besitzt unbekannte Zusatzentscheidungen.' }
        foreach ($choice in $originalChoices) {
            $visible = Get-LitoNativeChild -Source $decisions -Entry $choice -Name 'visible'
            $guards = 0
            foreach ($condition in @(Get-LitoNativeChildren -Source $decisions -Entry $visible)) {
                if ($condition.Name -ceq 'NOT' -and $condition.IsBlock) {
                    $conditionText = $decisions.Text.Substring($condition.Start, $condition.End - $condition.Start)
                    if (Test-LitoNativePictureSameTokens -Left $conditionText -Right $hideOriginal) { $guards++ }
                }
            }
            if ($guards -gt 1) { throw "Mehrfache Lito-Auswahlsperre: $($choice.Name)." }
            if ($guards -eq 0) {
                $decisionEdits.Add([pscustomobject]@{ Start = $decisions.Tokens[$visible.Open].End; End = $decisions.Tokens[$visible.Open].End; Text = "`n            $hideOriginal`n" })
            }
        }
        if ($decisionCounts.SOV_expand_the_agitprop -ne 9 -or $decisionCounts.SOV_collectivist_propaganda -ne 1 -or $decisionCounts.SOV_the_komsomol -ne 3) {
            throw 'Die originalen Kampagnen besitzen eine unbekannte Agitprop-Freischaltstruktur.'
        }
        Write-LitoNativePatched -Source $decisions -Edits $decisionEdits

        $runtime = [Text.StringBuilder]::new()
        $null = $runtime.AppendLine('# Generated from this local game installation. Preserve all existing campaign state.')
        $null = $runtime.AppendLine('sr_lito_native_agitprop_sync_effect = {')
        $null = $runtime.AppendLine('    if = { limit = { tag = SOV has_country_flag = sr_lito_initialized }')
        $null = $runtime.AppendLine('        set_country_flag = sr_lito_native_agitprop_ready')
        foreach ($item in $defaults) {
            $null = $runtime.AppendLine('        if = { limit = { NOT = { has_variable = ' + $item.Name + ' } } ' + $item.Text + ' }')
        }
        $null = $runtime.AppendLine('        if = { limit = { has_completed_focus = sr_lito_politics_cadre_schools } set_country_flag = sr_lito_native_agitprop_unlocked }')
        $null = $runtime.AppendLine('        if = { limit = { has_country_flag = sr_lito_native_agitprop_unlocked }')
        $null = $runtime.AppendLine('            set_variable = { sr_lito_native_agitprop_target_slots = 1 }')
        $null = $runtime.AppendLine('            if = { limit = { OR = { has_completed_focus = sr_lito_workers_councils has_country_flag = sr_lito_native_agitprop_councils_milestone } } add_to_variable = { sr_lito_native_agitprop_target_slots = 1 } }')
        $null = $runtime.AppendLine('            if = { limit = { OR = { has_completed_focus = sr_lito_academy_network has_country_flag = sr_lito_native_agitprop_academy_milestone } } add_to_variable = { sr_lito_native_agitprop_target_slots = 1 } }')
        $null = $runtime.AppendLine('            set_variable = { sr_lito_native_agitprop_open_slots = 0 }')
        foreach ($side in @('left', 'center', 'right')) {
            $null = $runtime.AppendLine('            if = { limit = { NOT = { check_variable = { var = SOV_poster_' + $side + '_icon_frame value = SOV_propaganda_locked_slot_index compare = equals } } } add_to_variable = { sr_lito_native_agitprop_open_slots = 1 } }')
        }
        for ($i = 0; $i -lt 3; $i++) {
            $null = $runtime.AppendLine('            if = { limit = { check_variable = { sr_lito_native_agitprop_open_slots < sr_lito_native_agitprop_target_slots } OR = { check_variable = { var = SOV_poster_left_icon_frame value = SOV_propaganda_locked_slot_index compare = equals } check_variable = { var = SOV_poster_center_icon_frame value = SOV_propaganda_locked_slot_index compare = equals } check_variable = { var = SOV_poster_right_icon_frame value = SOV_propaganda_locked_slot_index compare = equals } } } SOV_unlock_propaganda_campaign_slot_effect = yes add_to_variable = { sr_lito_native_agitprop_open_slots = 1 } }')
        }
        $null = $runtime.AppendLine('            clear_variable = sr_lito_native_agitprop_open_slots')
        $null = $runtime.AppendLine('            clear_variable = sr_lito_native_agitprop_target_slots')
        $null = $runtime.AppendLine('        }')
        $null = $runtime.AppendLine('    }')
        $null = $runtime.AppendLine('}')
        $runtimeText = $runtime.ToString()
        $null = Get-ClausewitzTokens -Text $runtimeText -SourceName 'sr_native_agitprop_effects.txt (generiert)'
        $runtimePath = Join-Path $workMod 'common/scripted_effects/sr_native_agitprop_effects.txt'
        New-Item -ItemType Directory -Path (Split-Path -Parent $runtimePath) -Force | Out-Null
        [IO.File]::WriteAllText($runtimePath, $runtimeText, [Text.UTF8Encoding]::new($false))

        if (-not (Get-Command Install-LitoNativeAgitpropPictures -ErrorAction SilentlyContinue)) { throw 'Die native Poster-Anbindung fehlt im Installationspaket.' }
        $picturesResult = Install-LitoNativeAgitpropPictures -GameRoot $GameRoot -StagedMod $workMod
        if ($picturesResult -is [bool] -and -not $picturesResult) { throw 'Die nativen Poster konnten nicht vorbereitet werden.' }

        # Commit only changed files. In a failed commit restore every staged
        # byte (or remove newly added files), leaving the outer installer safe.
        try {
            foreach ($file in @(Get-ChildItem -LiteralPath $workMod -File -Recurse)) {
                $relative = $file.FullName.Substring($workMod.Length).TrimStart([char[]]'\/')
                $target = Join-Path $StagedMod $relative
                $data = [IO.File]::ReadAllBytes($file.FullName)
                $old = $null
                $exists = Test-Path -LiteralPath $target -PathType Leaf
                if ($exists) {
                    $old = [IO.File]::ReadAllBytes($target)
                    $newHash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
                    if ($newHash -ceq (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash) { continue }
                }
                $committed.Add([pscustomobject]@{ Path = $target; Existed = $exists; Bytes = $old })
                New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
                [IO.File]::WriteAllBytes($target, $data)
            }
        } catch {
            $commitError = $_
            foreach ($item in @($committed.ToArray()) | Sort-Object Path -Descending) {
                try {
                    if ($item.Existed) { [IO.File]::WriteAllBytes($item.Path, $item.Bytes) }
                    elseif (Test-Path -LiteralPath $item.Path -PathType Leaf) { Remove-Item -LiteralPath $item.Path -Force }
                } catch { $rollbackError = $_.Exception }
            }
            if ($null -ne $rollbackError) { throw [IO.IOException]::new('Die vorbereitete Agitprop-Anbindung konnte nach einem Schreibfehler nicht zurueckgesetzt werden.', $rollbackError) }
            throw $commitError
        }
        Write-Host ('Litos Agitprop vorbereitet: nur eigene Kampagnen und Poster, drei native Posterplaetze; {0} Moddateien angepasst.' -f $committed.Count) -ForegroundColor Green
        return $true
    } catch {
        if ($null -ne $rollbackError) { throw }
        Write-Warning ('Originales Agitprop nicht eingerichtet; der Agitprop-Fokus bleibt gesperrt. ' + $_.Exception.Message)
        return $false
    } finally {
        if ($null -ne $transactionRoot -and (Test-Path -LiteralPath $transactionRoot)) {
            try { Remove-Item -LiteralPath $transactionRoot -Recurse -Force }
            catch { Write-Warning ('Temporaere Agitprop-Dateien verblieben: ' + $transactionRoot) }
        }
    }
}
