
function up { docker compose up -d }
function down { docker compose down --remove-orphans }
function rebuild([string]$svc) { if ($svc) { docker compose build --no-cache $svc } else { docker compose build --no-cache } }
function logs([string]$svc) { if ($svc) { docker compose logs -f $svc } else { docker compose logs -f } }
function sh([string]$svc) { if (-not $svc) { $svc = 'api' } ; docker compose exec $svc sh }
function runsh([string]$svc) { if (-not $svc) { $svc = 'api' } ; docker compose run --rm $svc sh }
function restart([string]$svc) { if ($svc) { docker compose restart $svc } else { docker compose restart } }
function ps { docker compose ps }
Write-Host "Loaded: up, down, rebuild <svc>, logs [svc], sh [svc], runsh [svc], restart [svc], ps" -ForegroundColor Green
