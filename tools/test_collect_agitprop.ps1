# Synthetic collector checks. No game installation or rendering is involved.
[CmdletBinding()]
param([string]$Collector = (Join-Path (Split-Path -Parent $PSScriptRoot) 'collect_lito_agitprop.ps1'))
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$testRoot = Join-Path ([IO.Path]::GetTempPath()) ('lito-collect-tests-' + [guid]::NewGuid().ToString('N'))
$game = Join-Path $testRoot 'game'
$reports = Join-Path $testRoot 'reports'
$utf8 = [Text.UTF8Encoding]::new($true)
$passes = 0

function Assert-Collector {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw "FAIL: $Message" }
}
function Write-CollectorFixture {
    param([string]$Relative, [string]$Text)
    $path = Join-Path $game $Relative
    New-Item -ItemType Directory -Path (Split-Path -Parent $path) -Force | Out-Null
    [IO.File]::WriteAllText($path, $Text, $utf8)
}
function Get-CollectorSnapshot {
    $result = @{}
    foreach ($file in @(Get-ChildItem -LiteralPath $game -Recurse -File)) {
        $result[$file.FullName] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
    }
    return $result
}
try {
    Write-CollectorFixture 'common/ideologies/00_ideologies.txt' 'ideologies = { }'
    Write-CollectorFixture 'common/decisions/SOV_campaigns.txt' 'SOV_propaganda_campaigns = { SOV_propaganda_native = { complete_effect = { SOV_pick_propaganda_campaign_slot_effect = yes } } }'
    Write-CollectorFixture 'common/decisions/categories/SOV_categories.txt' 'SOV_propaganda_campaigns = { icon = generic }'
    Write-CollectorFixture 'common/scripted_effects/SOV_effects.txt' ("# Source with CR only`rSOV_pick_propaganda_campaign_slot_effect = { set_variable = { SOV_poster_left_icon_frame = SOV_new_propaganda_campaign } }`r")
    Write-CollectorFixture 'common/scripted_effects/reset_helper_only.txt' 'SOV_reset_propaganda_campaign_slot_effect = { generic_helper_effect = yes }'
    Write-CollectorFixture 'common/scripted_triggers/SOV_triggers.txt' 'SOV_propaganda_poster_slot_available = { always = yes }'
    Write-CollectorFixture 'common/scripted_guis/mixed_panels.txt' @'
scripted_gui = {
    native_panel = {
        window_name = "native_actual_window"
        properties = { poster_left = { frame = SOV_poster_left_icon_frame image = "GFX_native_inline" } }
    }
    unrelated_panel = { window_name = "irrelevant_window" properties = { other = { image = "GFX_not_needed" } } }
}
'@
    Write-CollectorFixture 'interface/native_window.gui' @'
guiTypes = {
    containerWindowType = {
        name = "native_actual_window"
        iconType = { name = "poster_left" spriteType = "GFX_native_poster" }
    }
    containerWindowType = {
        name = "unrelated_sibling"
        iconType = { name = "other_icon" spriteType = "GFX_not_needed" }
    }
}
'@
    Write-CollectorFixture 'interface/not_the_window.gui' 'guiTypes = { containerWindowType = { name = "different_window" text = "native_actual_window" } }'
    Write-CollectorFixture 'interface/native_poster.gfx' 'spriteTypes = { spriteType = { name = "GFX_native_poster" texturefile = "gfx/native.dds" } }'
    Write-CollectorFixture 'interface/mixed_native.gfx' 'spriteTypes = { spriteType = { name = "GFX_SOV_propaganda_shared" texturefile = "gfx/shared.dds" } spriteType = { name = "GFX_native_inline" texturefile = "gfx/inline.dds" } }'
    Write-CollectorFixture 'interface/irrelevant.gfx' 'spriteTypes = { spriteType = { name = "GFX_not_needed" texturefile = "gfx/irrelevant.dds" } }'
    Write-CollectorFixture 'common/decisions/unrelated.txt' 'completely_unrelated_decisions = { other_decision = { cost = 15 } }'
    Write-CollectorFixture 'save games/do_not_collect.txt' 'SOV_propaganda_campaigns = private_save_information'
    Write-CollectorFixture 'logs/do_not_collect.txt' 'SOV_propaganda_campaigns = private_log_information'
    $before = Get-CollectorSnapshot
    $result = & $Collector -GamePath $game -OutputDirectory $reports -WarningAction SilentlyContinue
    $report = [IO.File]::ReadAllText($result.ReportPath)
    Assert-Collector ($result.FileCount -eq 9) "Expected exactly nine relevant files, got $($result.FileCount)"
    Assert-Collector ($report.Contains('===== BEGIN FILE: common/scripted_effects/reset_helper_only.txt =====')) 'Confirmed native effect declaration must be selected even without known variables in its body'
    Assert-Collector ($report.Contains('===== BEGIN FILE: interface/native_window.gui =====')) 'Referenced GUI file must be collected'
    Assert-Collector ($report.Contains('===== BEGIN FILE: interface/native_poster.gfx =====')) 'Sprite referenced by actual GUI must be followed'
    Assert-Collector ($report.Contains('===== BEGIN FILE: interface/mixed_native.gfx =====')) 'Initial and dependent sprite in same file must be preserved'
    Assert-Collector (($report.Split(@('===== BEGIN FILE: interface/mixed_native.gfx ====='), [StringSplitOptions]::None).Count - 1) -eq 1) 'Mixed source must not be duplicated'
    foreach ($relative in @('interface/not_the_window.gui', 'interface/irrelevant.gfx', 'common/decisions/unrelated.txt', 'save games/do_not_collect.txt', 'logs/do_not_collect.txt')) {
        Assert-Collector (-not $report.Contains(('===== BEGIN FILE: ' + $relative + ' ====='))) "Unrelated or private file included: $relative"
    }
    $passes++; Write-Host 'PASS: native script, referenced GUI/sprites, mixed files and bounded source selection'

    $after = Get-CollectorSnapshot
    Assert-Collector ($before.Count -eq $after.Count) 'Game inventory changed'
    foreach ($key in $before.Keys) { Assert-Collector ($before[$key] -ceq $after[$key]) "Game source changed: $key" }
    Assert-Collector ($report.Contains('Zeilenenden CR')) 'Original CR line endings must be reported'
    Assert-Collector ($report.Contains('UTF8-BOM True')) 'Original BOM metadata missing'
    Assert-Collector ($report.Contains('SHA256')) 'Source hashes missing'
    Assert-Collector ($report.Contains('DLC-Unterordner und DLC-Archive wurden nicht durchsucht')) 'DLC search limitation must be explicit'
    $reportBytes = [IO.File]::ReadAllBytes($result.ReportPath)
    Assert-Collector (($reportBytes[0] -eq 239) -and ($reportBytes[1] -eq 187) -and ($reportBytes[2] -eq 191)) 'Report must carry UTF-8 BOM'
    $repeat = & $Collector -GamePath $game -OutputDirectory $reports -CreateZip -WarningAction SilentlyContinue
    Assert-Collector ($result.ReportPath -cne $repeat.ReportPath) 'Repeated collection must use a unique output name'
    Assert-Collector (Test-Path -LiteralPath $result.ReportPath) 'Earlier report must remain intact'
    $zipPath = [IO.Path]::ChangeExtension($repeat.ReportPath, '.zip')
    Assert-Collector (Test-Path -LiteralPath $zipPath) 'Requested ZIP must be created beside its report'
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [IO.Compression.ZipFile]::OpenRead($zipPath)
    try {
        Assert-Collector ($zip.Entries.Count -eq 1) 'ZIP must contain only the diagnostic report'
        Assert-Collector ($zip.Entries[0].Name -ceq [IO.Path]::GetFileName($repeat.ReportPath)) 'ZIP report filename mismatch'
    } finally { $zip.Dispose() }
    $passes++; Write-Host 'PASS: game is unchanged, full metadata/BOM, unique repeated report, explicit DLC limitation'

    Remove-Item -LiteralPath (Join-Path $game 'interface/native_poster.gfx')
    Remove-Item -LiteralPath (Join-Path $game 'common/scripted_triggers/SOV_triggers.txt')
    Write-CollectorFixture 'common/decisions/truncated_original.txt' 'SOV_propaganda_campaigns = { SOV_propaganda_truncated = {'
    $badEncoding = Join-Path $game 'common/scripted_effects/SOV_broken_encoding.txt'
    [IO.File]::WriteAllBytes($badEncoding, [Text.Encoding]::ASCII.GetBytes('SOV_new_propaganda_campaign ') + [byte[]]@(255, 255))
    $partial = & $Collector -GamePath $game -OutputDirectory $reports -WarningAction SilentlyContinue
    $partialText = [IO.File]::ReadAllText($partial.ReportPath)
    Assert-Collector ($partialText.Contains('Sprite-Definition nicht gefunden: GFX_native_poster')) 'Missing sprite must be reported'
    Assert-Collector ($partialText.Contains('Keine passenden Dateien: Scripted Triggers')) 'Missing native trigger group must be reported'
    Assert-Collector ($partialText.Contains('SOV_broken_encoding.txt :')) 'Invalid selected UTF-8 must be identified by filename'
    Assert-Collector ($partialText.Contains('===== BEGIN FILE: common/decisions/truncated_original.txt =====')) 'Collector must retain actual incomplete originals for diagnosis'
    Assert-Collector ($partial.WarningCount -ge 4) 'Partial report must expose limitations'
    $passes++; Write-Host 'PASS: absent dependencies/invalid encoding identified, incomplete originals still collected'

    $rejected = $false
    try { $null = & $Collector -GamePath $game -OutputDirectory (Join-Path $game 'do_not_write_here') -WarningAction SilentlyContinue }
    catch { $rejected = $_.Exception.Message -match 'ausserhalb' }
    Assert-Collector $rejected 'Report writes inside game must be rejected'
    Assert-Collector (-not (Test-Path -LiteralPath (Join-Path $game 'do_not_write_here'))) 'Forbidden output folder must not be created'
    $passes++; Write-Host 'PASS: report output inside game is rejected before any writes'
    Write-Host "$passes synthetic collector scenarios passed. No real HOI4 GUI validation."
} finally {
    if (Test-Path -LiteralPath $testRoot) { Remove-Item -LiteralPath $testRoot -Recurse -Force }
}
