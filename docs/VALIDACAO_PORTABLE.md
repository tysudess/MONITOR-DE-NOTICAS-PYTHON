# VALIDAÇÃO PORTABLE — PASSO 20

## Resultado atual

**PORTABLE NÃO VALIDADO — FALHA TÉCNICA**

A falha técnica pertence ao **gate de validação externa**, não a uma falha comprovada do motor de notificações. O candidato avaliado permanece o commit de código/artefato:

`186a28e4a5f53296178fd9d0ee74637a8a5149bf`

Run GitHub Actions:

`34768584764`

Nenhuma correção de código foi feita no Passo 20. Nenhum novo candidato foi criado.

## Run

- workflow: `Passo 17 - Windows Portable`
- branch: `migration/python-foundation`
- head SHA: `186a28e4a5f53296178fd9d0ee74637a8a5149bf`
- status: `completed`
- conclusion: `failure`
- run_started_at: `2026-09-13T16:26:33Z`
- updated_at: `2026-09-13T16:31:53Z`

O endpoint do run não forneceu um campo `completed_at` separado. O último job terminou em `2026-09-13T16:31:52Z`.

## Jobs

| Job | Runner | Status | Conclusion | Início | Fim |
|---|---|---|---|---|---|
| `build-windows-x64` | `GitHub Actions 1000000689` / `windows-latest` | completed | success | 16:26:36Z | 16:30:34Z |
| `validate-zip-without-repository` | `GitHub Actions 1000000690` / `windows-latest` | completed | failure | 16:30:37Z | 16:31:52Z |

A build e o segundo ambiente foram runners distintos.

## Build limpa

A etapa `Build clean portable` concluiu com sucesso.

Regressão antes do empacotamento:

- `148 passed`
- `0 failed`

O smoke local da pasta recém-construída também concluiu com `LOCAL_PORTABLE_SMOKE_OK`.

## Artefato do candidato 186a28

Nome do ZIP interno:

`MONITOR-DE-NOTICIAS-PYTHON-portable-windows-x64.zip`

- tamanho do ZIP interno: `651329759` bytes
- tamanho da pasta portable antes da compactação: `1262864276` bytes
- SHA-256 do ZIP interno: `5ebd57f312d3ce66b51b10b1abda8d92076a7971ad25aeb0bf0b23f78ee13cf2`
- `BUILD-SHA.txt`: `186a28e4a5f53296178fd9d0ee74637a8a5149bf`

O GitHub Actions encapsulou esse ZIP em seu próprio contêiner de artifact. O digest do contêiner do Actions (`adb365bc...`) NÃO é o hash do ZIP portable e não deve ser confundido com ele.

## Segundo runner

Ambiente externo:

- runner: `GitHub Actions 1000000690`
- Windows: Microsoft Windows Server 2025
- versão NT: `10.0.26100`
- arquitetura: AMD64
- imagem: `windows-2025-vs2026`
- development checkout: ausente
- FFmpeg global no PATH: ausente
- FFprobe global no PATH: ausente
- somente o artefato portable foi transferido para o job

O segundo runner recalculou:

`SHA256_RUNNER=5ebd57f312d3ce66b51b10b1abda8d92076a7971ad25aeb0bf0b23f78ee13cf2`

Resultado: **HASHES IDÊNTICOS**.

## Reextração e primeira execução

O ZIP foi extraído do zero para diretório novo contendo espaços e acentos:

`Edição Portable Monitor de Notícias\MonitorDeNoticias`

A estrutura obrigatória foi localizada. O EXE iniciou com CWD externo. Bancos e log foram criados na raiz portable. Não houve falha de `qwindows.dll`, plugin Qt, DLL estrutural ou traceback na primeira inicialização.

## Primeiro smoke externo

Resultado: **PASSOU**.

Confirmado pelo payload e pelo gate:

- navegação por todas as páginas: PASS
- banco/persistência: PASS
- notícias: PASS
- vídeos: PASS
- automação: PASS
- Extrator: PASS
- PDF: PASS
- Editor de Vídeo: PASS
- preview QMediaPlayer: PASS (`325 ms`)
- pause: PASS
- seek: PASS (`500`, `1000`, `1500` ms)
- FFmpeg empacotado: PASS
- FFprobe empacotado: PASS
- exportação: PASS
- codec vídeo: H.264
- codec áudio: AAC
- resolução: 320x240
- fps: 25
- duração exportada: 1.28 s
- sample rate: 44100 Hz
- canais: 1
- Extrator controlado: PASS
- DPAPI/proxy/startup: PASS
- evento e wiring de notificação no primeiro smoke: PASS

## Reabertura e movimentação

Após o primeiro smoke, o Monitor abriu novamente com sucesso.

A pasta portable foi então movida para:

`Movido Portable Monitor\Monitor de Notícias Validado`

A abertura normal após a movimentação também passou.

Assim, antes da falha posterior, já estavam objetivamente comprovados:

- path com espaços: PASS
- path com acentos: PASS
- CWD diferente: PASS
- relocação da pasta portable: PASS
- reabertura: PASS

## Segundo smoke depois da movimentação

O segundo smoke avançou com sucesso por:

- PDF
- Editor de Vídeo
- preview
- play/pause
- seeks
- FFmpeg
- FFprobe
- exportação
- Extrator

O `PORT-004` **não reapareceu**. A limpeza se limitou a arquivos `*extractor_fixture*` em `Videos/`, não apagou resultados arbitrários e não alterou `ExtractorEngine`.

A falha ocorreu depois, no pipeline controlado de notícias:

`Evento de notícia nova não acionou callback de notificação.`

## PORT-005 — falha do gate

Status: **ABERTO / NÃO CORRIGIDO NO PASSO 20**.

Classificação: **FALHA DO GATE**.

Causa comprovada:

1. o smoke usa `root/temp/pipeline-smoke/news.db`;
2. o primeiro smoke persiste a notícia artificial de link fixo `https://example.test/portable-noticia`;
3. a pasta inteira, inclusive esse banco, é movida para o segundo caminho;
4. o segundo smoke reutiliza o mesmo banco e o mesmo link artificial;
5. `AutomationService` só chama `notify()` quando `newCount + newDemandCount > 0`;
6. no segundo smoke a notícia já existe, logo não é nova e o comportamento correto é não gerar nova notificação;
7. o gate recria `notification_events=[]` e exige que a lista fique não vazia, tornando a asserção não idempotente.

Portanto não há evidência de defeito no motor de notificação. Há evidência de defeito na preparação/asserção do segundo smoke.

Nenhuma correção foi aplicada, pois o Passo 20 determina parar diante de falha técnica real e deixar qualquer correção para um novo candidato em passo posterior.

## PORT-001 a PORT-004

| ID | Resultado no candidato 186a28 |
|---|---|
| PORT-001 | CORRIGIDO; Extrator assíncrono concluiu no runtime congelado |
| PORT-002 | CORRIGIDO; workflow foi disparado e refez o portable para alterações relevantes |
| PORT-003 | CORRIGIDO; PowerShell do segundo runner executou normalmente |
| PORT-004 | CORRIGIDO; segundo smoke ultrapassou o Extrator sem reutilização da fixture |
| PORT-005 | ABERTO; gate de notificação do segundo smoke não é idempotente |

## Logs

As mensagens DXVA2 observadas são warnings de aceleração de hardware no runner sem sessão gráfica adequada. Elas não foram tratadas como falha porque o QMediaPlayer comprovadamente reproduziu, avançou posição e realizou seeks.

Erro funcional determinante do run:

`Smoke interno falhou: Evento de notícia nova não acionou callback de notificação.`

Não foi observado traceback estrutural anterior a esse gate.

## Shutdown e órfãos

O segundo smoke abortou no gate de notícias antes de chegar ao teardown final. Portanto:

- shutdown final após o segundo smoke: **NÃO EXECUTADO APÓS A FALHA**
- verificação final de processos órfãos: **NÃO EXECUTADA APÓS A FALHA**

Não é legítimo promover esses itens como PASS com base apenas no primeiro smoke ou na limpeza automática do runner.

## Segredos / estado pessoal

Antes da execução no segundo runner, o ZIP passou pela verificação de ausência de estado inicial/sensível e foi produzido depois da limpeza do estado artificial de build.

O marcador final pós-segundo-smoke `SEGREDOS_REAIS_ENCONTRADOS=0` não foi alcançado porque o gate abortou antes do fim. Portanto o registro conservador é:

- segredos/credenciais pessoais encontrados na inspeção inicial do ZIP: 0
- marcador final pós-smoke: NÃO EXECUTADO

## MIGs portable/distribuição

`MIG-079`–`MIG-083` não são promovidos por associação. Há evidência objetiva de build, ZIP, binários, `BUILD-SHA` e hash, mas o ciclo externo obrigatório não terminou. Permanecem no estado documental anterior até nova validação integral.

## Conclusão

**PORTABLE NÃO VALIDADO — FALHA TÉCNICA**
