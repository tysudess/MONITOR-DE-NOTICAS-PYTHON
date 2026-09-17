$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$Portable = 'MONITOR-DE-NOTICIAS-PYTHON-portable-windows-x64.zip'
$PrevAssetId = '566855563'
$PrevHash = '607c85cc48ec9722aaee0b65acd1a6188364833b1f26a868f58a7199e78162f8'
$FfmpegHash = '91678b935eb52cc740249474574b6042768b744c622347f28a1b487e1ed29915'
$FfprobeHash = 'c42ada47df746e3788e2ba3ed2f7af07662a58f9088f9894e1b14d3d5c432263'

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

$env:QT_QPA_PLATFORM = 'offscreen'
$env:MONITOR_DISABLE_WEATHER = '1'
$env:MONITOR_DISABLE_EXTERNAL_INTEGRATIONS = '1'
python -m compileall -q src tests scripts run.py
if ($LASTEXITCODE -ne 0) { throw 'Compilacao Python falhou' }
python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'Testes de regressao falharam' }

$env:QT_QPA_PLATFORM = 'windows'
python scripts/capture_home_layout.py
if ($LASTEXITCODE -ne 0) { throw 'Gate visual/sidebar v0.0.19 falhou' }

Remove-Item Env:MONITOR_DISABLE_EXTERNAL_INTEGRATIONS -ErrorAction SilentlyContinue
./scripts/build_external_integrations.ps1
if ($LASTEXITCODE -ne 0) { throw 'Build das integracoes externas falhou' }

$previousDir = Join-Path $env:RUNNER_TEMP 'v019-sidebar-fix-previous'
if (Test-Path $previousDir) { Remove-Item $previousDir -Recurse -Force }
New-Item -ItemType Directory -Force $previousDir | Out-Null
$previousZip = Join-Path $previousDir $Portable
$assetUrl = "https://api.github.com/repos/tysudess/MONITOR-DE-NOTICAS-PYTHON/releases/assets/$PrevAssetId"
& curl.exe --fail --location --silent --show-error -H "Authorization: Bearer $env:GH_TOKEN" -H 'Accept: application/octet-stream' -H 'X-GitHub-Api-Version: 2022-11-28' $assetUrl -o $previousZip
if ($LASTEXITCODE -ne 0) { throw 'Download do portable base v0.0.18 falhou' }
if ((Get-FileHash $previousZip -Algorithm SHA256).Hash.ToLowerInvariant() -ne $PrevHash) { throw 'Hash do portable base v0.0.18 divergente' }

$extract = Join-Path $env:RUNNER_TEMP 'v019-sidebar-fix-source'
if (Test-Path $extract) { Remove-Item $extract -Recurse -Force }
Expand-Archive $previousZip $extract -Force
$root = Get-ChildItem $extract -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'MonitorDeNoticias.exe') } | Select-Object -First 1
if (-not $root) { throw 'Raiz do portable base nao encontrada' }

$ff = Join-Path $root.FullName 'bin/ffmpeg.exe'
$fp = Join-Path $root.FullName 'bin/ffprobe.exe'
if ((Get-FileHash $ff -Algorithm SHA256).Hash.ToLowerInvariant() -ne $FfmpegHash) { throw 'FFmpeg divergente' }
if ((Get-FileHash $fp -Algorithm SHA256).Hash.ToLowerInvariant() -ne $FfprobeHash) { throw 'FFprobe divergente' }

$audit = Join-Path $env:RUNNER_TEMP 'v019-sidebar-fix-ffmpeg'
if (Test-Path $audit) { Remove-Item $audit -Recurse -Force }
New-Item -ItemType Directory -Force $audit | Out-Null
Copy-Item $ff (Join-Path $audit 'ffmpeg.exe') -Force
Copy-Item $fp (Join-Path $audit 'ffprobe.exe') -Force
$env:MONITOR_VALIDATED_FFMPEG_DIR = $audit

$out = Join-Path $env:RUNNER_TEMP 'v019-sidebar-fix-portable'
if (Test-Path $out) { Remove-Item $out -Recurse -Force }
./scripts/build_portable.ps1 -OutputDir $out
if ($LASTEXITCODE -ne 0) { throw 'Build portable falhou' }

$zip = Join-Path $out $Portable
if (-not (Test-Path $zip)) { throw 'ZIP portable nao foi gerado' }
./scripts/validate_portable.ps1 -ZipPath $zip
if ($LASTEXITCODE -ne 0) { throw 'Validacao final do portable falhou' }

$publish = Join-Path $PWD 'portable-test-artifact'
if (Test-Path $publish) { Remove-Item $publish -Recurse -Force }
New-Item -ItemType Directory -Force $publish | Out-Null
Copy-Item $zip (Join-Path $publish 'MONITOR-DE-NOTICIAS-PYTHON-v0.0.19-sidebar-fix-portable-windows-x64.zip') -Force
$hash = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLowerInvariant()
"$hash  MONITOR-DE-NOTICIAS-PYTHON-v0.0.19-sidebar-fix-portable-windows-x64.zip" | Set-Content (Join-Path $publish 'SHA256SUMS.txt') -Encoding ascii
Write-Host "PORTABLE_TEST_OK"
Write-Host "PORTABLE_SHA256=$hash"
