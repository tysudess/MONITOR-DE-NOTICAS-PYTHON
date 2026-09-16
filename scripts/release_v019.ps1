$ErrorActionPreference='Stop'
$Tag='v0.0.19'
$Portable='MONITOR-DE-NOTICIAS-PYTHON-portable-windows-x64.zip'
$PrevTag='v0.0.18'
$PrevHash='607c85cc48ec9722aaee0b65acd1a6188364833b1f26a868f58a7199e78162f8'
$FfmpegHash='91678b935eb52cc740249474574b6042768b744c622347f28a1b487e1ed29915'
$FfprobeHash='c42ada47df746e3788e2ba3ed2f7af07662a58f9088f9894e1b14d3d5c432263'
$ReferenceHash='d36b34896671cfe632da2585e9cbb37e16999a9d417b5d8e77ebf961917f0d2f'
$ReferenceBytes=54218

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
$env:QT_QPA_PLATFORM='offscreen'
$env:MONITOR_DISABLE_WEATHER='1'
$env:MONITOR_DISABLE_EXTERNAL_INTEGRATIONS='1'
python -m compileall -q src tests scripts run.py
if($LASTEXITCODE -ne 0){throw 'Compilacao Python falhou'}
python -m pytest -q
if($LASTEXITCODE -ne 0){throw 'Regressao falhou'}

# A Home deve usar exatamente o mesmo ativo integral empacotado no programa.
$parts=Get-ChildItem 'resources/ui/v019/home-full-q20' -Filter 'part*.b64' | Sort-Object Name
if(-not $parts -or $parts.Count -lt 5){throw 'Fragmentos da imagem-verdade integral v0.0.19 ausentes'}
$encoded=($parts | ForEach-Object {(Get-Content $_.FullName -Raw).Trim()}) -join ''
$referenceBytes=[Convert]::FromBase64String($encoded)
if($referenceBytes.Length -ne $ReferenceBytes){throw "Imagem-verdade integral com tamanho divergente: $($referenceBytes.Length)"}
$referenceTemp=Join-Path $env:RUNNER_TEMP 'home-truth-v019.webp'
[IO.File]::WriteAllBytes($referenceTemp,$referenceBytes)
$referenceSha=(Get-FileHash $referenceTemp -Algorithm SHA256).Hash.ToLowerInvariant()
if($referenceSha -ne $ReferenceHash){throw "Imagem-verdade integral divergente: $referenceSha"}
python -c "from PIL import Image; p=r'$referenceTemp'; im=Image.open(p); assert im.size==(1672,941), im.size; print('REFERENCE_OK', im.size)"
if($LASTEXITCODE -ne 0){throw 'Dimensao da imagem-verdade integral divergente'}

$env:QT_QPA_PLATFORM='windows'
python scripts/capture_home_layout.py
if($LASTEXITCODE -ne 0){throw 'Gate visual/sidebar v0.0.19 falhou'}

$run=Get-Content run.py -Raw
if($run -notmatch 'install_v017_home_truth\(\)'){throw 'Base funcional da Home ausente'}
if($run -notmatch 'install_v018_home_visual_fidelity\(\)'){throw 'Base visual v0.0.18 ausente'}
if($run -notmatch 'install_v019_exact_reference\(\)'){throw 'Shell v0.0.19 ausente'}
if($run -notmatch 'install_v019_literal_screen\(\)'){throw 'Camada literal integral v0.0.19 ausente'}
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

- Home passa a usar a imagem-verdade integral fornecida pelo usuario como composicao visual literal
- sidebar usa o recorte literal da mesma referencia e permanece visualmente invariavel em todas as abas
- topbar usa o recorte literal da mesma referencia; busca real continua ativa por cima da composicao
- nove cards da Home mantem areas de clique ligadas as rotas reais do programa
- tipografia e brilho deixam de ser aproximados: sao os pixels da propria referencia visual
- todas as 15 secoes/rotas existentes continuam registradas, inclusive Extrator de Noticias e Automacao Planilhas
- controller, banco, coletores, matching, automacao, proxy, credenciais e motores de ferramentas nao foram trocados
- Editor PDF, Extrator de Videos, Editor de Video, Capas e integracoes originais preservados
- FFmpeg/FFprobe mantidos byte-a-byte pelos hashes auditados da v0.0.18
- imagem integral validada antes do build: 1672x941, $ReferenceBytes bytes, SHA-256 $ReferenceHash
- regressao completa, captura 1672x941, gate de sidebar invariavel, build e smoke do portable executados antes da publicacao

SHA-256 do portable: $hash
"@

gh release create $Tag "publish/$Portable" publish/SHA256SUMS.txt publish/FFMPEG_SOURCE_INFO.txt publish/INTEGRATIONS-MANIFEST.json publish/HOME-v0.0.19.png --target $target --title 'Monitor de Noticias Python 0.0.19' --notes $notes
Write-Host "RELEASE_CREATED=$Tag"
Write-Host "RELEASE_SHA256=$hash"
