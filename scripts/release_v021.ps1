$ErrorActionPreference='Stop'
$Tag='v0.0.21'
$Portable='MONITOR-DE-NOTICIAS-PYTHON-portable-windows-x64.zip'
$PrevAssetId='568214482'
$PrevHash='083b6bcfcdd58282ad3eb266e653cf30a78fdc280016e997297332b16cea98e5'
$FfmpegHash='91678b935eb52cc740249474574b6042768b744c622347f28a1b487e1ed29915'
$FfprobeHash='c42ada47df746e3788e2ba3ed2f7af07662a58f9088f9894e1b14d3d5c432263'
$Truth=@(
  @{Path='resources/ui/v021/noticias-page-q90.webp';Size=170594;Hash='4c228cb5d0a134501f2f69698f4bf088b0d447db8355bacd970b57eb475cb3a3'},
  @{Path='resources/ui/v021/fontes-page-q90.webp';Size=154042;Hash='a425e04f7bd91e77d9546edc3d7e373771f96415e09e5c60a3ff01cefa0bc3f6'},
  @{Path='resources/ui/v021/termos-page-q90.webp';Size=136628;Hash='8b199f3f67c8b5e6d24e8825fe2a05f10167035b1890b5e16bee3fe607b69274'}
)

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
$env:QT_QPA_PLATFORM='offscreen'
$env:MONITOR_DISABLE_WEATHER='1'
$env:MONITOR_DISABLE_EXTERNAL_INTEGRATIONS='1'
python -m compileall -q src tests scripts run.py
if($LASTEXITCODE -ne 0){throw 'Compilacao Python falhou'}
python -m pytest -q
if($LASTEXITCODE -ne 0){throw 'Regressao falhou'}

foreach($asset in $Truth){
  $item=Get-Item $asset.Path -ErrorAction Stop
  if($item.Length -ne $asset.Size){throw "Imagem-verdade tamanho divergente: $($asset.Path) = $($item.Length)"}
  $sha=(Get-FileHash $item.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
  if($sha -ne $asset.Hash){throw "Imagem-verdade hash divergente: $($asset.Path) = $sha"}
}

$env:QT_QPA_PLATFORM='windows'
python scripts/capture_v021_literal_tabs.py
if($LASTEXITCODE -ne 0){throw 'Gate visual/overlap/sidebar v0.0.21 falhou'}

$run=Get-Content run.py -Raw
if($run -notmatch 'install_v021_literal_tabs\(\)'){throw 'Camada literal v0.0.21 ausente'}
if($run -notmatch 'install_v021_surface_stability\(\)'){throw 'Estabilidade de superficies v0.0.21 ausente'}
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
$previousZip=Join-Path (Resolve-Path previous).Path $Portable
$assetUrl="https://api.github.com/repos/tysudess/MONITOR-DE-NOTICAS-PYTHON/releases/assets/$PrevAssetId"
& curl.exe --fail --location --silent --show-error -H "Authorization: Bearer $env:GH_TOKEN" -H 'Accept: application/octet-stream' -H 'X-GitHub-Api-Version: 2022-11-28' $assetUrl -o $previousZip
if($LASTEXITCODE -ne 0){throw 'Download autenticado do portable v0.0.20 falhou'}
if((Get-FileHash $previousZip -Algorithm SHA256).Hash.ToLowerInvariant() -ne $PrevHash){throw 'Hash do portable v0.0.20 divergente'}
$extract=Join-Path $env:RUNNER_TEMP 'v020-source-v021'
if(Test-Path $extract){Remove-Item $extract -Recurse -Force}
Expand-Archive $previousZip $extract -Force
$root=Get-ChildItem $extract -Directory | Where-Object {Test-Path (Join-Path $_.FullName 'MonitorDeNoticias.exe')} | Select-Object -First 1
if(-not $root){throw 'Raiz do portable v0.0.20 ausente'}
$ff=Join-Path $root.FullName 'bin/ffmpeg.exe'; $fp=Join-Path $root.FullName 'bin/ffprobe.exe'
if((Get-FileHash $ff -Algorithm SHA256).Hash.ToLowerInvariant() -ne $FfmpegHash){throw 'FFmpeg divergente'}
if((Get-FileHash $fp -Algorithm SHA256).Hash.ToLowerInvariant() -ne $FfprobeHash){throw 'FFprobe divergente'}
$audit=Join-Path $env:RUNNER_TEMP 'ffmpeg-v021'; New-Item -ItemType Directory -Force $audit | Out-Null
Copy-Item $ff (Join-Path $audit 'ffmpeg.exe') -Force; Copy-Item $fp (Join-Path $audit 'ffprobe.exe') -Force
$env:MONITOR_VALIDATED_FFMPEG_DIR=$audit

$portableOut=Join-Path $env:RUNNER_TEMP 'v021-portable-out'
if(Test-Path $portableOut){Remove-Item $portableOut -Recurse -Force}
./scripts/build_portable.ps1 -OutputDir $portableOut
$newZip=Join-Path $portableOut $Portable
if(-not (Test-Path $newZip)){throw "ZIP recém-gerado ausente: $newZip"}
$newZip=(Get-Item $newZip).FullName
./scripts/validate_portable.ps1 -ZipPath $newZip

if(Test-Path publish){Remove-Item publish -Recurse -Force}
New-Item -ItemType Directory publish | Out-Null
Copy-Item $newZip "publish/$Portable"
$hash=(Get-FileHash $newZip -Algorithm SHA256).Hash.ToLowerInvariant()
"$hash  $Portable" | Set-Content publish/SHA256SUMS.txt -Encoding ascii
Copy-Item portable/FFMPEG_SOURCE_INFO.txt publish/FFMPEG_SOURCE_INFO.txt
Copy-Item resources/integrations/manifest.json publish/INTEGRATIONS-MANIFEST.json
foreach($name in @('HOME-v0.0.21.png','NOTICIAS-v0.0.21.png','FONTES-v0.0.21.png','TERMOS-v0.0.21.png')){Copy-Item "artifacts/$name" "publish/$name"}

if(gh release view $Tag 2>$null){throw "$Tag ja existe"}
$notes=@"
Monitor de Noticias Python 0.0.21 — Windows Portable x64

- Notícias, Fontes e Termos usam literalmente as imagens-verdade fornecidas, sem reinterpretar o layout
- as superfícies finais são opacas e eliminam o vazamento visual da interface antiga por baixo
- dados variáveis são redesenhados a partir dos mesmos controller/state/widgets reais já existentes
- Home recebe correção das faixas duplicadas de cards e monitoramento, removendo números sobrepostos
- sidebar global de 225 px permanece idêntica ao navegar e retornar entre Início, Notícias, Fontes e Termos
- páginas funcionais originais, callbacks, filtros, banco, coletores, matching, automação, proxy e credenciais são preservados
- todas as 15 rotas funcionais permanecem registradas
- imagens-verdade validadas por tamanho e SHA-256 antes do build
- integrações externas e FFmpeg/FFprobe preservados pelos commits/hashes auditados
- regressão completa, gate Windows com múltiplas idas/voltas, quatro capturas, build e smoke do portable executados antes da publicação

SHA-256 do portable: $hash
"@

gh release create $Tag "publish/$Portable" publish/SHA256SUMS.txt publish/FFMPEG_SOURCE_INFO.txt publish/INTEGRATIONS-MANIFEST.json publish/HOME-v0.0.21.png publish/NOTICIAS-v0.0.21.png publish/FONTES-v0.0.21.png publish/TERMOS-v0.0.21.png --target $target --title 'Monitor de Noticias Python 0.0.21' --notes $notes
Write-Host "RELEASE_CREATED=$Tag"
Write-Host "RELEASE_SHA256=$hash"
