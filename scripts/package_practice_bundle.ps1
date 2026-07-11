param(
    [Parameter(Mandatory = $true)][string]$BundleRoot,
    [Parameter(Mandatory = $true)][string]$OutputDirectory,
    [string]$Version = ""
)
$ErrorActionPreference = 'Stop'
$script = Join-Path $PSScriptRoot 'package_practice_bundle.py'
$args = @($script, $BundleRoot, $OutputDirectory)
if ($Version) { $args += @('--version', $Version) }
python @args
if ($LASTEXITCODE -ne 0) { throw 'Presentation bundle packaging failed.' }
