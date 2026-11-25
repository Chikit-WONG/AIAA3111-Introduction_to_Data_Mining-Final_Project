param([string]$ReportDirectory = '', [switch]$Overleaf, [switch]$Offline)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
if (-not $ReportDirectory) {
    $ReportDirectory = Join-Path (Split-Path -Parent $projectRoot) ((Split-Path -Leaf $projectRoot) + '-Report')
}
$reportPath = (Resolve-Path -LiteralPath $ReportDirectory).Path
if (-not ($Overleaf -or $Offline)) {
    & (Join-Path $PSScriptRoot 'export_word_report.ps1') -Document (Join-Path $reportPath 'Report.docx') -Pdf (Join-Path $reportPath 'Report.pdf')
    return
}
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
Write-Output (Join-Path $buildPath 'main.pdf')
