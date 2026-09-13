# BUILD PORTABLE — WINDOWS x64

## Fonte da build

- Repositório: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- Branch: `migration/python-foundation`
- Estratégia: PyInstaller **onedir**.
- Python: 3.12.x.
- PySide6: 6.9.1.
- PyInstaller: 6.15.0.
- Entry point: `run.py`.
- Executável: `MonitorDeNoticias.exe`.

O empacotamento não altera regras de negócio, repositories, collectors, matching, AutomationService, motores PDF, Extrator ou Editor de Vídeo.

## Build reprodutível

No Windows x64:

```powershell
./scripts/build_portable.ps1
```

O script limpa artefatos antigos, instala dependências declaradas, gera o helper Globoplay, executa PyInstaller onedir, prepara resources/diretórios graváveis, obtém os binários externos previstos, grava `BUILD-INFO.json`/`BUILD-SHA.txt`, executa smoke local, remove estado artificial e cria o ZIP final.

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

`docs/` não é copiado para o portable. Atualizações documentais posteriores não alteram o ZIP já produzido e não exigem rebuild apenas por documentação.

## Qt / PySide6

O spec coleta PySide6/PDFium e valida a presença dos plugins/DLLs necessários, incluindo `qwindows.dll`, QtCore, QtGui, QtWidgets e QtMultimedia.

O motor do preview permanece `QMediaPlayer + QVideoWidget + QAudioOutput`; FFmpeg é usado em processamento/exportação.

## Binários externos

A build usa binários em `bin/` do próprio portable:

- yt-dlp nightly oficial
- yt-dlp stable oficial
- Deno x64 oficial
- FFmpeg/FFprobe BtbN n9.0 com fallback Gyan Essentials

Não existe fallback para FFmpeg/FFprobe do PATH na validação do pacote.

## Helper Globoplay

`tools/build-globoplay-login-helper.py` gera `resources/globoplay-login-helper/GloboplayLoginHelper.exe` com PySide6/PyInstaller. Em runtime o Extrator materializa o helper em seu diretório de dados conforme o contrato migrado.

## Workflow de validação

`.github/workflows/pass17-build-portable.yml` possui dois ambientes:

1. `build-windows-x64`: checkout, regressão, build limpa, smoke local, ZIP e upload;
2. `validate-zip-without-repository`: recebe somente o artifact, sem checkout do source, recalcula hash, reextrai e executa o gate externo.

O segundo ambiente lança o EXE com CWD externo e PATH reduzido, testa os binários do bundle e move fisicamente a pasta antes de repetir o smoke.

## Resultado objetivo do candidato 186a28

Run: `34768584764`.

Commit do artefato:

`186a28e4a5f53296178fd9d0ee74637a8a5149bf`

### Build job

**SUCCESS**.

- `148 passed`
- clean build: PASS
- local runtime smoke: PASS
- ZIP gerado: SIM
- `BUILD-SHA.txt`: correto

### ZIP

- nome: `MONITOR-DE-NOTICIAS-PYTHON-portable-windows-x64.zip`
- tamanho: `651329759` bytes
- tamanho descompactado: `1262864276` bytes
- SHA-256: `5ebd57f312d3ce66b51b10b1abda8d92076a7971ad25aeb0bf0b23f78ee13cf2`

O digest `adb365bc66b1aa21284494e9d40e3be6d030d242ad1afff450f0cde17f61a600` pertence ao contêiner de artifact criado pelo GitHub Actions para transportar o ZIP e NÃO substitui o SHA-256 interno acima.

### Segundo runner

**FAIL** no gate externo.

O segundo runner recalculou exatamente o mesmo SHA-256 interno, reextraiu do zero e passou pelo primeiro smoke integral, reabertura, movimentação e nova inicialização.

O segundo smoke também passou pelo Extrator, comprovando que `PORT-004` não reapareceu.

A falha posterior foi:

```text
Evento de notícia nova não acionou callback de notificação.
```

## Diagnóstico PORT-005

O gate de notícias usa um banco persistente sob `temp/pipeline-smoke` e uma notícia artificial de link fixo. No segundo smoke, a mesma notícia já está gravada. O `AutomationService` notifica apenas resultados novos; logo, não notificar novamente é comportamento esperado.

A asserção externa recria a lista de eventos e exige uma nova notificação, tornando o segundo smoke não idempotente.

Classificação: **FALHA DO GATE**.

Nenhuma correção foi aplicada no Passo 20.

## Warnings de mídia

Warnings DXVA2 no runner não são falha funcional enquanto o QMediaPlayer provar reprodução. No candidato 186a28 o player avançou (`325 ms`) e os seeks 500/1000/1500 ms passaram, portanto esses warnings foram corretamente separados do erro real.

## Estado final desta build

A build em si foi produzida e transportada corretamente, mas o candidato não cumpriu o ciclo integral de validação externa porque o segundo smoke foi interrompido pelo PORT-005 antes do teardown final.

**PORTABLE NÃO VALIDADO — FALHA TÉCNICA**
