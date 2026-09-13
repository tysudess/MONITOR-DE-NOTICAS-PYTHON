# Migração Kotlin → Python

## Fonte da verdade

- Repositório original: `tysudess/noticias-monitor`
- Baseline Kotlin auditada: `df1701ba5427a04954093e8ebed63f26abb2b2b7` + transformações comprovadas do workflow V8.
- Repositório destino: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- Branch de integração: `migration/python-foundation`.

O comportamento comprovado é a fonte da verdade. Lacunas não são preenchidas por suposição. Quando algo não é comprovado: **NÃO DETERMINADO PELO CÓDIGO ANALISADO.**

## Estados permitidos

`PENDENTE`, `EM MIGRAÇÃO`, `EM TESTE`, `APROVADO`, `BLOQUEADO`.

`APROVADO` significa equivalência objetiva dentro do escopo explícito do MIG. Existência de código, aparência semelhante ou teste verde isolado não bastam.

## Histórico de gates

- Passo 13: auditoria estrutural, Python congelado em `6419ee336f3015bd466afa8c2ac4e961ca7c6ff3`.
- Passo 14: composition root/runtime real conectados; suíte de 141 testes e smokes live de notícias/vídeos.
- Passo 15: gate final encontrou bloqueadores altos `MIG-050`, `MIG-116` e validação real de mídia `MIG-070/071/072/074/075/076`; decisão `NÃO APTO PARA PORTABLE`.
- Passo 16: eliminou exclusivamente esses bloqueadores; gate de código `c8a53b600faa49105937b194dc74455c0eb13d3a` com Windows 147/147 e media smoke real; decisão `APTO PARA PORTABLE`.

Os documentos detalhados permanecem em:

- `docs/RELATORIO_PASSO_14.md`
- `docs/MIGRACAO_PASSO_15.md`
- `docs/RELATORIO_PASSO_15.md`
- `docs/MIGRACAO_PASSO_16.md`
- `docs/RELEASE_READINESS.md`

## Runtime real

```text
run.py
  → Application
  → AppContainer
     → AppPaths / SharedPreferences
     → NewsDb / VideoDb
     → ProxySettings / HTTP
     → collectors existentes
     → NewsRepository / VideoRepository
     → RuntimeNewsRunner / RuntimeVideoRunner
     → AutomationService
     → RuntimeUiController
  → MainWindow
     → páginas do Monitor
     → Extrator / PDF / Editor de Vídeo
```

O `AppContainer` apenas monta dependências; não contém scraping, matching ou SQL de negócio.

## Evidência central preservada

Passo 14 live smoke:

```text
LIVE NEWS OK found=22 new=22 stored=22
LIVE VIDEO COLLECTOR OK items=15
```

Passo 16 media smoke Windows:

```text
MEDIA SMOKE OK player_position=301ms seek=1000ms codec=h264 duration=2.000s resolution=320x240 fps=25/1 audio=aac sample_rate=44100 channels=1
```

Suíte alvo final do Passo 16:

- Windows: `147 passed`, `0 failed`, `0 error`, `0 skip`, `0 xfail`.
- Ubuntu: `144 passed`, `3 skipped` exclusivamente Windows; os três executam e passam no Windows.

## Checklist oficial — estado após Passo 16

A tabela completa dos `MIG-001`–`MIG-115` do Passo 14 permanece historicamente registrada nos commits/documentos anteriores. O Passo 15 acrescentou `MIG-116`. O estado atual é definido pelo checklist anterior **mais as alterações objetivamente aprovadas abaixo**; nenhum outro MIG foi promovido por associação.

| MIG | Módulo | Funcionalidade | Estado anterior | Estado após Passo 16 | Evidência |
|---|---|---|---|---|---|
| MIG-050 | Extrator | Login interno Globoplay | BLOQUEADO | APROVADO | helper source idêntico ao Kotlin (`de8839c...`), resource→runtime e integração processo/cookies testados |
| MIG-070 | Editor Vídeo | Probe FFprobe | EM TESTE | APROVADO | FFprobe real em MP4 controlado + probe do arquivo exportado |
| MIG-071 | Editor Vídeo | Preview | EM TESTE | APROVADO | QMediaPlayer real avançou posição em arquivo H.264 |
| MIG-072 | Editor Vídeo | Áudio/mute | EM TESTE | APROVADO | QAudioOutput real conectado, volume 0.85; AAC presente no probe |
| MIG-074 | Editor Vídeo | Seek global/local | EM TESTE | APROVADO | seek real para 1000 ms dentro da tolerância |
| MIG-075 | Editor Vídeo | Play/pause/avanço | EM TESTE | APROVADO | play avançou; pause confirmado pelo playback state |
| MIG-076 | Editor Vídeo | Exportação trecho | EM TESTE | APROVADO | comando FFmpeg de produção executado; H.264/AAC/320x240/25 fps/44.1 kHz confirmados |
| MIG-116 | Runtime/UI | Lifecycle/Shutdown das ferramentas integradas | BLOQUEADO | APROVADO | MainWindow coordena shutdown; processo auxiliar real terminado; player libera source/temporário |

### Totais atuais

- Total: **116 MIGs**.
- `APROVADO`: **71**.
- `EM TESTE`: **37**.
- `PENDENTE`: **8**.
- `BLOQUEADO`: **0**.

## MIG que permanecem deliberadamente sem promoção

- `MIG-002`: resolução de raiz portable — `PENDENTE`; o build portable ainda não ocorreu.
- `MIG-003`, `MIG-004` e demais itens anteriormente `EM TESTE` não são promovidos sem evidência específica.
- `MIG-061`: rotação/flip PDF — `PENDENTE`.
- `MIG-079`–`MIG-083`: build/portable/hash — `PENDENTE`; executar somente em passo futuro explicitamente autorizado.
- `MIG-114`: consumo do resolver Google News pela UI — `PENDENTE`; o baseline ativo não comprovou wiring, portanto não inventar.
- itens de UI/Windows/coletores ainda `EM TESTE` permanecem assim mesmo com o gate de bloqueadores liberado.

Essas pendências não eram bloqueadores CRÍTICOS/ALTOS registrados na matriz do Passo 15 e não foram usadas para falsificar a conclusão do Passo 16.

## MIG-050 — contrato final

O Kotlin `GloboplayLoginWindow` materializa `/globoplay-login-helper/GloboplayLoginHelper.exe` em `data/extractor/runtime/GloboplayLoginHelper.exe`, executa o helper com `--output` e `--profile-dir`, recebe cookies Netscape e os entrega ao store protegido.

O Python agora reproduz esse fluxo. `tools/globoplay-login-helper.py` no destino tem o mesmo blob Git `de8839c232e1857bb7b04cd079a5e7eafb755453` da fonte Kotlin. Não existe fallback para helper externo da máquina.

A geração física do `.exe` pertence à etapa futura de build. A autenticação humana contra o serviço externo não é simulada como sucesso.

## MIG-116 — contrato final

Ao escolher `Sair`:

1. `ExtractorPage.shutdown()` invalida callbacks, cancela o motor/process tree, encerra helper rastreado e espera QThreads; não usa `QThread.terminate()`.
2. se worker conhecido não encerrar com segurança, o Monitor recusa a saída.
3. `VideoEditorPage.shutdown()` para o player, limpa `QMediaPlayer.setSource(QUrl())`, fecha/delete a janela top-level.
4. somente depois `MainWindow` fecha controller/tray e aceita o encerramento.

Um teste com processo filho real comprova que o auxiliar rastreado termina. O media smoke final prova que o handle do arquivo é liberado e o diretório temporário pode ser removido.

## Editor de vídeo — motor preservado

Não houve troca de player nem reescrita do motor. O comando FFmpeg permanece equivalente ao `video_editor_pyside/main.py` do baseline:

```text
-y -i input -ss start -t duration -map 0:v:0 -map 0:a? -vf scale=trunc(iw/2)*2:trunc(ih/2)*2 -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart output
```

Os controles Extração/Compactação/Corte/Unir/Converter que não possuem motor no baseline ativo permanecem deliberadamente não funcionais conforme `MIG-077`. `MIG-078` continua preservando que IN/OUT manual é **NÃO DETERMINADO PELO CÓDIGO ANALISADO.**

## Gate de bloqueadores após Passo 16

- BLOQUEADORES CRÍTICOS: **0**
- BLOQUEADORES ALTOS: **0**
- BLOQUEADORES MÉDIOS: **0**
- BLOQUEADORES BAIXOS: **0**

A ausência de bloqueadores nessa matriz não transforma automaticamente todos os MIG pendentes/em teste em aprovados.

## Regra permanente

Os IDs `MIG-001` a `MIG-116` são permanentes. Não renumerar, reutilizar ou substituir. Novos achados recebem apenas IDs posteriores.

## Decisão do Passo 16

**APTO PARA PORTABLE**

A decisão significa pronto para iniciar uma futura etapa de build/validação portable quando houver instrução explícita. Não foi criado portable, instalador, release ou merge no Passo 16.
