# BUILD PORTABLE — WINDOWS x64

## Fonte da build

- Repositório: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- Branch: `migration/python-foundation`
- Estratégia: PyInstaller **onedir**.
- Python: 3.12.x.
- PySide6: 6.9.1.
- PyInstaller: 6.15.0.
- Entry point: `run.py`, o mesmo fluxo usado em desenvolvimento.
- Executável: `MonitorDeNoticias.exe`.

O empacotamento não altera regras de negócio, repositories, collectors, matching, AutomationService, motores PDF, Extrator ou Editor de Vídeo.

## Por que PyInstaller onedir

A release V8 aprovada já utiliza PyInstaller 6.15.0 para o editor PySide6. O formato `onedir` reduz risco para Qt/PySide6, plugins dinâmicos, QtMultimedia, PDFium e diretórios graváveis. O runtime congelado fica em `_internal/`, enquanto recursos e dados graváveis permanecem ao lado do executável.

## Build reprodutível

No Windows x64, com Python 3.12 disponível apenas para **construir** o pacote:

```powershell
./scripts/build_portable.ps1
```

O script:

1. remove `build/`, `dist/`, cache do helper e staging antigo;
2. instala as dependências declaradas em `requirements.txt` e `requirements-build.txt`;
3. gera `GloboplayLoginHelper.exe` a partir do helper aprovado com PyInstaller onefile/windowed;
4. gera `MonitorDeNoticias.exe` usando `MonitorDeNoticias.spec` em modo onedir/windowed;
5. copia somente os resources aprovados para `resources/` externo;
6. cria `data/`, `logs/`, `temp/`, `Videos/` e `VideoEditorExports/` como diretórios graváveis;
7. baixa os cinco binários conforme a estratégia da release Kotlin: yt-dlp nightly, yt-dlp stable, Deno x64, FFmpeg e FFprobe;
8. valida a execução dos binários;
9. grava `BUILD-INFO.json` e `BUILD-SHA.txt`;
10. gera `MONITOR-DE-NOTICIAS-PYTHON-portable-windows-x64.zip` e seu SHA-256.

## Estrutura esperada

```text
MonitorDeNoticias/
├── MonitorDeNoticias.exe
├── _internal/
├── bin/
│   ├── yt-dlp.exe
│   ├── yt-dlp-stable.exe
│   ├── deno.exe
│   ├── ffmpeg.exe
│   └── ffprobe.exe
├── resources/
│   ├── monitor-icon.svg
│   ├── pdf-default-cover.b64
│   └── globoplay-login-helper/GloboplayLoginHelper.exe
├── data/
├── logs/
├── temp/
├── Videos/
├── VideoEditorExports/
├── BUILD-INFO.json
├── BUILD-SHA.txt
├── README_PORTABLE.txt
└── THIRD_PARTY_NOTICES.txt
```

`AppPaths` resolve a raiz frozen por `sys.executable`, portanto o aplicativo não depende do current working directory.

## Qt / PySide6

O spec coleta PySide6 porque o aplicativo usa módulos Qt carregados dinamicamente, incluindo QtMultimedia e plugins de plataforma. A validação exige:

- `qwindows.dll`;
- `Qt6Core.dll`;
- `Qt6Gui.dll`;
- `Qt6Widgets.dll`;
- `Qt6Multimedia.dll`;
- `Qt6MultimediaWidgets.dll`;
- ao menos um plugin em `plugins/multimedia`.

O motor do preview continua sendo `QMediaPlayer + QVideoWidget + QAudioOutput`; FFmpeg permanece exclusivamente no processamento/exportação.

## Binários externos

A build não usa FFmpeg/FFprobe do PATH. Os executáveis são esperados em `bin/`. As fontes de download reproduzem as da release V8:

- yt-dlp nightly: release nightly oficial;
- yt-dlp stable: release oficial;
- Deno: `deno-x86_64-pc-windows-msvc.zip` oficial;
- FFmpeg/FFprobe: BtbN n9.0 GPL com fallback para Gyan Essentials.

As versões efetivamente incluídas ficam registradas em `BUILD-INFO.json`.

## Helper Globoplay

`tools/build-globoplay-login-helper.py` reproduz a geração original do helper: PySide6 6.9.1 + PyInstaller 6.15.0, `--onefile --windowed`. O executável resultante é colocado em `resources/globoplay-login-helper/GloboplayLoginHelper.exe`; em runtime o Extrator o materializa em `data/extractor/runtime/` como no Kotlin.

## Validação limpa

A workflow `Passo 17 - Windows Portable` possui dois jobs:

1. `build-windows-x64`: checkout, suíte normal, build limpa e geração do artefato;
2. `validate-zip-without-repository`: baixa **somente** o artefato, sem checkout e sem setup-python, reextrai o ZIP em caminho com espaço/acento e executa `scripts/validate_portable.ps1`.

O validador:

- compara SHA-256;
- confirma ausência de `src/`, `tests/`, `.git` e venv na pasta final;
- verifica DLLs/plugins Qt;
- executa FFmpeg/FFprobe próprios;
- inicia apenas `MonitorDeNoticias.exe` com CWD externo e PATH reduzido, sem Python/FFmpeg de desenvolvimento;
- verifica criação de bancos/logs na raiz portable;
- navega pelas páginas principais via Windows UI Automation;
- abre o Editor de Vídeo a partir do Monitor, carrega mídia artificial, executa play/pause/seek e exportação;
- valida a exportação com o `ffprobe.exe` do próprio portable;
- confirma que o handle de mídia é liberado e que não ficaram processos FFmpeg/FFprobe do portable.

## Troubleshooting

- `qwindows.dll ausente`: revisar coleta de plugins PySide6 no spec.
- QtMultimedia ausente: revisar DLLs/plugins em `_internal/PySide6/Qt`.
- `ffmpeg.exe`/`ffprobe.exe` ausentes: corrigir staging/cópia em `scripts/build_portable.ps1`; não usar PATH como fallback.
- helper Globoplay ausente/incompleto: corrigir a etapa `tools/build-globoplay-login-helper.py`; não apontar para executável externo.
- resources não encontrados: verificar que `resources/` está ao lado do EXE; não alterar `AppPaths` para depender de CWD.
- banco/log em local inesperado: bloquear a build e revisar somente paths/empacotamento.

## Resultado da validação

Esta seção é atualizada depois da execução final da workflow do Passo 17. Não considerar a build validada antes de o job de ambiente limpo e o ZIP reextraído concluírem com sucesso.
