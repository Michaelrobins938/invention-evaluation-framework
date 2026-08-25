<#
Word COM finalization: update every field and the Table of Contents,
save the DOCX, export the PDF. Never touches prior runs.

Usage:
  powershell -ExecutionPolicy Bypass -File finalize-word-fields.ps1 -RunDir <dir>
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$RunDir
)

$ErrorActionPreference = "Stop"
$docx = Join-Path $RunDir "market-evaluation-8530-v17-revised.docx"
$pdf  = Join-Path $RunDir "market-evaluation-8530-v17-revised.pdf"

if (-not (Test-Path -LiteralPath $docx)) {
    throw "DOCX not found: $docx"
}

try {
    $word = New-Object -ComObject Word.Application
} catch {
    $msg = "Microsoft Word is unavailable on this machine; DOCX was generated but fields/TOC/PDF were NOT finalized. Open the DOCX in Word, press Ctrl+A then F9 (Update entire table), save, and export PDF manually."
    Write-Warning $msg
    Set-Content -LiteralPath (Join-Path $RunDir "word-finalization-pending.txt") -Value $msg
    exit 0
}

try {
    $word.Visible = $false
    $doc = $word.Documents.Open($docx)

    foreach ($story in $doc.StoryRanges) {
        $range = $story
        while ($null -ne $range) {
            $range.Fields.Update() | Out-Null
            $range = $range.NextStoryRange
        }
    }
    if ($doc.TablesOfContents.Count -gt 0) {
        for ($i = 1; $i -le $doc.TablesOfContents.Count; $i++) {
            $doc.TablesOfContents.Item($i).Update()
        }
    }
    $doc.Save()

    # wdExportFormatPDF = 17
    $doc.ExportAsFixedFormat($pdf, 17)
    $doc.Close($false)
    Write-Host "  Fields updated, TOC rebuilt, saved, PDF exported:"
    Write-Host ("    " + $pdf)
} finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
}
