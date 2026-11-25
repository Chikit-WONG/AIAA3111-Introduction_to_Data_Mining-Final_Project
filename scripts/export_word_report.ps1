param(
    [Parameter(Mandatory)][string]$Document,
    [Parameter(Mandatory)][string]$Pdf
)
$ErrorActionPreference = 'Stop'
$source = (Resolve-Path -LiteralPath $Document).Path
$destination = [IO.Path]::GetFullPath($Pdf)
if ([IO.Path]::GetExtension($source) -ne '.docx' -or [IO.Path]::GetExtension($destination) -ne '.pdf') {
    throw 'Expected a Word .docx input and a .pdf output.'
}
$directory = (Get-Item -LiteralPath (Split-Path -Parent $destination)).FullName
$temporary = Join-Path $directory (([guid]::NewGuid().ToString()) + '.pdf')
$word = $null
$documentObject = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3
    $documentObject = $word.Documents.Open($source, $false, $true, $false)
    $documentObject.Repaginate()
    # Print-optimized PDF with heading bookmarks, document tags and embedded fonts.
    $documentObject.ExportAsFixedFormat($temporary, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false)
    if ((Get-Item -LiteralPath $temporary).Length -eq 0) { throw 'Word exported an empty file.' }
    Move-Item -LiteralPath $temporary -Destination $destination -Force
    Write-Output $destination
} finally {
    if ($documentObject) {
        $documentObject.Close(0)
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($documentObject)
    }
    if ($word) {
        $word.Quit()
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
    }
    if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary }
}
