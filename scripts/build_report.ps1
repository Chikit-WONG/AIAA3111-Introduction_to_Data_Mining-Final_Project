param([string]$ReportDirectory = '', [switch]$Offline)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
if (-not $ReportDirectory) {
    $ReportDirectory = Join-Path (Split-Path -Parent $projectRoot) ((Split-Path -Leaf $projectRoot) + '-Report')
}
$reportPath = (Resolve-Path -LiteralPath $ReportDirectory).Path
$compiler = Join-Path $projectRoot 'tools\bin\tectonic.exe'
if (-not (Test-Path -LiteralPath $compiler)) { throw 'Run python scripts/bootstrap_tex.py first, or compile main.tex in Overleaf.' }
$cachePath = Join-Path $projectRoot 'tools\cache'
New-Item -ItemType Directory -Force -Path $cachePath | Out-Null
# Extended-length path avoids Windows MAX_PATH failures in the format cache.
$env:TECTONIC_CACHE_DIR = '\\?\' + $cachePath
$buildPath = Join-Path $reportPath 'build'
New-Item -ItemType Directory -Force -Path $buildPath | Out-Null
$compilerArgs = @('--untrusted', '--keep-logs', '--outdir', $buildPath)
if ($Offline) { $compilerArgs += '--only-cached' }
$compilerArgs += (Join-Path $reportPath 'main.tex')
& $compiler @compilerArgs
if ($LASTEXITCODE -ne 0) { throw 'LaTeX compilation failed; inspect build/main.log.' }
Copy-Item -LiteralPath (Join-Path $buildPath 'main.pdf') -Destination (Join-Path $reportPath 'Report.pdf') -Force
Write-Output (Join-Path $reportPath 'Report.pdf')
