# Self-contained installer regression checks. Uses synthetic game files in TEMP;
# this checks installation mechanics, not HOI4 gameplay or image rendering.
[CmdletBinding()]
param([string]$Installer = (Join-Path $PSScriptRoot 'install_lito.ps1'))
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$testRoot = Join-Path ([IO.Path]::GetTempPath()) ('lito-tests-' + [guid]::NewGuid().ToString('N'))
$game = Join-Path $testRoot 'game'
$source = Join-Path $testRoot 'source'
$destination = Join-Path $testRoot 'mod'
$vanillaFile = Join-Path $game 'common/ideologies/00_ideologies.txt'
$installedMod = Join-Path $destination 'soviet_renewal'
$installedFile = Join-Path $installedMod 'common/ideologies/00_ideologies.txt'
$externalDescriptor = Join-Path $destination 'soviet_renewal.mod'
$utf8 = [Text.UTF8Encoding]::new($true)
$passes = 0

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw "FAIL: $Message" }
}
function Invoke-TestInstaller {
    & $Installer -GamePath $game -ModDirectory $destination -SourceRoot $source
}
function Assert-Aborts {
    param([string]$Expected)
    $caught = $false
    try { Invoke-TestInstaller } catch {
        $caught = $true
        Assert-True ($_.Exception.Message -match $Expected) "Unexpected failure: $($_.Exception.Message)"
    }
    Assert-True $caught 'The invalid fixture did not abort'
}

try {
    foreach ($folder in @('game/common/ideologies', 'game/gfx/leaders/Europe', 'source/soviet_renewal/common/characters')) {
        New-Item -ItemType Directory -Path (Join-Path $testRoot $folder) -Force | Out-Null
    }
    $original = @'
# ignored: communism = { types = { } }
ideologies = {
    democratic = { types = { liberalism = {} } color = { 1 2 3 } }
    communism = {
        # ignored braces: { }
        types = {
            marxism = { description = "Quoted { brace }, # and escaped \" quote" }
            leninism = {}
            stalinism = {}
        }
        color = { 255 0 0 }
        rules = { can_puppet = yes }
        modifiers = { drift_defence_factor = 0.3 }
    }
    neutrality = { types = { despotism = {} } color = { 50 50 50 } }
    fascism = { types = { nazism = {} } color = { 60 60 60 } }
}
'@
    [IO.File]::WriteAllText($vanillaFile, $original, $utf8)
    [IO.File]::WriteAllText((Join-Path $game 'gfx/leaders/Europe/Portrait_Europe_Generic_1.dds'), 'Synthetic DDS placeholder; no rendering tested.')
    [IO.File]::WriteAllText((Join-Path $source 'soviet_renewal/descriptor.mod'), "name=`"Lito Test`"`nversion=`"0.0.0`"`n")
    [IO.File]::WriteAllText((Join-Path $source 'soviet_renewal/common/characters/test.txt'), 'characters = { SOV_test = { name = "Test" } }')
    $flagFixtures = @(
        @{ CosmeticTag = 'SOV_LITO_SFSU'; RelativePath = 'gfx/flags'; SourceName = 'SOV_communism.tga'; Marker = 'SOV normal communist flag bytes' },
        @{ CosmeticTag = 'SOV_LITO_SFSU'; RelativePath = 'gfx/flags/medium'; SourceName = 'SOV.tga'; Marker = 'SOV medium base flag bytes' },
        @{ CosmeticTag = 'SOV_LITO_SFSU'; RelativePath = 'gfx/flags/small'; SourceName = 'SOV_communism.tga'; Marker = 'SOV small communist flag bytes' },
        @{ CosmeticTag = 'YUG_LITO_BALKAN'; RelativePath = 'gfx/flags'; SourceName = 'YUG_communism.tga'; Marker = 'YUG normal communist flag bytes' },
        @{ CosmeticTag = 'YUG_LITO_BALKAN'; RelativePath = 'gfx/flags/medium'; SourceName = 'YUG.tga'; Marker = 'YUG medium base flag bytes' },
        @{ CosmeticTag = 'YUG_LITO_BALKAN'; RelativePath = 'gfx/flags/small'; SourceName = 'YUG_communism.tga'; Marker = 'YUG small communist flag bytes' }
    )
    $gameFlagHashes = @{}
    foreach ($fixture in $flagFixtures) {
        $folder = Join-Path $game $fixture.RelativePath
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        $flagFile = Join-Path $folder $fixture.SourceName
        [IO.File]::WriteAllBytes($flagFile, [Text.Encoding]::UTF8.GetBytes($fixture.Marker))
        $gameFlagHashes[$flagFile] = (Get-FileHash -LiteralPath $flagFile -Algorithm SHA256).Hash
    }
    # A second normal-size flag verifies that communism takes precedence.
    [IO.File]::WriteAllText((Join-Path $game 'gfx/flags/SOV.tga'), 'Do not choose this normal base flag')
    [IO.File]::WriteAllText((Join-Path $game 'gfx/flags/YUG.tga'), 'Do not choose this normal YUG base flag')
    $originalHash = (Get-FileHash -LiteralPath $vanillaFile -Algorithm SHA256).Hash

    Invoke-TestInstaller
    $installed = [IO.File]::ReadAllText($installedFile)
    $installedBytes = [IO.File]::ReadAllBytes($installedFile)
    $added = "`n            titoism = { can_be_randomly_selected = no }`n"
    Assert-True ($installed.Replace($added, '') -ceq $original) 'All original ideology text must be preserved'
    Assert-True (($installedBytes[0] -eq 239) -and ($installedBytes[1] -eq 187) -and ($installedBytes[2] -eq 191)) 'Source UTF-8 BOM must be preserved'
    Assert-True (($installed.Split(@('titoism ='), [StringSplitOptions]::None).Count - 1) -eq 1) 'Exactly one subtype is added'
    Assert-True ((Get-FileHash -LiteralPath $vanillaFile -Algorithm SHA256).Hash -ceq $originalHash) 'Game file must be unchanged'
    Assert-True ([IO.File]::ReadAllText($externalDescriptor).Contains($installedMod.Replace('\', '/'))) 'Descriptor must use absolute mod path'
    $portraitSprites = [IO.File]::ReadAllText((Join-Path $installedMod 'interface/sr_lito_portrait.gfx'))
    Assert-True $portraitSprites.Contains('GFX_sr_lito_portrait') 'Lito sprite must be defined'
    Assert-True $portraitSprites.Contains('GFX_sr_balkan_council_portrait') 'Balkan council needs a separate sprite name for future custom art'
    Assert-True $portraitSprites.Contains('GFX_sr_kardelj_portrait') 'Kardelj needs a separate portrait sprite'
    Assert-True (($portraitSprites.Split(@('gfx/leaders/Europe/Portrait_Europe_Generic_1.dds'), [StringSplitOptions]::None).Count - 1) -eq 3) 'All missing portrait sprites must point to the verified installed generic asset'
    foreach ($fixture in $flagFixtures) {
        $cosmeticTag = $fixture.CosmeticTag
        foreach ($flagName in @("$cosmeticTag.tga", "${cosmeticTag}_communism.tga")) {
            $flagFile = Join-Path (Join-Path $installedMod $fixture.RelativePath) $flagName
            Assert-True ([IO.File]::ReadAllText($flagFile) -ceq $fixture.Marker) "Cosmetic flag bytes must match local source: $flagFile"
        }
    }
    $passes++; Write-Host 'PASS: first install, exact text/BOM preservation, descriptor, three portraits and twelve cosmetic flags'

    [IO.File]::WriteAllText((Join-Path $installedMod 'user-marker.txt'), 'Preserve this in backup')
    $customFlag = Join-Path $source 'soviet_renewal/gfx/flags/SOV_LITO_SFSU_communism.tga'
    New-Item -ItemType Directory -Path (Split-Path -Parent $customFlag) -Force | Out-Null
    [IO.File]::WriteAllText($customFlag, 'Custom user-supplied flag bytes')
    $customBalkanFlag = Join-Path $source 'soviet_renewal/gfx/flags/small/YUG_LITO_BALKAN.tga'
    New-Item -ItemType Directory -Path (Split-Path -Parent $customBalkanFlag) -Force | Out-Null
    [IO.File]::WriteAllText($customBalkanFlag, 'Custom user-supplied Balkan flag bytes')
    $customPortraitFile = Join-Path $source 'soviet_renewal/interface/sr_custom_portraits.gfx'
    New-Item -ItemType Directory -Path (Split-Path -Parent $customPortraitFile) -Force | Out-Null
    $customPortraitText = "spriteTypes = {`n    spriteType = {`n        name = `"GFX_sr_lito_portrait`"`n        texturefile = `"gfx/leaders/SOV/custom.dds`"`n    }`n}`n"
    [IO.File]::WriteAllText($customPortraitFile, $customPortraitText)
    Invoke-TestInstaller
    $backups = @(Get-ChildItem -LiteralPath $destination -Directory -Filter 'soviet_renewal.backup-*')
    Assert-True ($backups.Count -eq 1) 'Repeat installation must create one backup'
    Assert-True (Test-Path -LiteralPath (Join-Path $backups[0].FullName 'user-marker.txt')) 'Previous user files must survive in backup'
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $installedMod 'user-marker.txt'))) 'New target must be a fresh staged copy'
    Assert-True ([IO.File]::ReadAllText((Join-Path $installedMod 'gfx/flags/SOV_LITO_SFSU_communism.tga')) -ceq 'Custom user-supplied flag bytes') 'Source-supplied custom flag must never be overwritten'
    Assert-True ([IO.File]::ReadAllText((Join-Path $installedMod 'gfx/flags/small/YUG_LITO_BALKAN.tga')) -ceq 'Custom user-supplied Balkan flag bytes') 'Source-supplied custom Balkan flag must never be overwritten'
    Assert-True ([IO.File]::ReadAllText((Join-Path $installedMod 'interface/sr_custom_portraits.gfx')) -ceq $customPortraitText) 'Supplied Lito portrait binding must survive installation'
    Assert-True (-not [IO.File]::ReadAllText((Join-Path $installedMod 'interface/sr_lito_portrait.gfx')).Contains('GFX_sr_lito_portrait')) 'No duplicate fallback may replace the custom Lito sprite'
    $passes++; Write-Host 'PASS: repeat install preserves backup, custom flags and the custom Lito portrait binding'

    $installedHash = (Get-FileHash -LiteralPath $installedFile -Algorithm SHA256).Hash
    [IO.File]::WriteAllText($vanillaFile, $original.Replace('leninism = {}', 'leninism = {} titoism = {}'), $utf8)
    Assert-Aborts 'bereits titoism'
    Assert-True ((Get-FileHash -LiteralPath $installedFile -Algorithm SHA256).Hash -ceq $installedHash) 'Collision must not alter installed mod'
    $passes++; Write-Host 'PASS: existing subtype collision aborts without altering destination'

    [IO.File]::WriteAllText($vanillaFile, $original + "`n}", $utf8)
    Assert-Aborts 'Klammer'
    Assert-True ((Get-FileHash -LiteralPath $installedFile -Algorithm SHA256).Hash -ceq $installedHash) 'Malformed source must not alter installed mod'
    $brokenOpen = $original + "`nideologies = {"
    [IO.File]::WriteAllText($vanillaFile, $brokenOpen, $utf8)
    $descriptorBeforeParseFailure = [IO.File]::ReadAllText($externalDescriptor)
    Assert-Aborts '00_ideologies\.txt.*Zeile'
    Assert-True ((Get-FileHash -LiteralPath $installedFile -Algorithm SHA256).Hash -ceq $installedHash) 'Unclosed ideology source must not alter installed mod'
    Assert-True ([IO.File]::ReadAllText($externalDescriptor) -ceq $descriptorBeforeParseFailure) 'Unclosed ideology source must not alter descriptor'
    $passes++; Write-Host 'PASS: malformed braces abort without altering destination'

    [IO.File]::WriteAllText($vanillaFile, $original, $utf8)
    [IO.File]::WriteAllText((Join-Path $installedMod 'rollback-marker.txt'), 'Must be restored')
    $oldDescriptor = [IO.File]::ReadAllText($externalDescriptor)
    $global:LitoTestFailCopyDestination = $installedMod
    function Copy-Item {
        [CmdletBinding()]
        param([string]$LiteralPath, [string]$Destination, [switch]$Recurse)
        if ($Destination -eq $global:LitoTestFailCopyDestination) { throw 'Injected installation copy failure' }
        Microsoft.PowerShell.Management\Copy-Item @PSBoundParameters
    }
    try { Assert-Aborts 'Injected installation copy failure' } finally {
        Remove-Item Function:\Copy-Item
        Remove-Variable -Name LitoTestFailCopyDestination -Scope Global
    }
    Assert-True (Test-Path -LiteralPath (Join-Path $installedMod 'rollback-marker.txt')) 'Rollback must restore prior mod folder'
    Assert-True ([IO.File]::ReadAllText($externalDescriptor) -ceq $oldDescriptor) 'Rollback must restore prior descriptor'
    Assert-True ((Get-FileHash -LiteralPath $vanillaFile -Algorithm SHA256).Hash -ceq $originalHash) 'Game file must remain unchanged after all tests'
    foreach ($flagFile in $gameFlagHashes.Keys) {
        Assert-True ((Get-FileHash -LiteralPath $flagFile -Algorithm SHA256).Hash -ceq $gameFlagHashes[$flagFile]) 'Installed game flag bytes must remain unchanged'
    }
    $passes++; Write-Host 'PASS: injected copy failure rolls back both previous targets'

    $crlfOriginal = $original.Replace("`r`n", "`n").Replace("`n", "`r`n")
    [IO.File]::WriteAllText($vanillaFile, $crlfOriginal, [Text.UTF8Encoding]::new($false))
    $crlfHash = (Get-FileHash -LiteralPath $vanillaFile -Algorithm SHA256).Hash
    # Missing local flag assets are a warning, not a reason to abort an install.
    Remove-Item -LiteralPath (Join-Path $game 'gfx/flags') -Recurse -Force
    $missingFlagWarnings = @()
    & $Installer -GamePath $game -ModDirectory $destination -SourceRoot $source -WarningVariable missingFlagWarnings
    Assert-True ($missingFlagWarnings.Count -ge 6) 'Missing flag assets must report a clear warning for each country and size'
    Assert-True ([IO.File]::ReadAllText((Join-Path $installedMod 'gfx/flags/SOV_LITO_SFSU_communism.tga')) -ceq 'Custom user-supplied flag bytes') 'Custom flag must survive even without vanilla flag assets'
    Assert-True ([IO.File]::ReadAllText((Join-Path $installedMod 'gfx/flags/small/YUG_LITO_BALKAN.tga')) -ceq 'Custom user-supplied Balkan flag bytes') 'Custom Balkan flag must survive even without vanilla flag assets'
    $installed = [IO.File]::ReadAllText($installedFile)
    $crlfInsertion = "`r`n            titoism = { can_be_randomly_selected = no }`r`n"
    Assert-True ($installed.Replace($crlfInsertion, '') -ceq $crlfOriginal) 'CRLF source text must be preserved'
    $installedBytes = [IO.File]::ReadAllBytes($installedFile)
    Assert-True (-not (($installedBytes[0] -eq 239) -and ($installedBytes[1] -eq 187) -and ($installedBytes[2] -eq 191))) 'No BOM may be added to a BOM-free source'
    Assert-True ((Get-FileHash -LiteralPath $vanillaFile -Algorithm SHA256).Hash -ceq $crlfHash) 'CRLF game file must remain unchanged'
    $passes++; Write-Host 'PASS: CRLF/BOM-free source remains intact; missing flags warn without aborting'
    $crOriginal = $original.Replace("`r`n", "`n").Replace("`n", "`r")
    [IO.File]::WriteAllText($vanillaFile, $crOriginal, [Text.UTF8Encoding]::new($true))
    & $Installer -GamePath $game -ModDirectory $destination -SourceRoot $source -WarningAction SilentlyContinue
    $crInstalled = [IO.File]::ReadAllText($installedFile)
    $crInsertion = "`r            titoism = { can_be_randomly_selected = no }`r"
    Assert-True ($crInstalled.Replace($crInsertion, '') -ceq $crOriginal) 'CR-only source with comments must preserve its original bytes after insertion removal'
    Assert-True (-not $crInstalled.Contains("`n")) 'CR-only source must retain CR-only line endings'
    $passes++; Write-Host 'PASS: CR-only ideology comments parse correctly and line endings survive installation'
    Write-Host "$passes installer regression scenarios passed. HOI4 engine and Windows-specific Steam discovery were not tested."
} finally {
    if (Test-Path -LiteralPath $testRoot) { Remove-Item -LiteralPath $testRoot -Recurse -Force }
}
