param(
    [string]$OutputDir = "portable-out"
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root

Write-Host "== Integrações originais preservadas =="
& (Join-Path $PSScriptRoot "build_external_integrations.ps1")
if ($LASTEXITCODE -ne 0) { throw "Falha ao materializar as integrações externas." }

Write-Host "== Build portable principal =="
& (Join-Path $PSScriptRoot "build_portable.ps1") -OutputDir $OutputDir
if ($LASTEXITCODE -ne 0) { throw "Falha na build portable principal." }

$portableRoot = Join-Path $Root "dist/MonitorDeNoticias"
$required = @(
    "resources/integrations/manifest.json",
    "resources/integrations/extrator-noticias/app/Extrator de Materias.exe",
    "resources/integrations/automacao-planilhas/app/Automacao Planilhas.exe",
    "resources/integrations/capas/source/app/ui.py",
    "resources/integrations/capas/source/assets/principais_capas_cover.png",
    "resources/integrations/capas/source/google-apps-script/GmailCentralClipping.gs",
    "resources/integrations/video-editor/source/advanced_editor.py",
    "resources/integrations/video-editor/source/range_slider.py"
)
foreach ($rel in $required) {
    if (-not (Test-Path (Join-Path $portableRoot $rel))) { throw "Portable sem integração obrigatória: $rel" }
}
Write-Host "FULL_PORTABLE_INTEGRATIONS_OK=YES"
