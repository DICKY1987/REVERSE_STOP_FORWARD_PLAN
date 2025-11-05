function Get-DocSemVer {
  param([string]$Path)
  $content = Get-Content -Raw -LiteralPath $Path
  if ($content -match '---\s*(.*?)---'s) {
    $yaml = $Matches[1]
    if ($yaml -match '(?m)^\s*semver:\s*([0-9]+\.[0-9]+\.[0-9]+)') {
      return $Matches[1]
    }
  }
  return $null
}

function Get-ActivePolicyVersions {
  return @{
    OC_CORE = Get-DocSemVer "docs/standards/OC_CORE.md"
    PIPELINE_POLICY = Get-DocSemVer "docs/standards/PIPELINE_POLICY.md"
    R_PIPELINE_PHASE_01 = Get-DocSemVer "plans/R_PIPELINE/PHASE_01_EXECUTION_CONTRACT.md"
  }
}

# Usage example: record versions into a ledger for a pipeline run
$runLedger = @{
  run_id = "2025-10-28T14-22-07Z_ULID01Q3..."
  repo_commit = (git rev-parse HEAD)
  policy_versions = Get-ActivePolicyVersions
  timestamp = Get-Date -Format "o"
}

$runLedger | ConvertTo-Json | Out-File "ledger/$($runLedger.run_id).json"