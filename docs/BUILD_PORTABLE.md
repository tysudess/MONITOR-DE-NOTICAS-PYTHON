# BUILD PORTABLE — WINDOWS x64

## Fonte da build aprovada

- Repositório: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- Branch: `migration/python-foundation`
- Commit do artefato: `0f9ec957b3e9f3fdf9b02f5dbe9bb0836310d60d`
- Run: `34776048157`
- Workflow: `.github/workflows/pass17-build-portable.yml`
- Estratégia: PyInstaller **onedir**
- Entry point: `run.py`
- Executável: `MonitorDeNoticias.exe`

Nenhuma alteração documental posterior muda a origem do ZIP aprovado.

## Processo efetivamente usado

A build oficial foi executada pelo workflow com Python 3.12 e `scripts/build_portable.ps1`. O script:

1. limpa artefatos anteriores;
2. instala `requirements.txt` e `requirements-build.txt`;
3. gera `GloboplayLoginHelper.exe`;
4. executa PyInstaller onedir;
5. cria diretórios graváveis e copia resources/README/notices;
6. baixa/copia yt-dlp nightly, yt-dlp stable, Deno, FFmpeg e FFprobe;
7. grava `BUILD-INFO.json` e `BUILD-SHA.txt`;
8. valida estrutura e plugins Qt;
9. executa smoke local do runtime congelado;
10. remove estado artificial de `data`, `logs`, `temp`, `Videos` e `VideoEditorExports`;
11. rejeita estado sensível/pessoal inesperado;
12. cria o ZIP final e SHA-256.

Não houve etapa manual fora desse processo para produzir o candidato aprovado.

## Estrutura distribuída

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

`docs/` não é copiado para o portable. O workflow portable também não dispara para alterações somente em `docs/**`.

## Versões registradas na build

- Python: `3.12.10`
- PySide6: `6.9.1`
- Qt: `6.9.1`
- PyInstaller: `6.15.0`
- yt-dlp nightly: `2026.08.30.232658`
- yt-dlp stable: `2026.08.19`
- Deno: `2.9.6`
- FFmpeg: `n9.0.1-29-gad500d59cb-20260913`
- FFprobe: `n9.0.1-29-gad500d59cb-20260913`

## Qt / preview

O motor de preview permanece `QMediaPlayer + QVideoWidget + QAudioOutput`. FFmpeg não é o player; ele é usado em processamento/exportação. O segundo runner comprovou reprodução, pause e seeks 500/1000/1500 ms usando o bundle.

## Binários externos

O portable validado contém os cinco binários exigidos:
- yt-dlp nightly
- yt-dlp stable
- Deno x64
- FFmpeg
- FFprobe

O segundo runner executou FFmpeg/FFprobe próprios com os globais ausentes.

## Artefato oficial

- nome: `MONITOR-DE-NOTICIAS-PYTHON-portable-windows-x64.zip`
- tamanho: `651329315` bytes
- tamanho descompactado: `1262862742` bytes
- SHA-256: `259739899fe044157d350ab077d877ef8dd9e024cd33939266e026e8df3563f4`
- `BUILD-SHA`: `0f9ec957b3e9f3fdf9b02f5dbe9bb0836310d60d`

## Validação externa

Job independente, sem checkout do source:
- hash idêntico: PASS
- reextração: PASS
- primeira execução: PASS
- primeiro smoke: PASS
- reabertura: PASS
- movimentação: PASS
- path com espaços/acentos: PASS
- segundo smoke: PASS
- shutdown: PASS
- órfãos: 0
- temporários: PASS
- segredos/dados pessoais no artefato: 0

## Estado

**PORTABLE VALIDADO**

Não rebuildar somente para incorporar documentação.
