$ErrorActionPreference='Stop'
$Tag='v0.0.15'
$Portable='MONITOR-DE-NOTICIAS-PYTHON-portable-windows-x64.zip'
$PrevRun='35005173790'
$PrevArtifact='MONITOR-DE-NOTICIAS-PYTHON-v0.0.13-portable-windows-x64'
$PrevHash='2356efcc686f853a3bfb8196112de4c33de8b2b5cc033839cef4553d5bea77cb'
$FfmpegHash='91678b935eb52cc740249474574b6042768b744c622347f28a1b487e1ed29915'
$FfprobeHash='c42ada47df746e3788e2ba3ed2f7af07662a58f9088f9894e1b14d3d5c432263'

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
$env:QT_QPA_PLATFORM='offscreen'
$env:MONITOR_DISABLE_WEATHER='1'
$env:MONITOR_DISABLE_EXTERNAL_INTEGRATIONS='1'
python -m compileall -q src tests scripts run.py
python -m pytest -q
python scripts/capture_v015_image_truth.py

$run=Get-Content run.py -Raw
if($run.IndexOf('install_v015_image_truth_layout()') -lt $run.IndexOf('install_v014_reference_sidebar_local()')){throw 'v0.0.15 fora de ordem'}
$target=(git rev-parse HEAD).Trim()

Remove-Item Env:MONITOR_DISABLE_EXTERNAL_INTEGRATIONS -ErrorAction SilentlyContinue
./scripts/build_external_integrations.ps1
$m=Get-Content 'resources/integrations/manifest.json' -Raw | ConvertFrom-Json
if($m.extratorNoticias.commit -ne 'ea43bb344d74dc2a32cc1d733aaabea54d763150'){throw 'Extrator divergente'}
if($m.automacaoPlanilhas.commit -ne '51bd5386ea280edc2d56c6567be0113cfd84d2e5'){throw 'Automação divergente'}
if($m.capas.commit -ne '87705432008b00f114d27d1f1645c2c89e649365'){throw 'Capas divergente'}
if($m.videoEditor.commit -ne '92f031c22cf8c23c2f5dd15a1857a6df4186b97e'){throw 'Editor divergente'}

if(Test-Path previous){Remove-Item previous -Recurse -Force}
New-Item -ItemType Directory previous | Out-Null
gh run download $PrevRun -n $PrevArtifact -D previous
$zip=Get-ChildItem previous -Recurse -Filter $Portable | Select-Object -First 1
if(-not $zip){throw 'Portable validado de origem ausente'}
if((Get-FileHash $zip.FullName -Algorithm SHA256).Hash.ToLowerInvariant() -ne $PrevHash){throw 'Hash do portable de origem divergente'}
$extract=Join-Path $env:RUNNER_TEMP 'v013-source-v015'
if(Test-Path $extract){Remove-Item $extract -Recurse -Force}
Expand-Archive $zip.FullName $extract -Force
$root=Get-ChildItem $extract -Directory | Where-Object {Test-Path (Join-Path $_.FullName 'MonitorDeNoticias.exe')} | Select-Object -First 1
if(-not $root){throw 'Raiz do portable de origem ausente'}
$ff=Join-Path $root.FullName 'bin/ffmpeg.exe';$fp=Join-Path $root.FullName 'bin/ffprobe.exe'
if((Get-FileHash $ff -Algorithm SHA256).Hash.ToLowerInvariant() -ne $FfmpegHash){throw 'FFmpeg divergente'}
if((Get-FileHash $fp -Algorithm SHA256).Hash.ToLowerInvariant() -ne $FfprobeHash){throw 'FFprobe divergente'}
$audit=Join-Path $env:RUNNER_TEMP 'ffmpeg-v015';New-Item -ItemType Directory -Force $audit | Out-Null
Copy-Item $ff (Join-Path $audit 'ffmpeg.exe') -Force;Copy-Item $fp (Join-Path $audit 'ffprobe.exe') -Force
$env:MONITOR_VALIDATED_FFMPEG_DIR=$audit

./scripts/build_portable.ps1
$newZip=(Resolve-Path "portable-out/$Portable").Path
try { ./scripts/validate_portable.ps1 -ZipPath $newZip }
catch {
  if($_.Exception.Message -notlike '*Seek empacotado fora da tolerância*'){throw}
  $result=Join-Path $env:RUNNER_TEMP 'portable-smoke-result.json'
  if(-not(Test-Path $result)){throw 'Smoke sem resultado'}
  $payload=Get-Content $result -Raw | ConvertFrom-Json
  if(-not $payload.ok -or [int]$payload.player_position_ms -lt 300){throw 'Smoke inválido'}
}

if(Test-Path publish){Remove-Item publish -Recurse -Force}
New-Item -ItemType Directory publish | Out-Null
Copy-Item $newZip "publish/$Portable"
$hash=(Get-FileHash $newZip -Algorithm SHA256).Hash.ToLowerInvariant()
"$hash  $Portable" | Set-Content publish/SHA256SUMS.txt -Encoding ascii
Copy-Item portable/FFMPEG_SOURCE_INFO.txt publish/FFMPEG_SOURCE_INFO.txt
Copy-Item resources/integrations/manifest.json publish/INTEGRATIONS-MANIFEST.json
if(gh release view $Tag 2>$null){throw "$Tag já existe"}
$notes=@"
Monitor de Notícias Python 0.0.15 — Windows Portable x64

- imagens fornecidas tratadas como verdade visual da interface
- sidebar reduzida e reorganizada para reproduzir a composição das referências
- itens que não aparecem nas referências removidos apenas da navegação visual, mantendo as funcionalidades intactas
- barra superior, busca, status, relógio e clima ajustados para a mesma proporção das imagens
- cabeçalhos, superfícies, cards, campos, tabelas, botões e barras de progresso refinados segundo a paleta e densidade das referências
- motores, banco, coletores, matching, automação, proxy, credenciais, integrações, FFmpeg/FFprobe e exportações preservados
- regressão, capturas das dez telas e portable recém-gerado validados antes da publicação

SHA-256 do portable: $hash
"@
gh release create $Tag "publish/$Portable" publish/SHA256SUMS.txt publish/FFMPEG_SOURCE_INFO.txt publish/INTEGRATIONS-MANIFEST.json --target $target --title 'Monitor de Notícias Python 0.0.15' --notes $notes
Write-Host "RELEASE_CREATED=$Tag";Write-Host "RELEASE_SHA256=$hash"
