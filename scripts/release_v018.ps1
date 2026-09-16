$ErrorActionPreference='Stop'
$Tag='v0.0.18'
$Portable='MONITOR-DE-NOTICIAS-PYTHON-portable-windows-x64.zip'
$PrevTag='v0.0.17'
$PrevHash='cecff350020b58e68118fb676e27a55a8c07d1f122335876a80f8f4e1fc3d85b'
$FfmpegHash='91678b935eb52cc740249474574b6042768b744c622347f28a1b487e1ed29915'
$FfprobeHash='c42ada47df746e3788e2ba3ed2f7af07662a58f9088f9894e1b14d3d5c432263'

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
$env:QT_QPA_PLATFORM='offscreen'
$env:MONITOR_DISABLE_WEATHER='1'
$env:MONITOR_DISABLE_EXTERNAL_INTEGRATIONS='1'
python -m compileall -q src tests scripts run.py
python -m pytest -q
python scripts/capture_home_layout.py

$run=Get-Content run.py -Raw
if($run -notmatch 'install_v017_home_truth\(\)'){throw 'Base funcional/visual v0.0.17 da Home ausente'}
if($run -notmatch 'install_v017_home_truth_precision\(\)'){throw 'Precisao visual v0.0.17 da Home ausente'}
if($run -notmatch 'install_v018_home_visual_fidelity\(\)'){throw 'Refino visual v0.0.18 da Home ausente'}
if($run -notmatch 'install_v016_layout_only\(\)'){throw 'Base visual v0.0.16 ausente'}
$target=(git rev-parse HEAD).Trim()

Remove-Item Env:MONITOR_DISABLE_EXTERNAL_INTEGRATIONS -ErrorAction SilentlyContinue
./scripts/build_external_integrations.ps1
$m=Get-Content 'resources/integrations/manifest.json' -Raw | ConvertFrom-Json
if($m.extratorNoticias.commit -ne 'ea43bb344d74dc2a32cc1d733aaabea54d763150'){throw 'Extrator de Noticias divergente'}
if($m.automacaoPlanilhas.commit -ne '51bd5386ea280edc2d56c6567be0113cfd84d2e5'){throw 'Automacao Planilhas divergente'}
if($m.capas.commit -ne '87705432008b00f114d27d1f1645c2c89e649365'){throw 'Capas divergente'}
if($m.videoEditor.commit -ne '92f031c22cf8c23c2f5dd15a1857a6df4186b97e'){throw 'Editor de Video divergente'}

if(Test-Path previous){Remove-Item previous -Recurse -Force}
New-Item -ItemType Directory previous | Out-Null
gh release download $PrevTag -p $Portable -D previous
$zip=Get-ChildItem previous -Recurse -Filter $Portable | Select-Object -First 1
if(-not $zip){throw 'Portable validado v0.0.17 ausente'}
if((Get-FileHash $zip.FullName -Algorithm SHA256).Hash.ToLowerInvariant() -ne $PrevHash){throw 'Hash do portable v0.0.17 divergente'}
$extract=Join-Path $env:RUNNER_TEMP 'v017-source-v018'
if(Test-Path $extract){Remove-Item $extract -Recurse -Force}
Expand-Archive $zip.FullName $extract -Force
$root=Get-ChildItem $extract -Directory | Where-Object {Test-Path (Join-Path $_.FullName 'MonitorDeNoticias.exe')} | Select-Object -First 1
if(-not $root){throw 'Raiz do portable v0.0.17 ausente'}
$ff=Join-Path $root.FullName 'bin/ffmpeg.exe'
$fp=Join-Path $root.FullName 'bin/ffprobe.exe'
if((Get-FileHash $ff -Algorithm SHA256).Hash.ToLowerInvariant() -ne $FfmpegHash){throw 'FFmpeg divergente'}
if((Get-FileHash $fp -Algorithm SHA256).Hash.ToLowerInvariant() -ne $FfprobeHash){throw 'FFprobe divergente'}
$audit=Join-Path $env:RUNNER_TEMP 'ffmpeg-v018'
New-Item -ItemType Directory -Force $audit | Out-Null
Copy-Item $ff (Join-Path $audit 'ffmpeg.exe') -Force
Copy-Item $fp (Join-Path $audit 'ffprobe.exe') -Force
$env:MONITOR_VALIDATED_FFMPEG_DIR=$audit

./scripts/build_portable.ps1
$newZip=(Resolve-Path "portable-out/$Portable").Path
./scripts/validate_portable.ps1 -ZipPath $newZip

if(Test-Path publish){Remove-Item publish -Recurse -Force}
New-Item -ItemType Directory publish | Out-Null
Copy-Item $newZip "publish/$Portable"
$hash=(Get-FileHash $newZip -Algorithm SHA256).Hash.ToLowerInvariant()
"$hash  $Portable" | Set-Content publish/SHA256SUMS.txt -Encoding ascii
Copy-Item portable/FFMPEG_SOURCE_INFO.txt publish/FFMPEG_SOURCE_INFO.txt
Copy-Item resources/integrations/manifest.json publish/INTEGRATIONS-MANIFEST.json
Copy-Item artifacts/home-reference-1672x941.png publish/HOME-v0.0.18.png

if(gh release view $Tag 2>$null){throw "$Tag ja existe"}
$notes=@"
Monitor de Noticias Python 0.0.18 — Windows Portable x64

- refino visual minucioso da tela Inicio conforme as imagens-verdade enviadas
- cores, luzes, contraste, neon e profundidade reforcados para aproximar a vivacidade da referencia
- globo do hero redesenhado com halo, rede, pontos luminosos e maior intensidade azul/ciano
- sidebar refinada com fundo mais profundo, item ativo mais luminoso e contraste mais fiel
- topbar refinada com busca, status, relogio e notificacao mais vivos
- cards e paineis da Home ganharam bordas e brilho locais sem trocar widgets funcionais
- alteracao restrita a camada visual; controller, rotas, callbacks, banco, coletores e regras de negocio preservados
- Extrator de Noticias, Automacao Planilhas, Capas, Editor de Video, Editor PDF e demais modulos preservados
- FFmpeg e FFprobe preservados pelos hashes validados da versao anterior
- regressao completa, captura 1672x941, build e smoke do portable executados antes da publicacao

SHA-256 do portable: $hash
"@

gh release create $Tag "publish/$Portable" publish/SHA256SUMS.txt publish/FFMPEG_SOURCE_INFO.txt publish/INTEGRATIONS-MANIFEST.json publish/HOME-v0.0.18.png --target $target --title 'Monitor de Noticias Python 0.0.18' --notes $notes
Write-Host "RELEASE_CREATED=$Tag"
Write-Host "RELEASE_SHA256=$hash"
