# VALIDAÇÃO PORTABLE — CICLO FINAL APROVADO

## Candidato congelado

- repositório: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- branch: `migration/python-foundation`
- commit exato: `0f9ec957b3e9f3fdf9b02f5dbe9bb0836310d60d`
- workflow: `Passo 17 - Windows Portable`
- run: `34776048157`
- conclusão: `success`
- build iniciada em: `2026-09-13T18:54:14Z`
- build metadata UTC: `2026-09-13T18:57:50Z`

Nenhum ZIP posterior substitui este candidato.

## Artefato validado

- nome: `MONITOR-DE-NOTICIAS-PYTHON-portable-windows-x64.zip`
- tamanho: `651329315` bytes
- tamanho descompactado: `1262862742` bytes
- SHA-256: `259739899fe044157d350ab077d877ef8dd9e024cd33939266e026e8df3563f4`
- `BUILD-SHA.txt`: `0f9ec957b3e9f3fdf9b02f5dbe9bb0836310d60d`

O contêiner de artifact do GitHub Actions possui hash/tamanho próprios e não deve ser confundido com o ZIP interno.

## Suíte antes do empacotamento

- TOTAL: 149
- PASS: 149
- FAIL: 0
- ERROR: 0
- SKIP: 0
- XFAIL: 0

## Build

A workflow fez checkout da branch real, comprovou worktree limpa e HEAD igual ao `github.sha`, instalou as dependências, executou a regressão, criou o helper Globoplay, gerou PyInstaller onedir, preparou recursos/binários, executou smoke local, limpou todo estado artificial e só então compactou.

Resultado: **PASS**.

## Segundo runner independente

Job: `validate-zip-without-repository`.

Ambiente:
- Microsoft Windows Server 2025
- Microsoft Windows NT 10.0.26100.0
- AMD64
- imagem `windows-2025-vs2026`
- sem checkout de desenvolvimento
- FFmpeg/FFprobe globais ausentes

O segundo runner recebeu somente o artifact, recalculou o SHA-256 do ZIP interno e obteve exatamente `259739899fe044157d350ab077d877ef8dd9e024cd33939266e026e8df3563f4`.

Resultado: **HASHES IDÊNTICOS**.

## Reextração, abertura e movimentação

O ZIP foi extraído do zero para diretório com espaços e acentos. O EXE iniciou com CWD externo. Depois do primeiro smoke, a aplicação reabriu e a pasta inteira foi movida para outro caminho com espaços e acentos. A abertura após a movimentação também passou.

- REEXTRAÇÃO = PASS
- REABERTURA = PASS
- MOVIMENTAÇÃO = PASS
- PATH COM ESPAÇOS = PASS
- PATH COM ACENTOS = PASS
- CWD DIFERENTE = PASS

## Primeiro e segundo smoke

Primeiro smoke:
`PORTABLE_RUNTIME_SMOKE_OK label=original player=325 codec=h264 audio=aac resolution=320x240 fps=25 duration=1.28 sample_rate=44100 channels=1`

Segundo smoke, depois da movimentação:
`PORTABLE_RUNTIME_SMOKE_OK label=moved player=348 codec=h264 audio=aac resolution=320x240 fps=25 duration=1.28 sample_rate=44100 channels=1`

Os dois percorreram o runtime congelado e validaram, conforme o harness existente: páginas do Monitor, persistência controlada, pipelines controlados de notícias/vídeos, automação, Extrator, Editor PDF, Editor de Vídeo, preview, play/pause, seek, FFmpeg, FFprobe, exportação, DPAPI, proxy, startup e wiring/evento de notificação.

## PORT-005

Causa do candidato anterior: o segundo smoke persistia o mesmo `news.db` e reapresentava uma notícia com a mesma identidade lógica. A deduplicação correta não produzia `newCount`, mas o gate exigia nova notificação.

A primeira tentativa de correção variou somente a URL e falhou no teste de regressão porque `storyKey` é `source normalizada | título normalizado`.

Correção final: o harness varia deterministicamente **URL e título artificiais** por execução (`local`, `original`, `moved`), preservando `MARINHA` para matching. Nenhum código em `src/`, repository, deduplicação ou `AutomationService` foi alterado.

Teste de regressão: nova história notifica; a mesma história repetida não notifica; uma história logicamente distinta notifica. O run final passou integralmente.

Status: **PORT-005 RESOLVIDO**.

## Shutdown / órfãos / temporários

O segundo smoke chegou ao teardown final:
- shutdown = PASS
- processos órfãos = `0`
- temporários finais = PASS
- estado artificial removido = PASS

## Segurança do artefato

Gate final:
- `SEGREDOS_REAIS_ENCONTRADOS=0`
- `DADOS_PESSOAIS_NO_ZIP=0`

O ZIP também foi validado sem `.git`, `src`, `tests`, `.venv`/`venv` e sem banco/prefs/cookies/sessão pessoal inicial nos diretórios graváveis.

## Conclusão

**PORTABLE VALIDADO**
