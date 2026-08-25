# Invention Evaluation Framework - one-click setup (Windows / PowerShell)
# Installs Python dependencies, detects installed coding agents,
# installs the run-invention-evaluation skill into each one,
# creates .env from template, and runs a smoke test.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File setup.ps1
#   powershell -File setup.ps1 -SkipDeps
#   powershell -File setup.ps1 -Agents claude,opencode

param(
    [switch]$SkipDeps,
    [string]$Agents = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillSrc = Join-Path $ScriptDir "skills\skill-00-run-evaluation\SKILL.md"
$SkillName = "run-invention-evaluation"

function Banner($msg) { Write-Host ""; Write-Host "== $msg ==" }

# ---------------------------------------------------------------------------
Banner "Preflight"

$python = $null
foreach ($candidate in @("python", "python3", "py")) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) {
        $python = $candidate
        break
    }
}
if (-not $python) {
    Write-Host "ERROR: Python not found. Install Python 3.10+ first:"
    Write-Host "  https://www.python.org/downloads/"
    exit 1
}

$pyVersion = & $python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$pyOk = & $python -c "import sys; print(1 if sys.version_info >= (3,10) else 0)"
Write-Host "  python ($python): $pyVersion"
if ("$pyOk".Trim() -ne "1") {
    Write-Host "ERROR: Python 3.10+ required, found $pyVersion."
    exit 1
}

if (-not (Test-Path $SkillSrc)) {
    Write-Host "ERROR: skill source not found: $SkillSrc"
    exit 1
}

# ---------------------------------------------------------------------------
Banner "Detecting coding agents"

$agentDirs = [ordered]@{
    "claude"       = Join-Path $HOME ".claude\skills"
    "opencode"     = Join-Path $HOME ".config\opencode\skills"
    "opencode-alt" = Join-Path $HOME ".opencode\skills"
    "agents"       = Join-Path $HOME ".agents\skills"
}

$detected = @()
foreach ($name in $agentDirs.Keys) {
    if (Test-Path $agentDirs[$name]) {
        $detected += @{ name = $name; dir = $agentDirs[$name] }
        Write-Host "  [FOUND] $($name) -> $($agentDirs[$name])"
    }
}

if ($Agents -ne "") {
    $detected = @()
    foreach ($w in ($Agents -split ",")) {
        $key = $w.Trim().ToLower()
        switch ($key) {
            "claude"   { $detected += @{ name = "claude"; dir = $agentDirs["claude"] } }
            "opencode" {
                $detected += @{ name = "opencode"; dir = $agentDirs["opencode"] }
                if (Test-Path $agentDirs["opencode-alt"]) {
                    $detected += @{ name = "opencode-alt"; dir = $agentDirs["opencode-alt"] }
                }
            }
            "agents"   { $detected += @{ name = "agents"; dir = $agentDirs["agents"] } }
            default    { Write-Host "Unknown agent '$w' (supported: claude, opencode, agents)"; exit 1 }
        }
    }
}

if ($detected.Count -eq 0) {
    Write-Host ""
    Write-Host "No coding-agent skill directories found."
    Write-Host "Supported agents: Claude Code (~/.claude), OpenCode (~/.config/opencode or ~/.opencode)"
    Write-Host ""
    Write-Host "The framework still works standalone:"
    Write-Host "  cd $ScriptDir; python run.py C:\path\to\invention-folder"
}

# ---------------------------------------------------------------------------
if (-not $SkipDeps) {
    Banner "Installing Python dependencies"
    & $python -m pip install -r (Join-Path $ScriptDir "requirements.txt") --quiet --disable-pip-version-check
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] dependencies installed from requirements.txt"
    } else {
        Write-Host "  [WARN] pip install failed - trying with --user"
        & $python -m pip install --user -r (Join-Path $ScriptDir "requirements.txt") --quiet --disable-pip-version-check
    }
} else {
    Banner "Skipping dependency installation (-SkipDeps)"
}

$missing = @()
foreach ($mod in @("pdfplumber", "yaml", "jsonschema", "PIL", "docx")) {
    & $python -c "import $mod" 2>$null
    if ($LASTEXITCODE -ne 0) { $missing += $mod }
}
if ($missing.Count -gt 0) {
    Write-Host "  [WARN] missing modules: $($missing -join ' ')"
    Write-Host "         re-run this script or: python -m pip install --user -r requirements.txt"
} else {
    Write-Host "  [OK] all runtime modules importable"
}

# ---------------------------------------------------------------------------
Banner "Installing skill: $SkillName"

$installedTo = @()
foreach ($entry in $detected) {
    $targetDir = Join-Path $entry.dir $SkillName
    New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
    $content = Get-Content $SkillSrc -Raw
    $content = $content.Replace("{{FRAMEWORK_ROOT}}", $ScriptDir.Replace("\", "/"))
    Set-Content -Path (Join-Path $targetDir "SKILL.md") -Value $content -Encoding UTF8
    $installedTo += $targetDir
    Write-Host "  [OK] $($entry.name) -> $targetDir\SKILL.md"
}

# ---------------------------------------------------------------------------
Banner "Environment configuration"

$envPath = Join-Path $ScriptDir ".env"
$envExample = Join-Path $ScriptDir ".env.example"
if (Test-Path $envPath) {
    Write-Host "  [OK] .env already exists (left untouched)"
} elseif (Test-Path $envExample) {
    Copy-Item $envExample $envPath
    Write-Host "  [OK] created .env from .env.example"
    Write-Host "       add EPO OPS credentials later for live patent search:"
    Write-Host "       https://developers.epo.org"
} else {
    Write-Host "  [WARN] no .env.example found - skipping (framework runs without live APIs)"
}

# ---------------------------------------------------------------------------
Banner "Smoke test"

& $python (Join-Path $ScriptDir "run.py") --help *> $null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] run.py loads and shows help"
} else {
    Write-Host "  [FAIL] run.py --help errored"
}

$smokeFail = $false
foreach ($t in $installedTo) {
    $installedContent = Get-Content (Join-Path $t "SKILL.md") -Raw
    if ($installedContent -like "*{{FRAMEWORK_ROOT}}*") {
        Write-Host "  [WARN] path substitution incomplete in $t\SKILL.md"
        $smokeFail = $true
    }
}

# ---------------------------------------------------------------------------
Banner "Setup complete"

Write-Host ""
Write-Host "  Framework root : $ScriptDir"
Write-Host "  Skill installed: $($installedTo.Count) agent(s)"
Write-Host ""
if ($installedTo.Count -gt 0) {
    Write-Host '  NEXT: restart your coding agent, then say:'
    Write-Host '        "evaluate this invention folder: C:\path\to\folder"'
    Write-Host ""
}
Write-Host "  Or run directly without any agent:"
Write-Host "    cd $ScriptDir; python run.py C:\path\to\invention-folder"
Write-Host ""

if ($smokeFail) {
    Write-Host "  Setup finished WITH WARNINGS - review [WARN]/[FAIL] lines above."
    exit 1
}
exit 0
