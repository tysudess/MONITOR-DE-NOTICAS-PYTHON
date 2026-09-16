$ErrorActionPreference='Stop'
$Tag='v0.0.19'
$Portable='MONITOR-DE-NOTICIAS-PYTHON-portable-windows-x64.zip'
$PrevTag='v0.0.18'
$PrevHash='607c85cc48ec9722aaee0b65acd1a6188364833b1f26a868f58a7199e78162f8'
$FfmpegHash='91678b935eb52cc740249474574b6042768b744c622347f28a1b487e1ed29915'
$FfprobeHash='c42ada47df746e3788e2ba3ed2f7af07662a58f9088f9894e1b14d3d5c432263'
$HeroHash='1695b8f24be0846a459ec021a147a0057a15a311a1c8e7474617f52fc52609ec'

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
$env:QT_QPA_PLATFORM='offscreen'
$env:MONITOR_DISABLE_WEATHER='1'
$env:MONITOR_DISABLE_EXTERNAL_INTEGRATIONS='1'
python -m compileall -q src tests scripts run.py
if($LASTEXITCODE -ne 0){throw 'Compilacao Python falhou'}
python -m pytest -q
if($LASTEXITCODE -ne 0){throw 'Regressao falhou'}

# Validação do ativo visual fornecido pelo usuário: não aceitar fallback inventado.
$heroB64='resources/ui/v019/home-hero.webp.b64'
if(-not (Test-Path $heroB64)){throw 'Imagem-verdade do hero v0.0.19 ausente'}
$heroBytes=[Convert]::FromBase64String((Get-Content $heroB64 -Raw).Trim())
$heroTemp=Join-Path $env:RUNNER_TEMP 'home-hero-v019.webp'
[IO.File]::WriteAllBytes($heroTemp,$heroBytes)
$heroSha=(Get-FileHash $heroTemp -Algorithm SHA256).Hash.ToLowerInvariant()
if($heroSha -ne $HeroHash){throw "Imagem-verdade do hero divergente: $heroSha"}
if((Get-Item $heroTemp).Length -ne 73746){throw 'Imagem-verdade do hero com tamanho divergente'}

$env:QT_QPA_PLATFORM='windows'
python scripts/capture_home_layout.py
if($LASTEXITCODE -ne 0){throw 'Gate visual/sidebar v0.0.19 falhou'}

$run=Get-Content run.py -Raw
if($run -notmatch 'install_v017_home_truth\(\)'){throw 'Base funcional da Home ausente'}
if($run -notmatch 'install_v018_home_visual_fidelity\(\)'){throw 'Base visual v0.0.18 ausente'}
if($run -notmatch 'install_v019_exact_reference\(\)'){throw 'Camada exata v0.0.19 ausente'}
if($run -notmatch 'install_v016_layout_only\(\)'){throw 'Base funcional v0.0.16 ausente'}
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
if(-not $zip){throw 'Portable validado v0.0.18 ausente'}
if((Get-FileHash $zip.FullName -Algorithm SHA256).Hash.ToLowerInvariant() -ne $PrevHash){throw 'Hash do portable v0.0.18 divergente'}
$extract=Join-Path $env:RUNNER_TEMP 'v018-source-v019'
if(Test-Path $extract){Remove-Item $extract -Recurse -Force}
Expand-Archive $zip.FullName $extract -Force
$root=Get-ChildItem $extract -Directory | Where-Object {Test-Path (Join-Path $_.FullName 'MonitorDeNoticias.exe')} | Select-Object -First 1
if(-not $root){throw 'Raiz do portable v0.0.18 ausente'}
$ff=Join-Path $root.FullName 'bin/ffmpeg.exe'
$fp=Join-Path $root.FullName 'bin/ffprobe.exe'
if((Get-FileHash $ff -Algorithm SHA256).Hash.ToLowerInvariant() -ne $FfmpegHash){throw 'FFmpeg divergente'}
if((Get-FileHash $fp -Algorithm SHA256).Hash.ToLowerInvariant() -ne $FfprobeHash){throw 'FFprobe divergente'}
$audit=Join-Path $env:RUNNER_TEMP 'ffmpeg-v019'
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
Copy-Item artifacts/home-reference-1672x941.png publish/HOME-v0.0.19.png

if(gh release view $Tag 2>$null){throw "$Tag ja existe"}
$notes=@"
Monitor de Noticias Python 0.0.19 — Windows Portable x64

- Home refeita com a imagem enviada pelo usuario como verdade visual literal
- hero usa diretamente o recorte da imagem-verdade; nao existe globo redesenhado ou aproximado nesta camada
- sidebar fixada em 225 px e mantida com a mesma estrutura/estilo em todas as abas
- troca de aba nao restaura mais sidebar antiga nem muda largura, grupos ou aparencia
- tipografia da Home, sidebar e topbar aumentada para melhorar legibilidade
- nove cards, paineis, dados reais e callbacks da Home continuam sendo widgets funcionais
- todas as 15 secoes/rotas existentes continuam registradas, inclusive Extrator de Noticias e Automacao Planilhas
- controller, banco, coletores, matching, automacao, proxy, credenciais e motores de ferramentas nao foram trocados
- Editor PDF, Extrator de Videos, Editor de Video, Capas e integracoes originais preservados
- FFmpeg/FFprobe mantidos byte-a-byte pelos hashes auditados da v0.0.18
- regressao completa, captura 1672x941, gate de sidebar invariavel, build e smoke do portable executados antes da publicacao

SHA-256 do portable: $hash
"@

gh release create $Tag "publish/$Portable" publish/SHA256SUMS.txt publish/FFMPEG_SOURCE_INFO.txt publish/INTEGRATIONS-MANIFEST.json publish/HOME-v0.0.19.png --target $target --title 'Monitor de Noticias Python 0.0.19' --notes $notes
Write-Host "RELEASE_CREATED=$Tag"
Write-Host "RELEASE_SHA256=$hash"
