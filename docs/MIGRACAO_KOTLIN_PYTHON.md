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
- Passos 18–19: build/validação portable revelou e tratou `PORT-001` a `PORT-004`; candidato resultante `186a28e4a5f53296178fd9d0ee74637a8a5149bf`.
- Passo 20: run `34768584764` concluiu com build limpa aprovada e falha no segundo smoke externo por `PORT-005`, classificado como **FALHA DO GATE**; decisão `PORTABLE NÃO VALIDADO — FALHA TÉCNICA`.

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

## Estado preservado após Passo 16

O Passo 16 aprovou especificamente:

- `MIG-050` — helper/login interno Globoplay por escopo comprovado;
- `MIG-070` — FFprobe;
- `MIG-071` — preview;
- `MIG-072` — áudio/mute;
- `MIG-074` — seek;
- `MIG-075` — play/pause/avanço;
- `MIG-076` — exportação;
- `MIG-116` — lifecycle/shutdown das ferramentas integradas.

Nenhum desses estados é rebaixado pelo PORT-005, pois o bloqueador atual está no harness de repetição da validação portable, não nesses motores.

### Totais preservados do Passo 16

- Total: **116 MIGs**.
- `APROVADO`: **71**.
- `EM TESTE`: **37**.
- `PENDENTE`: **8**.
- `BLOQUEADO`: **0**.

## MIGs portable/distribuição

`MIG-079`–`MIG-083` tratam entry/build/workflow/binários/BUILD-SHA/hash no conjunto histórico.

O Passo 20 trouxe evidência positiva de:

- build PyInstaller onedir;
- binários próprios no bundle;
- `BUILD-SHA.txt` apontando para `186a28e4...`;
- ZIP criado;
- SHA-256 recalculado em segundo runner e idêntico;
- reextração e primeira execução externas;
- paths com espaços/acentos;
- movimentação do portable.

Entretanto o segundo smoke obrigatório não concluiu. Assim **nenhum MIG-079–MIG-083 é promovido por associação** neste passo. Eles permanecem no estado documental anterior até uma validação externa integralmente concluída.

## PORT-005

O primeiro smoke persiste a notícia artificial de link fixo em `temp/pipeline-smoke/news.db`. O segundo smoke reutiliza a mesma base e o mesmo link. Como a notícia já existe, o repository não a contabiliza como nova e `AutomationService` corretamente não chama notificação para `newCount=0`.

O gate recria `notification_events=[]` e exige evento não vazio, portanto a falha é do harness não idempotente.

Status: **ABERTO / NÃO CORRIGIDO NO PASSO 20**.

Não foi alterado o `AutomationService`, o repository de notícias nem qualquer regra de negócio.

## Editor de vídeo — motor preservado

O motor continua PySide6 `QMediaPlayer` + `QVideoWidget` + `QAudioOutput`. O comando de exportação preserva o contrato previamente aprovado com H.264/AAC, CRF 20, preset veryfast, `yuv420p`, áudio 160k e `+faststart`.

No segundo runner do Passo 20, preview avançou para 325 ms e seeks 500/1000/1500 ms passaram. A exportação foi validada pelo FFprobe do próprio portable.

## Regra permanente

Os IDs `MIG-001` a `MIG-116` são permanentes. Não renumerar, reutilizar ou substituir.

IDs `PORT-XXX` documentam bloqueadores da validação/empacotamento e não substituem MIGs funcionais.

## Repositório Kotlin

A branch original observada `work/v8-extrator-v301-tab` permanece em `e7b5d8eaac68bce6a9785e4da5b8ca5f83c34d2e`.

O repositório Kotlin não foi alterado no Passo 20.

## Decisão atual

O source continua com as equivalências já aprovadas, mas o candidato portable atual não completou o gate externo.

**PORTABLE NÃO VALIDADO — FALHA TÉCNICA**
