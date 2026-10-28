# Read-only native-source integration checks. Uses the user's own local sources;
# no original game files are bundled or modified. All mutations stay in TEMP.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$GameRoot,
    [string]$SourceRoot = (Split-Path -Parent $PSScriptRoot)
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$tempRoot = Join-Path ([IO.Path]::GetTempPath()) ('lito-native-test-' + [guid]::NewGuid().ToString('N'))
$stage = Join-Path $tempRoot 'soviet_renewal'

function Assert-Native {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw ('FAIL: ' + $Message) }
}
function Get-NativeSnapshot {
    param([string]$Root)
    $result = @{}
    foreach ($file in @(Get-ChildItem -LiteralPath $Root -File -Recurse)) {
        $relative = $file.FullName.Substring($Root.Length).TrimStart([char[]]'\/')
        $result[$relative] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
    }
    return $result
}
function Assert-NativeSnapshot {
    param([object]$Before, [object]$After)
    Assert-Native ($Before.Count -eq $After.Count) 'Staged file inventory changed unexpectedly'
    foreach ($key in $Before.Keys) { Assert-Native ($After.ContainsKey($key) -and $Before[$key] -ceq $After[$key]) ('File changed: ' + $key) }
}
function Assert-NativeCustomChoices {
    param([string]$Stage)
    $nativeText = [IO.File]::ReadAllText((Join-Path $Stage 'common/decisions/SOV.txt'))
    $tokens = Get-ClausewitzTokens -Text $nativeText -SourceName 'prepared native decisions'
    $category = @(Get-LitoScriptEntries -Tokens $tokens | Where-Object { $_.Name -ceq 'SOV_propaganda_campaigns' })
    Assert-Native ($category.Count -eq 1) 'Native campaign category is not unique'
    $originalChoices = @(Get-LitoScriptEntries -Tokens $tokens -Open $category[0].Open -Close $category[0].Close)
    Assert-Native ($originalChoices.Count -eq 28) 'Expected all 24 historical campaigns and four debug controls'
    foreach ($choice in $originalChoices) {
        $visible = @(Get-LitoScriptEntries -Tokens $tokens -Open $choice.Open -Close $choice.Close | Where-Object { $_.Name -ceq 'visible' })
        Assert-Native ($visible.Count -eq 1) ('Expected one visibility block: ' + $choice.Name)
        $guards = @(Get-LitoScriptEntries -Tokens $tokens -Open $visible[0].Open -Close $visible[0].Close | Where-Object { $_.Name -ceq 'NOT' -and $_.IsBlock })
        $found = 0
        foreach ($guard in $guards) {
            $and = @(Get-LitoScriptEntries -Tokens $tokens -Open $guard.Open -Close $guard.Close)
            if ($and.Count -ne 1 -or $and[0].Name -cne 'AND' -or -not $and[0].IsBlock) { continue }
            $terms = @(Get-LitoScriptEntries -Tokens $tokens -Open $and[0].Open -Close $and[0].Close)
            if ($terms.Count -eq 2 -and @($terms | Where-Object { $_.Name -ceq 'tag' -and $_.Value -ceq 'SOV' }).Count -eq 1 -and
                @($terms | Where-Object { $_.Name -ceq 'has_country_flag' -and $_.Value -ceq 'sr_lito_initialized' }).Count -eq 1) { $found++ }
        }
        Assert-Native ($found -eq 1) ('Missing unique Lito-only exclusion guard: ' + $choice.Name)
    }
    $customText = [IO.File]::ReadAllText((Join-Path $Stage 'common/decisions/sr_lito_native_propaganda.txt'))
    $customTokens = Get-ClausewitzTokens -Text $customText -SourceName 'custom native campaigns'
    $customRoot = @(Get-LitoScriptEntries -Tokens $customTokens)
    Assert-Native ($customRoot.Count -eq 1 -and $customRoot[0].Name -ceq 'SOV_propaganda_campaigns') 'Custom campaigns must extend the native category'
    $customIds = @(Get-LitoScriptEntries -Tokens $customTokens -Open $customRoot[0].Open -Close $customRoot[0].Close | ForEach-Object { $_.Name } | Sort-Object)
    Assert-Native (($customIds -join ',') -ceq 'sr_lito_propaganda_light,sr_lito_propaganda_peoples,sr_lito_propaganda_star') 'Exactly three custom campaign IDs are required'
}

try {
    $GameRoot = [IO.Path]::GetFullPath($GameRoot).TrimEnd([char[]]'\/')
    $installerAst = [Management.Automation.Language.Parser]::ParseFile((Join-Path $SourceRoot 'tools/install_lito.ps1'), [ref]$null, [ref]$null)
    foreach ($name in @('Get-ClausewitzTokens', 'Get-ClosingBrace', 'Get-DirectBlock', 'Get-LitoScriptEntries',
            'Test-LitoLegacyName', 'Add-LitoLegacyGuard', 'Add-LitoLegacyDecisionGuards', 'Add-LitoLegacyEventEffects', 'Protect-LitoLegacySoviet')) {
        $definition = $installerAst.Find({ param($node)
            $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq $name
        }, $true)
        if ($null -eq $definition) { throw ('Missing shared installer function: ' + $name) }
        . ([ScriptBlock]::Create($definition.Extent.Text))
    }
    foreach ($name in @('install_native_agitprop_gui', 'install_native_agitprop')) {
        . ([ScriptBlock]::Create([IO.File]::ReadAllText((Join-Path $SourceRoot ('tools/' + $name + '.ps1')), [Text.Encoding]::UTF8)))
    }
    $sourceFiles = @('common/decisions/SOV.txt', 'common/decisions/categories/SOV_decision_categories.txt',
        'common/scripted_effects/SOV_scripted_effects.txt', 'common/scripted_guis/SOV_propaganda_campaigns_scripted_gui.txt',
        'common/national_focus/soviet.txt', 'history/countries/SOV - Soviet union.txt',
        'interface/propaganda.gfx', 'interface/sov_propaganda_campaigns_scripted_gui.gui')
    $gameBefore = @{}
    foreach ($relative in $sourceFiles) {
        $gameBefore[$relative] = (Get-FileHash -LiteralPath (Join-Path $GameRoot $relative) -Algorithm SHA256).Hash
    }
    New-Item -ItemType Directory -Path $tempRoot | Out-Null
    Copy-Item -LiteralPath (Join-Path $SourceRoot 'soviet_renewal') -Destination $stage -Recurse
    Protect-LitoLegacySoviet -GameRoot $GameRoot -StagedMod $stage
    Assert-Native (Install-LitoNativeAgitprop -GameRoot $GameRoot -StagedMod $stage) 'Native installation failed'
    $runtime = [IO.File]::ReadAllText((Join-Path $stage 'common/scripted_effects/sr_native_agitprop_effects.txt'))
    Assert-Native ($runtime.Contains('set_country_flag = sr_lito_native_agitprop_ready')) 'Validated feature must expose readiness'
    $categoryText = [IO.File]::ReadAllText((Join-Path $stage 'common/decisions/categories/SOV_decision_categories.txt'))
    Assert-Native ($categoryText.Contains('NOT = { SOV = { has_country_flag = sr_lito_initialized } }')) 'Historical category guards were lost'
    Assert-Native ($categoryText.Contains('has_country_flag = sr_lito_native_agitprop_unlocked')) 'Lito focus alias missing'
    Write-Host 'PASS: native installation after historical guards preserves guards and exposes validated readiness'
    Assert-NativeCustomChoices -Stage $stage
    Write-Host 'PASS: all 28 original choices have a unique Lito exclusion and three own campaigns extend the native category'

    $before = Get-NativeSnapshot -Root $stage
    Assert-Native (Install-LitoNativeAgitprop -GameRoot $GameRoot -StagedMod $stage) 'Repeated native installation failed'
    Assert-NativeSnapshot -Before $before -After (Get-NativeSnapshot -Root $stage)
    Write-Host 'PASS: repeated native preparation is byte-identical'

    $poster = Join-Path $stage 'gfx/interface/agitprop/sr_agitprop_star.dds'
    $posterBytes = [IO.File]::ReadAllBytes($poster)
    [IO.File]::WriteAllBytes($poster, [byte[]]@(1, 2, 3))
    $beforeFailure = Get-NativeSnapshot -Root $stage
    Assert-Native (-not (Install-LitoNativeAgitprop -GameRoot $GameRoot -StagedMod $stage -WarningAction SilentlyContinue)) 'Invalid poster must reject native preparation'
    Assert-NativeSnapshot -Before $beforeFailure -After (Get-NativeSnapshot -Root $stage)
    [IO.File]::WriteAllBytes($poster, $posterBytes)
    Write-Host 'PASS: native preparation failure leaves every staged file unchanged'

    foreach ($relative in $sourceFiles) {
        $after = (Get-FileHash -LiteralPath (Join-Path $GameRoot $relative) -Algorithm SHA256).Hash
        Assert-Native ($gameBefore[$relative] -ceq $after) ('Original game source changed: ' + $relative)
    }
    Write-Host 'PASS: all inspected original game sources remain byte-identical'
    Write-Host '5 native-source installation scenarios passed. No HOI4 engine or GUI rendering test.'
} finally {
    if (Test-Path -LiteralPath $tempRoot) { Remove-Item -LiteralPath $tempRoot -Recurse -Force }
}
