param(
    [int]$Count = 1,
    [switch]$Push,
    [int]$Category = 0
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$argsList = @("-m", "src.main", "-n", "$Count")
if ($Category -gt 0) {
    $argsList += @("--category", "$Category")
}
if ($Push) {
    $argsList += "--push"
}

Write-Host "Running: python $($argsList -join ' ')" -ForegroundColor Cyan
python @argsList
