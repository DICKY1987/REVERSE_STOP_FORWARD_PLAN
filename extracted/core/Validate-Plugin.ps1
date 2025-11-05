param(
    [Parameter(Mandatory=$true)]
    [string]$PluginPath
)

$ErrorActionPreference = "Stop"
$validationPassed = $true

Write-Host "`n=== Validating Plugin: $PluginPath ===" -ForegroundColor Cyan

# 1. Check plugin.spec.json exists and is valid
Write-Host "`nChecking plugin.spec.json..." -ForegroundColor Yellow
if (-not (Test-Path "$PluginPath/plugin.spec.json")) {
    Write-Host "✗ plugin.spec.json not found" -ForegroundColor Red
    $validationPassed = $false
} else {
    try {
        $spec = Get-Content "$PluginPath/plugin.spec.json" | ConvertFrom-Json
        Write-Host "✓ plugin.spec.json valid" -ForegroundColor Green
    } catch {
        Write-Host "✗ plugin.spec.json invalid JSON" -ForegroundColor Red
        $validationPassed = $false
    }
}

# 2. Check required artifacts exist
Write-Host "`nChecking required artifacts..." -ForegroundColor Yellow
$requiredFiles = @(
    "manifest.json",
    "policy_snapshot.json",
    "ledger_contract.json",
    "README_PLUGIN.md",
    "healthcheck.md",
    "$($spec.entry_point)",
    "tests/test_$($spec.plugin_name).py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path "$PluginPath/$file") {
        Write-Host "✓ $file exists" -ForegroundColor Green
    } else {
        Write-Host "✗ $file missing" -ForegroundColor Red
        $validationPassed = $false
    }
}

# 3. Validate input/output schemas
Write-Host "`nValidating schemas..." -ForegroundColor Yellow
if ($spec.input_schema -and $spec.output_schema) {
    # Check that trace_id is in input schema
    if ($spec.input_schema.required -contains "trace_id") {
        Write-Host "✓ Input schema includes trace_id" -ForegroundColor Green
    } else {
        Write-Host "✗ Input schema missing trace_id" -ForegroundColor Red
        $validationPassed = $false
    }
    # Check that output schema includes required fields
    $requiredOutputFields = @("status", "trace_id")
    foreach ($field in $requiredOutputFields) {
        if ($spec.output_schema.required -contains $field) {
            Write-Host "✓ Output schema includes $field" -ForegroundColor Green
        } else {
            Write-Host "✗ Output schema missing $field" -ForegroundColor Red
            $validationPassed = $false
        }
    }
} else {
    Write-Host "✗ Schemas not defined" -ForegroundColor Red
    $validationPassed = $false
}

# 4. Run tests
Write-Host "`nRunning tests..." -ForegroundColor Yellow
if ($spec.language -eq "python") {
    try {
        $null = pytest "$PluginPath/tests/" -v --tb=short 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ All tests passed" -ForegroundColor Green
        } else {
            Write-Host "✗ Tests failed" -ForegroundColor Red
            Write-Host $testResult
            $validationPassed = $false
        }
    } catch {
        Write-Host "✗ Failed to run tests: $_" -ForegroundColor Red
        $validationPassed = $false
    }
}

# 5. Check code coverage
Write-Host "`nChecking code coverage..." -ForegroundColor Yellow
$coverageResult = pytest "$PluginPath/tests/" --cov="$PluginPath" --cov-report=term-missing 2>&1
if ($coverageResult -match "(\d+)%") {
    $coverage = [int]$matches[1]
    if ($coverage -ge 80) {
        Write-Host "✓ Code coverage: $coverage% (>= 80%)" -ForegroundColor Green
    } else {
        Write-Host "✗ Code coverage: $coverage% (< 80%)" -ForegroundColor Red
        $validationPassed = $false
    }
}

# 6. Run linters
Write-Host "`nRunning linters..." -ForegroundColor Yellow
if ($spec.language -eq "python") {
    # Ruff
    $ruffResult = ruff check "$PluginPath/" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Ruff passed" -ForegroundColor Green
    } else {
        Write-Host "✗ Ruff found issues" -ForegroundColor Red
        Write-Host $ruffResult
        $validationPassed = $false
    }
    # MyPy
    $mypyResult = mypy "$PluginPath/$($spec.entry_point)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ MyPy passed" -ForegroundColor Green
    } else {
        Write-Host "✗ MyPy found issues" -ForegroundColor Red
        Write-Host $mypyResult
        $validationPassed = $false
    }
}

# Final result
Write-Host "`n=== Validation Result ===" -ForegroundColor Cyan
if ($validationPassed) {
    Write-Host "✓ VALIDATION PASSED" -ForegroundColor Green
    Write-Host "Plugin is ready for deployment" -ForegroundColor Green
    exit 0
} else {
    Write-Host "✗ VALIDATION FAILED" -ForegroundColor Red
    Write-Host "Fix the issues above before deploying" -ForegroundColor Red
    exit 1
}