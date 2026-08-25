<#
Invention Evaluation Framework — market-only report regeneration, Run 4
GenIP research-team specification. PowerShell-native only.

Usage:
  powershell -ExecutionPolicy Bypass -File run-regeneration.ps1 `
      -Root "C:\Users\nicho\Documents\invention-evaluation-framework-main\invention-evaluation-framework-main"
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$Root
)

$ErrorActionPreference = "Stop"
Set-Location $Root

Write-Host "== Locate prior deliverable (preserved, never overwritten) =="
$priorDocx = Get-ChildItem -Path $Root -Recurse -Filter "market-evaluation-8530-v17.docx" |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($null -eq $priorDocx) {
    Write-Warning "Prior market-evaluation-8530-v17.docx not found under $Root - continuing; generator will still require the Technology Overview markdown."
} else {
    Write-Host ("  Found: " + $priorDocx.FullName)
}

Write-Host "== Create new run directory (prior runs untouched) =="
$runDir = Join-Path $Root "evaluations\8530-market-only-run4"
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
Write-Host ("  Run dir: " + $runDir)

Write-Host "== Verify source files exist read-only (never modified) =="
$sourceDir = Join-Path $Root "8530"
foreach ($name in @("-8530 disclosure.pdf", "-8530 attachment.pdf", "sample.docx")) {
    $p = Join-Path $sourceDir $name
    if (-not (Test-Path -LiteralPath $p)) {
        throw "ESSENTIAL SOURCE MISSING: $p"
    }
    $hash = Get-FileHash -LiteralPath $p -Algorithm SHA256
    Write-Host ("  OK: " + $name + "  sha256=" + $hash.Hash.Substring(0, 16) + "... (recorded in manifest)")
}

Write-Host "== Locate prior Technology Overview markdown (essential input) =="
$techMd = Get-ChildItem -Path (Join-Path $Root "evaluations") -Recurse -Filter "*.md" -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match "8530" } |
    Where-Object { (Get-Content -LiteralPath $_.FullName -Raw) -match "(?s)#\s*Technology Overview.{400,}" } |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
$genArgs = @()
if ($null -ne $techMd) {
    Write-Host ("  Using: " + $techMd.FullName)
    $genArgs += "--prior-tech-overview"
    $genArgs += $techMd.FullName
}

Write-Host "== Generate revised report =="
$py = (Get-Command py -ErrorAction SilentlyContinue)
$pythonCmd = if ($null -ne $py) { "py" } else { "python" }
& $pythonCmd (Join-Path $Root "market-report-generator\generate_market_report.py") `
    --config-dir (Join-Path $Root "market-report-generator\content") `
    --out $runDir `
    --sources-dir $sourceDir `
    @genArgs
if ($LASTEXITCODE -ne 0) {
    throw "Generation failed with exit code $LASTEXITCODE"
}

Write-Host "== Copy ledger + QA checklist into run dir =="
Copy-Item -LiteralPath (Join-Path $Root "market-report-generator\execution-ledger-8530-market-only-run4.md") -Destination $runDir -Force
Copy-Item -LiteralPath (Join-Path $Root "market-report-generator\visual-qa-checklist-8530-run4.md") -Destination $runDir -Force

Write-Host "== Finalize in Word (fields + TOC + PDF export), if Word available =="
& powershell -ExecutionPolicy Bypass -File (Join-Path $Root "market-report-generator\finalize-word-fields.ps1") `
    -RunDir $runDir

Write-Host ""
Write-Host "RUN 4 COMPLETE. Outputs in:" 
Write-Host ("  " + $runDir)
Write-Host "Visual QA: open visual-qa-checklist-8530-run4.md and inspect every rendered page."
