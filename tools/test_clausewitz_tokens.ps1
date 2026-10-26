# Exercise the real installer lexer without executing the installer transaction.
[CmdletBinding()]
param([string]$Installer = (Join-Path $PSScriptRoot 'install_lito.ps1'))
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$parseTokens = $null
$parseErrors = $null
$scriptAst = [Management.Automation.Language.Parser]::ParseFile($Installer, [ref]$parseTokens, [ref]$parseErrors)
if ($parseErrors.Count -gt 0) { throw 'Installer has PowerShell syntax errors.' }
foreach ($name in @('Get-ClausewitzTokens', 'Get-ClosingBrace', 'Get-DirectBlock')) {
    $function = $scriptAst.Find({ param($node)
        ($node -is [Management.Automation.Language.FunctionDefinitionAst]) -and ($node.Name -eq $name)
    }, $true)
    if ($null -eq $function) { throw "Missing installer function: $name" }
    . ([ScriptBlock]::Create($function.Extent.Text))
}

$source = @'
ideologies = {
    # Comments contain ignored braces: } {
    communism = { types = { stalinism = { } } }
    democratic = { types = { liberalism = { } } }
}
'@
foreach ($newline in @("`n", "`r`n", "`r")) {
    $text = $source.Replace("`r`n", "`n").Replace("`n", $newline)
    $tokens = Get-ClausewitzTokens -Text $text
    $root = Get-DirectBlock -Tokens $tokens -Close $tokens.Count -Name 'ideologies'
    $communism = Get-DirectBlock -Tokens $tokens -Open $root.Open -Close $root.Close -Name 'communism'
    $types = Get-DirectBlock -Tokens $tokens -Open $communism.Open -Close $communism.Close -Name 'types'
    $null = Get-DirectBlock -Tokens $tokens -Open $types.Open -Close $types.Close -Name 'stalinism'
    Write-Host ('PASS: line-ending bytes ' + ([BitConverter]::ToString([Text.Encoding]::UTF8.GetBytes($newline))))
}

$quoted = 'root = { name = "literal { # }, escaped \" quote, and backslash \\" child = { } }'
$tokens = Get-ClausewitzTokens -Text $quoted
$null = Get-DirectBlock -Tokens $tokens -Close $tokens.Count -Name 'root'
Write-Host 'PASS: braces/comment signs and escaped quote/backslash inside strings are ignored structurally'

foreach ($invalid in @('root = { child = { }', 'root = { } }', 'root = { name = "unterminated')) {
    $failed = $false
    try { $null = Get-ClausewitzTokens -Text $invalid } catch { $failed = $true }
    if (-not $failed) { throw 'Malformed source was accepted by the strict lexer.' }
}
Write-Host 'PASS: genuinely unclosed/opening/excess braces and unterminated strings remain errors'
Write-Host '5 parser regression groups passed. These fixtures do not identify the user file that failed.'
