# Synthetic integration checks for locally generated legacy-Soviet overrides.
# No game assets or engine are used; all fixture files are under TEMP.
[CmdletBinding()]
param([string]$Installer = (Join-Path $PSScriptRoot 'install_lito.ps1'))
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$legacyTestRoot = Join-Path ([IO.Path]::GetTempPath()) ('lito-legacy-' + [guid]::NewGuid().ToString('N'))
$legacyGame = Join-Path $legacyTestRoot 'game'
$legacySource = Join-Path $legacyTestRoot 'source'
$legacyMods = Join-Path $legacyTestRoot 'mods'
$legacyTarget = Join-Path $legacyMods 'soviet_renewal'
$legacyUtf8 = [Text.UTF8Encoding]::new($true)
$legacyGuard = 'NOT = { SOV = { has_country_flag = sr_lito_initialized } }'

function Assert-Legacy {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw "FAIL: $Message" }
}
function Write-LegacyFixture {
    param([string]$Relative, [string]$Text)
    $target = Join-Path $legacyGame $Relative
    New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
    [IO.File]::WriteAllText($target, $Text.Replace("`r`n", "`n").Replace("`n", "`r`n"), $legacyUtf8)
}
function Get-LegacyHashes {
    $result = @{}
    foreach ($file in Get-ChildItem -LiteralPath $legacyGame -File -Recurse) {
        $result[$file.FullName] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
    }
    return $result
}

try {
    Write-LegacyFixture 'common/ideologies/00_ideologies.txt' 'ideologies = { communism = { types = { stalinism = {} } } democratic = { types = { liberalism = {} } } }'
    Write-LegacyFixture 'gfx/leaders/Europe/Portrait_Europe_Generic_1.dds' 'synthetic portrait; not a DDS'
    foreach ($folder in @('gfx/flags', 'gfx/flags/medium', 'gfx/flags/small')) {
        Write-LegacyFixture "$folder/SOV.tga" 'synthetic Soviet flag'
        Write-LegacyFixture "$folder/YUG.tga" 'synthetic Yugoslav flag'
    }
    New-Item -ItemType Directory -Path (Join-Path $legacySource 'soviet_renewal/common/characters') -Force | Out-Null
    [IO.File]::WriteAllText((Join-Path $legacySource 'soviet_renewal/descriptor.mod'), 'name="Legacy Test"')
    [IO.File]::WriteAllText((Join-Path $legacySource 'soviet_renewal/common/characters/test.txt'), 'characters = { SOV_lito = { name = "Lito" } }')
    $routineEvent = 'country_event = { id = soviet.2 title = SOV_shipyard_report is_triggered_only = yes trigger = { tag = SOV } option = { name = SOV_shipyard_done add_political_power = 25 } }'
    $eventText = @'
add_namespace = soviet
# A comment mentions Trotsky and braces } { but is not an event.
country_event = {
    id = soviet.1
    title = SOV_political_paranoia_report
    desc = SOV_political_paranoia_report_desc
    is_triggered_only = yes
    trigger = { tag = SOV has_war = no }
    immediate = { add_to_variable = { SOV_paranoia = 10 } set_country_flag = SOV_paranoia_active }
    option = { name = SOV_paranoia_choice add_political_power = -50 }
}
__ROUTINE__
news_event = {
    id = soviet.3
    title = SOV_trotsky_in_exile
    is_triggered_only = yes
    option = { name = SOV_trotsky_news_option }
}
'@
    $eventText = $eventText.Replace('__ROUTINE__', $routineEvent)
    Write-LegacyFixture 'events/Soviet_mixed.txt' $eventText
    Write-LegacyFixture 'events/Generic_shipping.txt' 'country_event = { id = shipping.1 title = shipping option = { name = shipping_ok } }'
    [IO.File]::WriteAllBytes((Join-Path $legacyGame 'events/Old_encoding.txt'), [byte[]](35, 32, 228, 10, 99, 111, 117, 110, 116, 114, 121, 95, 101, 118, 101, 110, 116, 32, 61, 32, 123, 125))
    Write-LegacyFixture 'common/decisions/categories/Soviet.txt' @'
SOV_political_paranoia = { icon = generic_political_actions visible = { tag = SOV } }
SOV_trade_program = { icon = generic_trade visible = { tag = SOV } }
'@
    $routineDecision = 'SOV_merchant_contract = { cost = 25 complete_effect = { add_political_power = 10 } }'
    Write-LegacyFixture 'common/decisions/Soviet_mixed.txt' @"
SOV_political_actions = {
    SOV_hunt_trotsky = {
        cost = 50
        days_mission_timeout = 90
        visible = { tag = SOV }
        cancel_trigger = { has_war = yes }
        timeout_effect = { add_stability = -0.05 }
        cancel_effect = { add_political_power = -25 }
        complete_effect = { set_country_flag = SOV_trotsky_hunted }
    }
    $routineDecision
}
"@
    $routineEffect = 'SOV_shipyard_program = { add_political_power = 25 }'
    Write-LegacyFixture 'common/scripted_effects/Soviet_mixed.txt' @"
SOV_increase_paranoia = { add_to_variable = { SOV_paranoia = 5 } }
$routineEffect
"@
    $routineGui = 'SOV_industry_panel = { window_name = industry_window context_type = player_context visible = { tag = SOV } }'
    Write-LegacyFixture 'common/scripted_guis/Soviet_mixed.txt' @"
scripted_gui = {
    SOV_paranoia_panel = { window_name = paranoia_window context_type = player_context visible = { tag = SOV } }
    $routineGui
}
"@
    Write-LegacyFixture 'common/ideas/Soviet.txt' @'
ideas = { country = {
    SOV_political_paranoia = { modifier = { stability_factor = -0.05 } }
    SOV_trotskyist_opposition = { modifier = { political_power_gain = -0.05 } }
    SOV_industrial_program = { modifier = { industrial_capacity_factory = 0.05 } }
} }
'@
    Write-LegacyFixture 'common/characters/SOV.txt' @'
characters = {
    SOV_lev_trotsky = { name = SOV_lev_trotsky country_leader = { ideology = marxism } }
    SOV_ordinary_general = { name = "Ordinary general" }
}
'@
    $before = Get-LegacyHashes
    # Dot-source only in this fixture to expose the lossless token parser for
    # assertions after executing the real full installation transaction.
    . $Installer -GamePath $legacyGame -SourceRoot $legacySource -ModDirectory $legacyMods
    $eventsPath = Join-Path $legacyTarget 'events/Soviet_mixed.txt'
    $events = [IO.File]::ReadAllText($eventsPath)
    Assert-Legacy (($events.Split(@($legacyGuard), [StringSplitOptions]::None).Count - 1) -eq 4) 'Both event triggers, the historical immediate and its option effect need guards'
    Assert-Legacy (($events.Split(@('option = { name = OK trigger = { SOV = { has_country_flag = sr_lito_initialized } }'), [StringSplitOptions]::None).Count - 1) -eq 2) 'A forced historical event must have a harmless exit'
    Assert-Legacy ($events.Contains($routineEvent)) 'Unrelated Soviet event must remain exact'
    Assert-Legacy ($events.Contains('trigger = {') -and $events.Contains('tag = SOV has_war = no')) 'Original event conditions must survive'
    Assert-Legacy ($events.Contains('# A comment mentions Trotsky and braces } { but is not an event.')) 'Comments must survive'
    Assert-Legacy (-not (Test-Path -LiteralPath (Join-Path $legacyTarget 'events/Generic_shipping.txt'))) 'Unrelated event file must not be overridden'
    $eventBytes = [IO.File]::ReadAllBytes($eventsPath)
    Assert-Legacy ($eventBytes[0] -eq 239 -and $eventBytes[1] -eq 187 -and $eventBytes[2] -eq 191) 'Legacy copy BOM must survive'
    Assert-Legacy (-not ([regex]::IsMatch($events, '(?<!\r)\n'))) 'CRLF must survive in generated copy'
    Write-Host 'PASS: triggered paranoia/exile events guarded; unrelated event, comments, BOM and CRLF preserved'

    $decisions = [IO.File]::ReadAllText((Join-Path $legacyTarget 'common/decisions/Soviet_mixed.txt'))
    Assert-Legacy ($decisions.Contains($routineDecision)) 'Unrelated decision must remain exact'
    Assert-Legacy ($decisions.Contains('OR = { SOV = { has_country_flag = sr_lito_initialized } AND = {')) 'Old mission cancels for Lito without replacing its original condition'
    Assert-Legacy ($decisions.Contains('has_war = yes')) 'Original cancellation condition must survive'
    Assert-Legacy (($decisions.Split(@('if = { limit = { NOT = { SOV = { has_country_flag = sr_lito_initialized } } }'), [StringSplitOptions]::None).Count - 1) -eq 3) 'Complete, timeout and cancel effects must all be protected'
    $categories = [IO.File]::ReadAllText((Join-Path $legacyTarget 'common/decisions/categories/Soviet.txt'))
    Assert-Legacy ($categories.Contains('SOV_trade_program = { icon = generic_trade visible = { tag = SOV } }')) 'Unrelated category must remain exact'
    Write-Host 'PASS: active Trotsky mission and all outcomes suppressed safely; unrelated decisions/categories preserved'

    $effects = [IO.File]::ReadAllText((Join-Path $legacyTarget 'common/scripted_effects/Soviet_mixed.txt'))
    $guis = [IO.File]::ReadAllText((Join-Path $legacyTarget 'common/scripted_guis/Soviet_mixed.txt'))
    Assert-Legacy ($effects.Contains($routineEffect)) 'Unrelated scripted effect must remain exact'
    Assert-Legacy ($effects.Contains($legacyGuard)) 'Paranoia scripted effect must be disabled for Lito'
    Assert-Legacy ($guis.Contains($routineGui)) 'Unrelated scripted GUI must remain exact'
    Assert-Legacy ($guis.Contains($legacyGuard)) 'Paranoia display needs visibility guard'
    $cleanup = [IO.File]::ReadAllText((Join-Path $legacyTarget 'common/on_actions/zz_sr_legacy_soviet_shutdown.txt'))
    Assert-Legacy ($cleanup.Contains('tag = SOV has_country_flag = sr_lito_initialized')) 'Daily cleanup must only affect Lito SOV'
    Assert-Legacy ($cleanup.Contains('set_variable = { SOV_paranoia = 0 }')) 'Discovered paranoia variable must be zeroed'
    Assert-Legacy ($cleanup.Contains('clr_country_flag = SOV_paranoia_active')) 'Discovered active flag must be cleared'
    Assert-Legacy ($cleanup.Contains('remove_ideas = SOV_political_paranoia') -and $cleanup.Contains('remove_ideas = SOV_trotskyist_opposition')) 'Only actual registered legacy ideas are removed'
    Assert-Legacy (-not $cleanup.Contains('SOV_industrial_program')) 'Ordinary national spirit must survive'
    Assert-Legacy ($cleanup.Contains('has_character = SOV_lev_trotsky') -and $cleanup.Contains('retire_character = SOV_lev_trotsky')) 'Only discovered Trotsky token may be retired, with recruitment guard'
    Assert-Legacy (-not $cleanup.Contains('SOV_ordinary_general')) 'Ordinary characters must survive'
    Write-Host 'PASS: meter, GUI, scripted effects, actual spirits and discovered Trotsky character handled without guessed IDs'

    foreach ($path in @($eventsPath, (Join-Path $legacyTarget 'common/decisions/Soviet_mixed.txt'),
        (Join-Path $legacyTarget 'common/scripted_effects/Soviet_mixed.txt'),
        (Join-Path $legacyTarget 'common/scripted_guis/Soviet_mixed.txt'),
        (Join-Path $legacyTarget 'common/on_actions/zz_sr_legacy_soviet_shutdown.txt'))) {
        $null = Get-ClausewitzTokens -Text ([IO.File]::ReadAllText($path))
    }
    $after = Get-LegacyHashes
    Assert-Legacy ($before.Count -eq $after.Count) 'No game files may be added or removed'
    foreach ($path in $before.Keys) { Assert-Legacy ($before[$path] -ceq $after[$path]) "Game source changed: $path" }
    Write-Host 'PASS: all generated scripts parse and every game source hash remains unchanged'

    # An optional unsupported historical file must not prevent installation.
    # Valid historical files must still be patched; rejected identifiers must
    # never leak into cleanup or successful-file counters.
    Write-LegacyFixture 'events/SOV_paranoia_broken.txt' 'country_event = { id = bad.1 immediate = { set_variable = { SOV_paranoia_broken = 7 } }'
    Write-LegacyFixture 'common/scripted_guis/SOV_paranoia_unsupported.txt' @'
scripted_gui = {
    SOV_paranoia_unsupported = {
        visible = { tag = SOV }
        visible = { has_war = no }
        effects = { set_variable = { SOV_paranoia_rejected_gui = 10 } }
    }
}
'@
    $badEncoding = Join-Path $legacyGame 'events/SOV_paranoia_encoding.txt'
    [IO.File]::WriteAllBytes($badEncoding, ([Text.Encoding]::ASCII.GetBytes('# SOV_paranoia ') + [byte[]]@(255, 254, 255)))
    $beforeOptional = Get-LegacyHashes
    $legacyWarnings = @()
    & $Installer -GamePath $legacyGame -SourceRoot $legacySource -ModDirectory $legacyMods -WarningVariable legacyWarnings
    $warningText = ($legacyWarnings | ForEach-Object { $_.Message }) -join "`n"
    Assert-Legacy ($warningText.Contains('SOV_paranoia_broken.txt')) 'Malformed optional file must be named'
    Assert-Legacy ($warningText.Contains('SOV_paranoia_unsupported.txt')) 'Unsupported optional file must be named'
    Assert-Legacy ($warningText.Contains('SOV_paranoia_encoding.txt')) 'Undecodable optional file must be named'
    Assert-Legacy ($warningText.Contains('nur teilweise gesperrt')) 'Incomplete historical suppression must be disclosed'
    Assert-Legacy ($warningText.Contains('3 optionale Datei(en)')) 'Only failed optional files may count as skipped'
    foreach ($relative in @('events/SOV_paranoia_broken.txt', 'common/scripted_guis/SOV_paranoia_unsupported.txt', 'events/SOV_paranoia_encoding.txt')) {
        Assert-Legacy (-not (Test-Path -LiteralPath (Join-Path $legacyTarget $relative))) "Rejected file must not be installed: $relative"
    }
    Assert-Legacy ([IO.File]::ReadAllText($eventsPath).Contains($legacyGuard)) 'Valid event files must still be protected'
    $cleanup = [IO.File]::ReadAllText((Join-Path $legacyTarget 'common/on_actions/zz_sr_legacy_soviet_shutdown.txt'))
    Assert-Legacy (-not $cleanup.Contains('SOV_paranoia_broken')) 'Malformed-file IDs must not leak into cleanup'
    Assert-Legacy (-not $cleanup.Contains('SOV_paranoia_rejected_gui')) 'Rejected-file IDs must not leak into cleanup'
    $afterOptional = Get-LegacyHashes
    foreach ($path in $beforeOptional.Keys) { Assert-Legacy ($beforeOptional[$path] -ceq $afterOptional[$path]) "Optional scan modified game source: $path" }
    Write-Host 'PASS: malformed, unsupported and non-UTF8 optional files are isolated with file-specific warnings; valid patches survive'
    Write-Host '5 legacy-Soviet synthetic integration groups passed. Native event execution and actual installed HOI4/DLC files remain untested.'
} finally {
    if (Test-Path -LiteralPath $legacyTestRoot) { Remove-Item -LiteralPath $legacyTestRoot -Recurse -Force }
}
