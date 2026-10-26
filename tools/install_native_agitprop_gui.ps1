# Native poster artwork adapter. Dot-source after the shared Clausewitz helpers.
# Only staged mod copies are changed; original game files remain read-only.

function Read-LitoNativePictureText {
    param([string]$Path)
    $bytes = [IO.File]::ReadAllBytes($Path)
    $bom = $bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191
    $offset = 0
    if ($bom) { $offset = 3 }
    $text = [Text.UTF8Encoding]::new($false, $true).GetString($bytes, $offset, $bytes.Length - $offset)
    $newline = "`n"
    if ($text.Contains("`r`n")) { $newline = "`r`n" }
    elseif ($text.Contains("`r")) { $newline = "`r" }
    return [pscustomobject]@{ Text = $text; Bom = $bom; Newline = $newline }
}

function Get-LitoNativePictureField {
    param([object[]]$Tokens, [object]$Entry, [string]$Name, [switch]$Block)
    $found = @(Get-LitoScriptEntries -Tokens $Tokens -Open $Entry.Open -Close $Entry.Close |
        Where-Object { $_.Name -ceq $Name })
    if ($found.Count -ne 1 -or $found[0].IsBlock -ne [bool]$Block) {
        throw "Unerwartetes Feld '$Name' in der nativen Agitprop-Anzeige."
    }
    return $found[0]
}

function Get-LitoNativePictureGuiShape {
    param([string]$Text, [string]$SourceName, [string[]]$ExtraIcons = @())
    $tokens = Get-ClausewitzTokens -Text $Text -SourceName $SourceName
    $root = Get-DirectBlock -Tokens $tokens -Close $tokens.Count -Name 'guiTypes'
    $windows = @(Get-LitoScriptEntries -Tokens $tokens -Open $root.Open -Close $root.Close |
        Where-Object { $_.Name -ceq 'containerWindowType' -and $_.IsBlock })
    if ($windows.Count -ne 1) { throw 'Die native Agitprop-GUI muss genau ein Fenster enthalten.' }
    $window = $windows[0]
    $name = Get-LitoNativePictureField -Tokens $tokens -Entry $window -Name 'name'
    if ($name.Value -cne 'sov_propaganda_campaigns_ui_window') { throw 'Unerwarteter nativer Agitprop-Fenstername.' }
    $children = @(Get-LitoScriptEntries -Tokens $tokens -Open $window.Open -Close $window.Close)
    $icons = @($children | Where-Object { $_.Name -ceq 'iconType' -and $_.IsBlock })
    $texts = @($children | Where-Object { $_.Name -ceq 'instantTextBoxType' -and $_.IsBlock })
    if ($icons.Count -ne (4 + $ExtraIcons.Count) -or $texts.Count -ne 3) {
        throw 'Nicht unterstuetzte Struktur der nativen Agitprop-GUI: erwartet werden Hintergrund, drei Poster und drei Zeitangaben.'
    }
    $byName = @{}
    foreach ($icon in $icons) {
        $field = Get-LitoNativePictureField -Tokens $tokens -Entry $icon -Name 'name'
        if ($byName.ContainsKey($field.Value)) { throw "Doppeltes GUI-Element: $($field.Value)" }
        $byName[$field.Value] = $icon
    }
    foreach ($expected in @('propaganda_bg', 'propaganda_poster_left', 'propaganda_poster_center', 'propaganda_poster_right') + $ExtraIcons) {
        if (-not $byName.ContainsKey($expected)) { throw "Natives Agitprop-GUI-Element fehlt: $expected" }
    }
    $textNames = @()
    foreach ($textEntry in $texts) {
        $textNames += (Get-LitoNativePictureField -Tokens $tokens -Entry $textEntry -Name 'name').Value
    }
    foreach ($position in @('left', 'center', 'right')) {
        if (@($textNames | Where-Object { $_ -ceq "poster_${position}_text" }).Count -ne 1) { throw 'Eine native Agitprop-Zeitangabe fehlt oder ist doppelt.' }
        $icon = $byName["propaganda_poster_$position"]
        $null = Get-LitoNativePictureField -Tokens $tokens -Entry $icon -Name 'position' -Block
        $tooltip = Get-LitoNativePictureField -Tokens $tokens -Entry $icon -Name 'pdx_tooltip'
        if ($tooltip.Value -cne ('SOV_PROPAGANDA_CAMPAIGN_TT_' + $position.ToUpperInvariant())) { throw 'Unerwarteter nativer Poster-Tooltip.' }
    }
    return [pscustomobject]@{ Tokens = $tokens; Window = $window; Icons = $byName }
}

function Add-LitoNativePictureEdits {
    param([string]$Text, [object]$Edits)
    foreach ($edit in @($Edits | Sort-Object Position -Descending)) {
        $Text = $Text.Remove($edit.Position, $edit.Length).Insert($edit.Position, $edit.Text)
    }
    return $Text
}

function Test-LitoNativePictureSameTokens {
    param([string]$Left, [string]$Right)
    $leftTokens = Get-ClausewitzTokens -Text $Left -SourceName 'vorhandene Poster-Anpassung'
    $rightTokens = Get-ClausewitzTokens -Text $Right -SourceName 'erwartete Poster-Anpassung'
    if ($leftTokens.Count -ne $rightTokens.Count) { return $false }
    for ($i = 0; $i -lt $leftTokens.Count; $i++) {
        if ($leftTokens[$i].Value -cne $rightTokens[$i].Value) { return $false }
    }
    return $true
}

function Install-LitoNativeAgitpropPictures {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$GameRoot,
          [Parameter(Mandatory = $true)][string]$StagedMod)

    $guiRelative = 'interface/sov_propaganda_campaigns_scripted_gui.gui'
    $scriptRelative = 'common/scripted_guis/SOV_propaganda_campaigns_scripted_gui.txt'
    $spriteRelative = 'interface/sr_lito_native_agitprop_posters.gfx'
    $campaignPath = Join-Path $GameRoot 'common/decisions/SOV.txt'
    $campaignSource = Read-LitoNativePictureText -Path $campaignPath
    $campaignTokens = Get-ClausewitzTokens -Text $campaignSource.Text -SourceName $campaignPath
    $category = Get-DirectBlock -Tokens $campaignTokens -Close $campaignTokens.Count -Name 'SOV_propaganda_campaigns'
    $mapping = @(
        @{ Art = 'light'; Campaign = 'SOV_propaganda_motherland_calls' },
        @{ Art = 'star'; Campaign = 'SOV_propaganda_hit_of_hammer' },
        @{ Art = 'peoples'; Campaign = 'SOV_propaganda_high_yield' }
    )
    $ids = @{}
    foreach ($item in $mapping) {
        $campaign = Get-DirectBlock -Tokens $campaignTokens -Open $category.Open -Close $category.Close -Name $item.Campaign
        $complete = Get-DirectBlock -Tokens $campaignTokens -Open $campaign.Open -Close $campaign.Close -Name 'complete_effect'
        $fields = @(Get-LitoScriptEntries -Tokens $campaignTokens -Open $complete.Open -Close $complete.Close)
        if (@($fields | Where-Object { $_.Name -ceq 'SOV_pick_propaganda_campaign_slot_effect' -and -not $_.IsBlock -and $_.Value -ceq 'yes' }).Count -ne 1) {
            throw "Der originale Slot-Aufruf fehlt in $($item.Campaign)."
        }
        $idFields = @()
        foreach ($assignment in @($fields | Where-Object { $_.Name -ceq 'set_variable' -and $_.IsBlock })) {
            $idFields += @(Get-LitoScriptEntries -Tokens $campaignTokens -Open $assignment.Open -Close $assignment.Close |
                Where-Object { $_.Name -ceq 'SOV_new_propaganda_campaign' -and -not $_.IsBlock })
        }
        if ($idFields.Count -ne 1 -or $idFields[0].Value -notmatch '^[1-9][0-9]*$') { throw "Keine eindeutige native Poster-ID fuer $($item.Campaign)." }
        $id = [int]$idFields[0].Value
        if ($id -le 2 -or $ids.Values -contains $id) { throw 'Unerwartete oder doppelte native Poster-ID.' }
        $ids[$item.Art] = $id
        $texturePath = Join-Path $StagedMod ("gfx/interface/agitprop/sr_agitprop_$($item.Art).dds")
        $dds = [IO.File]::ReadAllBytes($texturePath)
        if ($dds.Length -lt 128 -or [Text.Encoding]::ASCII.GetString($dds, 0, 4) -cne 'DDS ' -or
            [BitConverter]::ToUInt32($dds, 12) -ne 200 -or [BitConverter]::ToUInt32($dds, 16) -ne 150) {
            throw "Das eigene Agitprop-Poster muss 150 x 200 Pixel als DDS vorliegen: $texturePath"
        }
    }

    $guiPath = Join-Path $StagedMod $guiRelative
    $scriptPath = Join-Path $StagedMod $scriptRelative
    $guiReadPath = $guiPath
    if (-not (Test-Path -LiteralPath $guiReadPath -PathType Leaf)) { $guiReadPath = Join-Path $GameRoot $guiRelative }
    $scriptReadPath = $scriptPath
    if (-not (Test-Path -LiteralPath $scriptReadPath -PathType Leaf)) { $scriptReadPath = Join-Path $GameRoot $scriptRelative }
    $guiSource = Read-LitoNativePictureText -Path $guiReadPath
    $scriptSource = Read-LitoNativePictureText -Path $scriptReadPath
    $guiText = $guiSource.Text
    $normalized = $false
    $alreadyInstalled = $false
    $expectedIconNames = @()
    foreach ($position in @('left', 'center', 'right')) {
        foreach ($item in $mapping) { $expectedIconNames += "sr_lito_poster_${position}_$($item.Art)" }
    }
    try {
        $gui = Get-LitoNativePictureGuiShape -Text $guiText -SourceName $guiReadPath
    } catch {
        $originalError = $_
        try {
            $gui = Get-LitoNativePictureGuiShape -Text $guiText -SourceName $guiReadPath -ExtraIcons $expectedIconNames
            $alreadyInstalled = $true
        } catch {
            # Some supplied vanilla copies omit only the outer guiTypes terminator.
            # Accept one extra terminator ONLY when the complete known native shape
            # then validates. Broken children or duplicate widgets still abort.
            $candidate = $guiText + $guiSource.Newline + '}' + $guiSource.Newline
            try { $gui = Get-LitoNativePictureGuiShape -Text $candidate -SourceName "$guiReadPath (Modkopie mit geschlossenem GUI-Rahmen)" }
            catch { throw $originalError }
            $guiText = $candidate
            $normalized = $true
        }
    }
    $scriptTokens = Get-ClausewitzTokens -Text $scriptSource.Text -SourceName $scriptReadPath
    $scriptRoot = Get-DirectBlock -Tokens $scriptTokens -Close $scriptTokens.Count -Name 'scripted_gui'
    $nativeUi = Get-DirectBlock -Tokens $scriptTokens -Open $scriptRoot.Open -Close $scriptRoot.Close -Name 'sov_propaganda_campaigns_ui'
    $uiFields = @(Get-LitoScriptEntries -Tokens $scriptTokens -Open $nativeUi.Open -Close $nativeUi.Close)
    $context = @($uiFields | Where-Object { $_.Name -ceq 'context_type' -and -not $_.IsBlock })
    $window = @($uiFields | Where-Object { $_.Name -ceq 'window_name' -and -not $_.IsBlock })
    if ($context.Count -ne 1 -or $context[0].Value -cne 'decision_category' -or
        $window.Count -ne 1 -or $window[0].Value -cne 'sov_propaganda_campaigns_ui_window') { throw 'Nicht unterstuetzte originale Agitprop-Scripted-GUI.' }
    $properties = Get-DirectBlock -Tokens $scriptTokens -Open $nativeUi.Open -Close $nativeUi.Close -Name 'properties'
    foreach ($position in @('left', 'center', 'right')) {
        $property = Get-DirectBlock -Tokens $scriptTokens -Open $properties.Open -Close $properties.Close -Name "propaganda_poster_$position"
        $propertyFields = @(Get-LitoScriptEntries -Tokens $scriptTokens -Open $property.Open -Close $property.Close)
        $image = @($propertyFields | Where-Object { $_.Name -ceq 'image' -and -not $_.IsBlock })
        $frame = @($propertyFields | Where-Object { $_.Name -ceq 'frame' -and -not $_.IsBlock })
        $capital = $position.Substring(0, 1).ToUpperInvariant() + $position.Substring(1)
        if ($image.Count -ne 1 -or $image[0].Value -cne "[GetPropaganda${capital}SlotAge]" -or
            $frame.Count -ne 1 -or $frame[0].Value -cne "SOV_poster_${position}_icon_frame") { throw 'Unerwartete native Poster-Eigenschaften.' }
    }

    $triggerBlocks = @($uiFields | Where-Object { $_.Name -ceq 'triggers' })
    if ($triggerBlocks.Count -gt 1 -or ($triggerBlocks.Count -eq 1 -and -not $triggerBlocks[0].IsBlock)) { throw 'Nicht eindeutige native GUI-Trigger.' }
    $triggerFields = @()
    if ($triggerBlocks.Count -eq 1) { $triggerFields = @(Get-LitoScriptEntries -Tokens $scriptTokens -Open $triggerBlocks[0].Open -Close $triggerBlocks[0].Close) }
    $scriptEdits = [Collections.Generic.List[object]]::new()
    $addedTriggers = ''
    $addedIcons = ''
    $newIconNames = [Collections.Generic.List[string]]::new()
    foreach ($position in @('left', 'center', 'right')) {
        $frameName = "SOV_poster_${position}_icon_frame"
        $gate = 'tag = SOV has_country_flag = sr_lito_initialized has_country_flag = sr_lito_native_agitprop_unlocked'
        $matches = ($mapping | ForEach-Object { "check_variable = { var = $frameName value = $($ids[$_.Art]) compare = equals }" }) -join ' '
        $hide = 'NOT = { AND = { ' + $gate + ' OR = { ' + $matches + ' } } }'
        $nativeTrigger = "propaganda_poster_${position}_visible"
        $existing = @($triggerFields | Where-Object { $_.Name -ceq $nativeTrigger })
        if ($existing.Count -gt 1 -or ($existing.Count -eq 1 -and -not $existing[0].IsBlock)) { throw "Unerwarteter Trigger: $nativeTrigger" }
        if ($alreadyInstalled) {
            if ($existing.Count -ne 1) { throw "Vorhandene Poster-Anpassung ist unvollstaendig: $nativeTrigger" }
            $existingHides = 0
            foreach ($condition in @(Get-LitoScriptEntries -Tokens $scriptTokens -Open $existing[0].Open -Close $existing[0].Close)) {
                if ($condition.Name -ceq 'NOT' -and $condition.IsBlock) {
                    $conditionText = $scriptSource.Text.Substring($condition.Start, $condition.End - $condition.Start)
                    if (Test-LitoNativePictureSameTokens -Left $conditionText -Right $hide) { $existingHides++ }
                }
            }
            if ($existingHides -ne 1) { throw "Vorhandene Poster-Anpassung hat keine eindeutige Bildsperre: $nativeTrigger" }
        } elseif ($existing.Count -eq 1) {
            $scriptEdits.Add([pscustomobject]@{ Position = $scriptTokens[$existing[0].Open].End; Length = 0; Text = $scriptSource.Newline + '            ' + $hide + $scriptSource.Newline })
        } else {
            $addedTriggers += '        ' + $nativeTrigger + ' = { ' + $hide + ' }' + $scriptSource.Newline
        }
        $icon = $gui.Icons["propaganda_poster_$position"]
        $iconFields = @(Get-LitoScriptEntries -Tokens $gui.Tokens -Open $icon.Open -Close $icon.Close)
        if (@($iconFields | Where-Object { $_.Name -in @('frame', 'spriteType', 'quadTextureSprite') }).Count -ne 0) { throw 'Das native Poster-Element enthaelt unerwartete statische Bild-/Frame-Felder.' }
        $nameField = Get-LitoNativePictureField -Tokens $gui.Tokens -Entry $icon -Name 'name'
        foreach ($item in $mapping) {
            $art = $item.Art
            $newName = "sr_lito_poster_${position}_${art}"
            $newIconNames.Add($newName)
            $triggerName = $newName + '_visible'
            $ownTriggers = @($triggerFields | Where-Object { $_.Name -ceq $triggerName })
            $expectedTrigger = $triggerName + ' = { ' + $gate + " check_variable = { var = $frameName value = $($ids[$art]) compare = equals } }"
            if ($alreadyInstalled) {
                if ($ownTriggers.Count -ne 1 -or -not $ownTriggers[0].IsBlock) { throw "Vorhandener Poster-Trigger ist unvollstaendig: $triggerName" }
                $ownTriggerText = $scriptSource.Text.Substring($ownTriggers[0].Start, $ownTriggers[0].End - $ownTriggers[0].Start)
                if (-not (Test-LitoNativePictureSameTokens -Left $ownTriggerText -Right $expectedTrigger)) { throw "Vorhandener Poster-Trigger stimmt nicht mit der nativen Kampagne ueberein: $triggerName" }
            } else {
                if ($ownTriggers.Count -ne 0) { throw "Eigener Poster-Trigger ist bereits vorhanden: $triggerName" }
                $addedTriggers += '        ' + $expectedTrigger + $scriptSource.Newline
            }
            $clone = $guiText.Substring($icon.Start, $icon.End - $icon.Start)
            $edits = [Collections.Generic.List[object]]::new()
            $nameToken = $gui.Tokens[$nameField.Open]
            $edits.Add([pscustomobject]@{ Position = $nameToken.Start - $icon.Start; Length = $nameToken.End - $nameToken.Start; Text = '"' + $newName + '"' })
            $edits.Add([pscustomobject]@{ Position = $gui.Tokens[$icon.Open].End - $icon.Start; Length = 0; Text = $guiSource.Newline + '            spriteType = "GFX_sr_lito_native_poster_' + $art + '"' + $guiSource.Newline })
            $clone = Add-LitoNativePictureEdits -Text $clone -Edits $edits
            if ($alreadyInstalled) {
                $ownIcon = $gui.Icons[$newName]
                $ownIconText = $guiText.Substring($ownIcon.Start, $ownIcon.End - $ownIcon.Start)
                if (-not (Test-LitoNativePictureSameTokens -Left $ownIconText -Right $clone)) { throw "Vorhandenes Poster-Element stimmt nicht mit dem Originalfenster ueberein: $newName" }
            } else {
                $addedIcons += $guiSource.Newline + '        ' + $clone + $guiSource.Newline
            }
        }
    }
    if ($alreadyInstalled) {
        $preparedScript = $scriptSource.Text
        $preparedGui = $guiText
    } elseif ($triggerBlocks.Count -eq 1) {
        $scriptEdits.Add([pscustomobject]@{ Position = $scriptTokens[$triggerBlocks[0].Close].Start; Length = 0; Text = $scriptSource.Newline + $addedTriggers })
    } else {
        $scriptEdits.Add([pscustomobject]@{ Position = $scriptTokens[$nativeUi.Close].Start; Length = 0; Text = $scriptSource.Newline + '    triggers = {' + $scriptSource.Newline + $addedTriggers + '    }' + $scriptSource.Newline })
    }
    if (-not $alreadyInstalled) {
        $preparedScript = Add-LitoNativePictureEdits -Text $scriptSource.Text -Edits $scriptEdits
        $preparedGui = $guiText.Insert($gui.Tokens[$gui.Window.Close].Start, $addedIcons)
    }
    $null = Get-ClausewitzTokens -Text $preparedScript -SourceName "$scriptRelative (Modkopie)"
    $null = Get-LitoNativePictureGuiShape -Text $preparedGui -SourceName "$guiRelative (Modkopie)" -ExtraIcons $newIconNames.ToArray()
    $spriteText = "spriteTypes = {`n"
    foreach ($item in $mapping) {
        $spriteText += '    spriteType = { name = "GFX_sr_lito_native_poster_' + $item.Art + '" texturefile = "gfx/interface/agitprop/sr_agitprop_' + $item.Art + '.dds" }' + "`n"
    }
    $spriteText += "}`n"
    $null = Get-ClausewitzTokens -Text $spriteText -SourceName $spriteRelative
    $spritePath = Join-Path $StagedMod $spriteRelative
    foreach ($file in @(Get-ChildItem -LiteralPath (Join-Path $StagedMod 'interface') -Filter '*.gfx' -File -Recurse -ErrorAction SilentlyContinue)) {
        if ($file.FullName -ieq [IO.Path]::GetFullPath($spritePath)) { continue }
        $content = [IO.File]::ReadAllText($file.FullName)
        foreach ($item in $mapping) {
            if ($content -match ('\bname\s*=\s*"?GFX_sr_lito_native_poster_' + [regex]::Escape($item.Art) + '(?:"|\s|\})')) { throw 'Ein eigener Agitprop-Poster-Sprite ist bereits anderweitig definiert.' }
        }
    }
    if ($alreadyInstalled) {
        if (-not (Test-Path -LiteralPath $spritePath -PathType Leaf)) { throw 'Vorhandene Poster-Anpassung hat keine eigenen Sprite-Definitionen.' }
        $oldSprite = Read-LitoNativePictureText -Path $spritePath
        if (-not (Test-LitoNativePictureSameTokens -Left $oldSprite.Text -Right $spriteText)) { throw 'Vorhandene Agitprop-Poster-Sprites stimmen nicht ueberein.' }
        return [pscustomobject]@{ Pictures = 3; Overlays = 9; GuiRootNormalized = $false; CampaignIds = $ids; AlreadyInstalled = $true }
    }

    # Every output is parsed before the first write. Snapshot each attempted
    # target so a failed staged write restores all prior staged bytes.
    $outputs = @(
        @{ Path = $guiPath; Text = $preparedGui; Bom = $guiSource.Bom },
        @{ Path = $scriptPath; Text = $preparedScript; Bom = $scriptSource.Bom },
        @{ Path = $spritePath; Text = $spriteText; Bom = $false }
    )
    $written = [Collections.Generic.List[object]]::new()
    $createdDirectories = [Collections.Generic.List[string]]::new()
    try {
        foreach ($output in $outputs) {
            $directory = Split-Path -Parent $output.Path
            $missing = [Collections.Generic.List[string]]::new()
            $walk = $directory
            while (-not (Test-Path -LiteralPath $walk -PathType Container)) {
                $missing.Add($walk)
                $walk = Split-Path -Parent $walk
            }
            foreach ($newDirectory in @($missing | Sort-Object Length)) {
                New-Item -ItemType Directory -Path $newDirectory | Out-Null
                $createdDirectories.Add($newDirectory)
            }
            $exists = Test-Path -LiteralPath $output.Path -PathType Leaf
            $oldBytes = $null
            if ($exists) { $oldBytes = [IO.File]::ReadAllBytes($output.Path) }
            $written.Add([pscustomobject]@{ Path = $output.Path; Existed = $exists; Bytes = $oldBytes })
            [IO.File]::WriteAllText($output.Path, $output.Text, [Text.UTF8Encoding]::new([bool]$output.Bom))
        }
    } catch {
        $writeError = $_
        for ($i = $written.Count - 1; $i -ge 0; $i--) {
            $previous = $written[$i]
            try {
                if ($previous.Existed) {
                    $same = (Test-Path -LiteralPath $previous.Path -PathType Leaf) -and
                        ([Convert]::ToBase64String([IO.File]::ReadAllBytes($previous.Path)) -ceq [Convert]::ToBase64String($previous.Bytes))
                    if (-not $same) { [IO.File]::WriteAllBytes($previous.Path, $previous.Bytes) }
                } elseif (Test-Path -LiteralPath $previous.Path -PathType Leaf) { Remove-Item -LiteralPath $previous.Path -Force }
            } catch { Write-Warning "Staging-Datei konnte nicht wiederhergestellt werden: $($previous.Path). $($_.Exception.Message)" }
        }
        foreach ($directory in @($createdDirectories | Sort-Object Length -Descending)) {
            if ((Test-Path -LiteralPath $directory -PathType Container) -and @(Get-ChildItem -LiteralPath $directory -Force).Count -eq 0) { [IO.Directory]::Delete($directory) }
        }
        throw $writeError
    }
    return [pscustomobject]@{ Pictures = 3; Overlays = 9; GuiRootNormalized = $normalized; CampaignIds = $ids; AlreadyInstalled = $false }
}
