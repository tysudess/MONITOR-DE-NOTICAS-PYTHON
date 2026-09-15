param(
    [string]$StageRoot = ""
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root

if (-not $IsWindows) { throw "As integrações externas desta build são Windows x64." }

$Work = Join-Path $Root ".integration-build"
if (-not $StageRoot) { $StageRoot = Join-Path $Root "resources/integrations" }
if (Test-Path $Work) { Remove-Item $Work -Recurse -Force }
if (Test-Path $StageRoot) { Remove-Item $StageRoot -Recurse -Force }
New-Item -ItemType Directory -Force $Work, $StageRoot | Out-Null

$sources = [ordered]@{
    extratorNoticias = [ordered]@{
        repo = "https://github.com/tysudess/Extrator-de-noticias-windows.git"
        sha = "ea43bb344d74dc2a32cc1d733aaabea54d763150"
        packageBlob = "72065b9f4bb489eebe2ce848d482022ee3a65fee"
    }
    automacaoPlanilhas = [ordered]@{
        repo = "https://github.com/tysudess/automa-o-planilhas.git"
        sha = "51bd5386ea280edc2d56c6567be0113cfd84d2e5"
        packageBlob = "451a9ec3a7bdddda866922d841446e1c604b5034"
    }
    capas = [ordered]@{
        repo = "https://github.com/tysudess/capas-windows-portable.git"
        sha = "87705432008b00f114d27d1f1645c2c89e649365"
        coverBlob = "a5eda7a1e3df8cfee064be3e8967abbfe59db250"
    }
    videoEditor = [ordered]@{
        repo = "https://github.com/tysudess/extrator-video-windows.git"
        sha = "92f031c22cf8c23c2f5dd15a1857a6df4186b97e"
        editorBlob = "24c723c9f40946d1c13de0b9e23e55a182581e2d"
    }
}

function Checkout-Pinned([string]$Name, [string]$Repo, [string]$Sha) {
    $dest = Join-Path $Work $Name
    git clone --quiet --no-checkout $Repo $dest
    if ($LASTEXITCODE -ne 0) { throw "Falha ao clonar $Repo" }
    git -C $dest checkout --quiet --detach $Sha
    if ($LASTEXITCODE -ne 0) { throw "Falha ao fixar $Name no commit $Sha" }
    $actual = (git -C $dest rev-parse HEAD).Trim()
    if ($actual -ne $Sha) { throw "$Name divergente: $actual" }
    return $dest
}

function Copy-Original-Source([string]$Source, [string]$Destination) {
    New-Item -ItemType Directory -Force $Destination | Out-Null
    Get-ChildItem $Source -Force | Where-Object { $_.Name -ne ".git" } | ForEach-Object {
        Copy-Item $_.FullName $Destination -Recurse -Force
    }
}

function Build-Electron-App([string]$Name, [string]$Source, [string]$Destination) {
    Write-Host "== Electron: $Name =="
    Push-Location $Source
    try {
        npm install --no-audit --no-fund
        if ($LASTEXITCODE -ne 0) { throw "npm install falhou em $Name" }
        npx electron-builder --win --x64 --dir --publish never
        if ($LASTEXITCODE -ne 0) { throw "electron-builder falhou em $Name" }
    }
    finally { Pop-Location }
    $unpacked = Get-ChildItem (Join-Path $Source "dist") -Directory -Filter "win-unpacked" -Recurse | Select-Object -First 1
    if (-not $unpacked) { throw "win-unpacked não encontrado para $Name" }
    New-Item -ItemType Directory -Force $Destination | Out-Null
    Copy-Item (Join-Path $unpacked.FullName "*") $Destination -Recurse -Force
}

Write-Host "== Materializando fontes originais fixadas =="
$news = Checkout-Pinned "extrator-noticias" $sources.extratorNoticias.repo $sources.extratorNoticias.sha
$sheet = Checkout-Pinned "automacao-planilhas" $sources.automacaoPlanilhas.repo $sources.automacaoPlanilhas.sha
$covers = Checkout-Pinned "capas" $sources.capas.repo $sources.capas.sha
$video = Checkout-Pinned "video-editor" $sources.videoEditor.repo $sources.videoEditor.sha

# Provas de que os commits materializados correspondem aos arquivos enviados/validados.
$newsPackageBlob = (git -C $news rev-parse "HEAD:package.json").Trim()
$sheetPackageBlob = (git -C $sheet rev-parse "HEAD:package.json").Trim()
$coverBlob = (git -C $covers rev-parse "HEAD:assets/principais_capas_cover.png").Trim()
$editorBlob = (git -C $video rev-parse "HEAD:advanced_editor.py").Trim()
if ($newsPackageBlob -ne $sources.extratorNoticias.packageBlob) { throw "Fonte Extrator de Notícias divergente." }
if ($sheetPackageBlob -ne $sources.automacaoPlanilhas.packageBlob) { throw "Fonte Automação Planilhas divergente." }
if ($coverBlob -ne $sources.capas.coverBlob) { throw "Fonte Capas divergente." }
if ($editorBlob -ne $sources.videoEditor.editorBlob) { throw "Fonte Editor de Vídeo divergente." }

$newsStage = Join-Path $StageRoot "extrator-noticias"
$sheetStage = Join-Path $StageRoot "automacao-planilhas"
$coversStage = Join-Path $StageRoot "capas"
$videoStage = Join-Path $StageRoot "video-editor"

# Mantém TODO o programa original dos três projetos pedidos, sem editar a cópia de auditoria.
Copy-Original-Source $news (Join-Path $newsStage "source")
Copy-Original-Source $sheet (Join-Path $sheetStage "source")
Copy-Original-Source $covers (Join-Path $coversStage "source")

# v0.0.10: depois de preservar a cópia byte-a-byte acima, aplica somente na cópia
# de BUILD o overlay de integração do Monitor: proxy global único e ponte de URL.
python (Join-Path $Root "scripts/patch_v010_external_integrations.py") $news $sheet
if ($LASTEXITCODE -ne 0) { throw "Falha ao aplicar overlay v0.0.10 nas integrações externas." }

# Do extrator-video-windows entra SOMENTE o editor original solicitado.
New-Item -ItemType Directory -Force (Join-Path $videoStage "source") | Out-Null
Copy-Item (Join-Path $video "advanced_editor.py") (Join-Path $videoStage "source/advanced_editor.py") -Force
Copy-Item (Join-Path $video "range_slider.py") (Join-Path $videoStage "source/range_slider.py") -Force
@"
Origem: tysudess/extrator-video-windows
Commit: $($sources.videoEditor.sha)
Integração: somente AdvancedVideoEditorWidget e RangeSlider, conforme solicitado.
Os arquivos acima são copiados byte-a-byte do repositório de origem.
"@ | Set-Content (Join-Path $videoStage "source/ORIGIN.txt") -Encoding utf8

# Os aplicativos Electron são empacotados como diretórios. O fonte original
# continua preservado em /source e o executável recebe apenas o overlay acima.
Build-Electron-App "Extrator de Notícias" $news (Join-Path $newsStage "app")
Build-Electron-App "Automação de Planilhas" $sheet (Join-Path $sheetStage "app")

$manifest = [ordered]@{
    schema = 1
    generatedAtUtc = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
    extratorNoticias = [ordered]@{ repo=$sources.extratorNoticias.repo; commit=$sources.extratorNoticias.sha; executable="extrator-noticias/app/Extrator de Materias.exe"; overlay="v0.0.10 global-proxy + monitor-url bridge" }
    automacaoPlanilhas = [ordered]@{ repo=$sources.automacaoPlanilhas.repo; commit=$sources.automacaoPlanilhas.sha; executable="automacao-planilhas/app/Automacao Planilhas.exe"; overlay="v0.0.10 global-proxy" }
    capas = [ordered]@{ repo=$sources.capas.repo; commit=$sources.capas.sha; source="capas/source" }
    videoEditor = [ordered]@{ repo=$sources.videoEditor.repo; commit=$sources.videoEditor.sha; source="video-editor/source" }
}
$manifest | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $StageRoot "manifest.json") -Encoding utf8

$required = @(
    "extrator-noticias/app/Extrator de Materias.exe",
    "extrator-noticias/source/main.js",
    "extrator-noticias/source/engine/extrator-materia-v1.25.19-runtime.js",
    "automacao-planilhas/app/Automacao Planilhas.exe",
    "automacao-planilhas/source/main.js",
    "automacao-planilhas/source/engine/index.js",
    "capas/source/app/ui.py",
    "capas/source/assets/principais_capas_cover.png",
    "capas/source/google-apps-script/GmailCentralClipping.gs",
    "video-editor/source/advanced_editor.py",
    "video-editor/source/range_slider.py",
    "manifest.json"
)
foreach ($rel in $required) {
    if (-not (Test-Path (Join-Path $StageRoot $rel))) { throw "Integração incompleta: $rel" }
}

Write-Host "INTEGRATIONS_STAGE=$StageRoot"
Write-Host "NEWS_EXTRACTOR_COMMIT=$($sources.extratorNoticias.sha)"
Write-Host "SHEET_AUTOMATION_COMMIT=$($sources.automacaoPlanilhas.sha)"
Write-Host "COVERS_COMMIT=$($sources.capas.sha)"
Write-Host "VIDEO_EDITOR_COMMIT=$($sources.videoEditor.sha)"
