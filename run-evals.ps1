# run-evals.ps1 — run promptfoo evals on Windows
# Uses full nodejs path to bypass pi-node PATH hijack.
# Usage:
#   .\run-evals.ps1              # run all 12 evals
#   .\run-evals.ps1 --filter-first-n 1   # run first eval only
#   .\run-evals.ps1 --verbose    # show model output inline

$npx = "C:\Program Files\nodejs\npx.cmd"
$config = "evals/promptfoo/promptfooconfig.yaml"
$output = "evals/promptfoo/output.json"

& $npx promptfoo eval -c $config -o $output --no-cache --no-share @args

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nEval run failed (exit $LASTEXITCODE). Check output above." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`nDone. View results: & '$npx' promptfoo view" -ForegroundColor Green
