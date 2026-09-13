param(
    [Parameter(Mandatory=$true)][string]$ZipPath
)

$ErrorActionPreference = "Stop"
$ZipPath = (Resolve-Path $ZipPath).Path
$ExpectedHashFile = "$ZipPath.sha256"
if (-not (Test-Path $ExpectedHashFile)) { throw "Arquivo SHA-256 ausente: $ExpectedHashFile" }
$expected = ((Get-Content $ExpectedHashFile -Raw).Trim() -split "\s+")[0].ToLowerInvariant()
$actual = (Get-FileHash $ZipPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($expected -ne $actual) { throw "SHA-256 do ZIP não confere." }

$ExtractBase = Join-Path $env:RUNNER_TEMP "Edição Portable Monitor de Notícias"
if (Test-Path $ExtractBase) { Remove-Item $ExtractBase -Recurse -Force }
New-Item -ItemType Directory -Force $ExtractBase | Out-Null
Expand-Archive $ZipPath $ExtractBase -Force
$PortableRoot = Get-ChildItem $ExtractBase -Directory | Where-Object { Test-Path (Join-Path $_.FullName "MonitorDeNoticias.exe") } | Select-Object -First 1
if (-not $PortableRoot) { throw "Raiz portable não encontrada após reextrair o ZIP." }
$Root = $PortableRoot.FullName

$required = @(
    "MonitorDeNoticias.exe",
    "_internal",
    "resources/monitor-icon.svg",
    "resources/pdf-default-cover.b64",
    "resources/globoplay-login-helper/GloboplayLoginHelper.exe",
    "bin/yt-dlp.exe",
    "bin/yt-dlp-stable.exe",
    "bin/deno.exe",
    "bin/ffmpeg.exe",
    "bin/ffprobe.exe",
    "README_PORTABLE.txt",
    "THIRD_PARTY_NOTICES.txt",
    "BUILD-INFO.json",
    "BUILD-SHA.txt"
)
foreach ($rel in $required) {
    if (-not (Test-Path (Join-Path $Root $rel))) { throw "Item ausente no ZIP reextraído: $rel" }
}
foreach ($forbidden in @("src", "tests", ".git", ".venv", "venv")) {
    if (Test-Path (Join-Path $Root $forbidden)) { throw "Conteúdo de desenvolvimento indevido no portable: $forbidden" }
}

$qwindows = Get-ChildItem (Join-Path $Root "_internal") -Recurse -Filter "qwindows.dll" | Select-Object -First 1
if (-not $qwindows) { throw "qwindows.dll não encontrado no portable." }
$qtCore = Get-ChildItem (Join-Path $Root "_internal") -Recurse -Filter "Qt6Core.dll" | Select-Object -First 1
$qtGui = Get-ChildItem (Join-Path $Root "_internal") -Recurse -Filter "Qt6Gui.dll" | Select-Object -First 1
$qtWidgets = Get-ChildItem (Join-Path $Root "_internal") -Recurse -Filter "Qt6Widgets.dll" | Select-Object -First 1
$qtMultimedia = Get-ChildItem (Join-Path $Root "_internal") -Recurse -Filter "Qt6Multimedia.dll" | Select-Object -First 1
$qtMultimediaWidgets = Get-ChildItem (Join-Path $Root "_internal") -Recurse -Filter "Qt6MultimediaWidgets.dll" | Select-Object -First 1
if (-not $qtCore -or -not $qtGui -or -not $qtWidgets -or -not $qtMultimedia -or -not $qtMultimediaWidgets) { throw "DLLs Qt essenciais ausentes." }
$mediaPlugins = Get-ChildItem (Join-Path $Root "_internal") -Recurse -File | Where-Object { $_.FullName -match "plugins[\\/]multimedia" }
if (-not $mediaPlugins) { throw "Plugins QtMultimedia ausentes." }

# Prova que FFmpeg/FFprobe próprios funcionam sem depender do PATH do sistema.
$SampleDir = Join-Path $env:RUNNER_TEMP "portable-media"
if (Test-Path $SampleDir) { Remove-Item $SampleDir -Recurse -Force }
New-Item -ItemType Directory -Force $SampleDir | Out-Null
$Sample = Join-Path $SampleDir "amostra portable.mp4"
$ExportProbe = Join-Path $SampleDir "probe.json"
& (Join-Path $Root "bin/ffmpeg.exe") -y -f lavfi -i "testsrc=size=320x240:rate=25" -f lavfi -i "sine=frequency=440:sample_rate=44100" -t 2 -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 96k $Sample | Out-Null
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $Sample)) { throw "FFmpeg incluído não conseguiu gerar mídia de teste." }
& (Join-Path $Root "bin/ffprobe.exe") -v error -show_streams -show_format -of json $Sample | Set-Content $ExportProbe -Encoding utf8
if ($LASTEXITCODE -ne 0) { throw "FFprobe incluído falhou." }
$probe = Get-Content $ExportProbe -Raw | ConvertFrom-Json
if (-not ($probe.streams | Where-Object codec_type -eq "video")) { throw "FFprobe não encontrou vídeo." }
if (-not ($probe.streams | Where-Object codec_type -eq "audio")) { throw "FFprobe não encontrou áudio." }

# Lança somente o EXE, com CWD externo e PATH sem Python/FFmpeg externos.
$psi = [System.Diagnostics.ProcessStartInfo]::new()
$psi.FileName = Join-Path $Root "MonitorDeNoticias.exe"
$psi.WorkingDirectory = $env:WINDIR
$psi.UseShellExecute = $false
$psi.Environment["PATH"] = "$env:WINDIR\System32;$env:WINDIR"
$process = [System.Diagnostics.Process]::Start($psi)
if (-not $process) { throw "Não foi possível iniciar MonitorDeNoticias.exe." }

try {
    $deadline = [DateTime]::UtcNow.AddSeconds(25)
    do {
        Start-Sleep -Milliseconds 500
        if ($process.HasExited) { throw "MonitorDeNoticias.exe encerrou prematuramente com código $($process.ExitCode)." }
        $ready = (Test-Path (Join-Path $Root "data/news.db")) -and (Test-Path (Join-Path $Root "data/videos.db")) -and (Test-Path (Join-Path $Root "logs/monitor-noticias.log"))
    } while (-not $ready -and [DateTime]::UtcNow -lt $deadline)
    if (-not $ready) { throw "Primeira execução não criou bancos/log dentro da raiz portable." }

    Add-Type -AssemblyName UIAutomationClient
    Add-Type -AssemblyName UIAutomationTypes
    $desktop = [System.Windows.Automation.AutomationElement]::RootElement
    $pidCond = [System.Windows.Automation.PropertyCondition]::new([System.Windows.Automation.AutomationElement]::ProcessIdProperty, $process.Id)
    $main = $desktop.FindFirst([System.Windows.Automation.TreeScope]::Children, $pidCond)
    if (-not $main) { throw "Janela principal não encontrada por UI Automation." }

    function Invoke-ButtonContains($root, [string]$text) {
        $buttons = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.PropertyCondition]::new([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button))
        foreach ($b in $buttons) {
            if (($b.Current.Name -as [string]) -like "*$text*") {
                $p = $b.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
                $p.Invoke(); return $true
            }
        }
        return $false
    }

    # Navegação pelas páginas essenciais e ferramentas internas.
    foreach ($page in @("Notícias", "Vídeos", "Demandas", "Fontes", "Histórico", "Termos", "Configurações", "Extrator de Vídeos", "Editor de PDF", "Editor de Vídeo")) {
        if (-not (Invoke-ButtonContains $main $page)) { throw "Botão de navegação não encontrado: $page" }
        Start-Sleep -Milliseconds 250
        if ($process.HasExited) { throw "Aplicação encerrou durante navegação: $page" }
    }

    # O workspace do Editor de Vídeo abre automaticamente sua janela top-level.
    Start-Sleep -Seconds 2
    $windows = $desktop.FindAll([System.Windows.Automation.TreeScope]::Children, $pidCond)
    $editor = $null
    foreach ($w in $windows) { if (($w.Current.Name -as [string]) -like "*VideoMaster PRO*") { $editor = $w; break } }
    if (-not $editor) { throw "Janela real do Editor de Vídeo não abriu a partir do Monitor." }

    # Abrir mídia real usando o diálogo nativo.
    if (-not (Invoke-ButtonContains $editor "Abrir Vídeo")) { throw "Botão Abrir Vídeo não encontrado." }
    Start-Sleep -Seconds 1
    $dialogs = $desktop.FindAll([System.Windows.Automation.TreeScope]::Children, $pidCond)
    $dialog = $null
    foreach ($w in $dialogs) { if (($w.Current.Name -as [string]) -like "*Abrir vídeos*") { $dialog = $w; break } }
    if (-not $dialog) { throw "Diálogo Abrir vídeos não encontrado." }
    $edits = $dialog.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.PropertyCondition]::new([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Edit))
    if ($edits.Count -lt 1) { throw "Campo de arquivo do diálogo não encontrado." }
    $valuePattern = $edits.Item($edits.Count - 1).GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
    $valuePattern.SetValue($Sample)
    if (-not (Invoke-ButtonContains $dialog "Abrir")) { throw "Botão Abrir do diálogo não encontrado." }
    Start-Sleep -Seconds 3

    # Play/pause real e seek por slider quando exposto pelo backend de acessibilidade.
    if (-not (Invoke-ButtonContains $editor "▶")) { throw "Botão Play não encontrado." }
    Start-Sleep -Seconds 1
    Invoke-ButtonContains $editor "⏸" | Out-Null
    $sliders = $editor.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.PropertyCondition]::new([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Slider))
    if ($sliders.Count -gt 0) {
        try {
            $range = $sliders.Item(0).GetCurrentPattern([System.Windows.Automation.RangeValuePattern]::Pattern)
            $target = [Math]::Min(1000.0, $range.Current.Maximum)
            $range.SetValue($target)
        } catch { Write-Warning "Slider não expôs RangeValuePattern: $($_.Exception.Message)" }
    }

    # Exporta usando o FFmpeg que está dentro da pasta portable.
    if (-not (Invoke-ButtonContains $editor "Exportar trecho")) { throw "Exportar trecho não encontrado." }
    $exportDeadline = [DateTime]::UtcNow.AddSeconds(60)
    do {
        Start-Sleep -Milliseconds 500
        $exports = Get-ChildItem (Join-Path $Root "VideoEditorExports") -Filter "*.mp4" -ErrorAction SilentlyContinue
    } while (-not $exports -and [DateTime]::UtcNow -lt $exportDeadline)
    if (-not $exports) { throw "Editor de Vídeo não gerou exportação no portable." }
    $exported = $exports | Select-Object -First 1
    $exportJson = & (Join-Path $Root "bin/ffprobe.exe") -v error -show_streams -show_format -of json $exported.FullName | ConvertFrom-Json
    if (-not ($exportJson.streams | Where-Object codec_type -eq "video")) { throw "Exportação não contém vídeo." }

    # Fecha a janela do editor para validar liberação do handle de mídia.
    try {
        $wp = $editor.GetCurrentPattern([System.Windows.Automation.WindowPattern]::Pattern)
        $wp.Close()
    } catch { Write-Warning "Não foi possível fechar editor via UIA: $($_.Exception.Message)" }
    Start-Sleep -Seconds 2
    Remove-Item $Sample -Force
    if (Test-Path $Sample) { throw "Player manteve handle do arquivo de origem após fechar editor." }

    # Não existe API externa segura para acionar o menu de tray em runner headless.
    # O shutdown coordenado é coberto pela suíte Windows; aqui validamos que não ficaram ffmpeg/ffprobe do portable.
    $orphans = Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -in @("ffmpeg", "ffprobe") -and $_.Path -like "$Root*" }
    if ($orphans) { throw "Processo FFmpeg/FFprobe órfão após a operação portable." }

    Write-Host "PORTABLE_RUNTIME_OK root=$Root"
    Write-Host "PORTABLE_MEDIA_OK export=$($exported.Name)"
}
finally {
    if ($process -and -not $process.HasExited) {
        $process.Kill($true)
        $process.WaitForExit(10000) | Out-Null
    }
}

Write-Host "PORTABLE_ZIP_VALIDATION_OK sha256=$actual"
