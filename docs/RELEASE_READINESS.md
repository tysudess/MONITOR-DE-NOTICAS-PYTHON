# RELEASE READINESS — ESTADO ATUAL APÓS PASSO 20

## Decisão atual

**PORTABLE NÃO VALIDADO — FALHA TÉCNICA**

O source havia sido declarado `APTO PARA PORTABLE` no Passo 16, mas isso significava apenas aptidão para iniciar a etapa de empacotamento. O candidato portable de código `186a28e4a5f53296178fd9d0ee74637a8a5149bf` NÃO concluiu o gate externo obrigatório do Passo 20 e, portanto, não está liberado para release.

Não houve merge, GitHub Release, publicação do ZIP ou instalador.

## Candidato avaliado

- repositório: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- branch: `migration/python-foundation`
- commit do artefato: `186a28e4a5f53296178fd9d0ee74637a8a5149bf`
- run: `34768584764`
- conclusão do run: `failure`

Build `build-windows-x64`: PASS.

Validação externa `validate-zip-without-repository`: FAIL.

## Evidência do artefato

- ZIP: `MONITOR-DE-NOTICIAS-PYTHON-portable-windows-x64.zip`
- tamanho: `651329759` bytes
- pasta portable: `1262864276` bytes
- SHA-256 build: `5ebd57f312d3ce66b51b10b1abda8d92076a7971ad25aeb0bf0b23f78ee13cf2`
- SHA-256 segundo runner: `5ebd57f312d3ce66b51b10b1abda8d92076a7971ad25aeb0bf0b23f78ee13cf2`
- hashes idênticos: SIM

## Gates que passaram

Antes do bloqueio final, o segundo runner independente comprovou reextração, inicialização, primeiro smoke integral, reabertura, movimentação para path com espaço/acento e nova inicialização. O segundo smoke voltou a comprovar PDF, Editor de Vídeo, preview, seeks, FFmpeg, FFprobe, exportação e Extrator antes de falhar no gate de notícias.

O `PORT-004` não reapareceu.

## Bloqueador atual

`PORT-005 — FALHA DO GATE`.

O segundo smoke reutiliza `temp/pipeline-smoke/news.db` do primeiro smoke e o mesmo link artificial. Como a notícia já existe, o resultado corretamente possui zero notícias novas e `AutomationService` corretamente não chama o callback de notificação. O gate exige mesmo assim um novo callback e reprova.

Isso não é evidência de falha do motor de notificações. É uma asserção não idempotente do harness externo.

O Passo 20 não corrigiu esse gate, pois qualquer correção requer novo commit → nova build → novo ZIP → novo hash → nova validação em passo posterior.

## Shutdown / processos finais

O segundo smoke encerrou no PORT-005 antes do teardown. Assim, shutdown final e verificação final de órfãos do segundo smoke não podem ser marcados como aprovados neste candidato.

## Segurança

O ZIP passou pela limpeza de estado artificial antes da compactação e pela inspeção inicial no segundo runner. Não foi encontrado estado pessoal/sensível nessa inspeção. O marcador final pós-segundo-smoke não foi alcançado devido ao bloqueio.

## MIGs portable

`MIG-079`–`MIG-083` permanecem no estado documental anterior. A existência da build/ZIP/hash não substitui a validação externa completa e nenhum MIG é promovido por associação.

## Fonte Kotlin

A fonte funcional continua sendo o baseline comprovado `df1701ba5427a04954093e8ebed63f26abb2b2b7` + transformações aprovadas do workflow V8.

A branch original observada `work/v8-extrator-v301-tab` permanece em `e7b5d8eaac68bce6a9785e4da5b8ca5f83c34d2e` e não foi alterada neste passo.

## Histórico preservado

### Passo 16

O Passo 16 eliminou os bloqueadores altos de source e concluiu `APTO PARA PORTABLE`. Esse status histórico autorizava somente iniciar a futura build/validação; não significava que um ZIP já estava validado.

Evidência histórica do Passo 16:

- Windows: 147/147 testes
- Ubuntu: 144 pass + 3 skips exclusivamente Windows
- MIG-050 aprovado
- MIG-070/071/072/074/075/076 aprovados
- MIG-116 aprovado
- media smoke H.264/AAC/320x240/25 fps/44.1 kHz aprovado

### Passos 18–19

As tentativas de portable revelaram e trataram PORT-001 a PORT-004. O Passo 19 terminou com o candidato `186a28...` aguardando conclusão do run externo.

### Passo 20

O run concluiu e revelou PORT-005. O portable permanece não validado.

## Decisão

**NÃO LIBERADO PARA RELEASE.**

**PORTABLE NÃO VALIDADO — FALHA TÉCNICA**
