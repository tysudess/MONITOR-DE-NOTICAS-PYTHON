# RELEASE READINESS — PASSO 16

## Referência congelada

- Repositório Kotlin: `tysudess/noticias-monitor`
- Commit Kotlin/fonte da verdade: `df1701ba5427a04954093e8ebed63f26abb2b2b7` + transformações comprovadas do workflow V8.
- Repositório Python: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- Branch: `migration/python-foundation`
- Commit Python no início do Passo 16: `5a4fd44f4fc69ee22e82f1cec283d62366d99a48`
- Commit de código submetido ao gate final do Passo 16: `c8a53b600faa49105937b194dc74455c0eb13d3a`
- Data do gate: `2026-09-13`

Regra: `OK` somente com evidência objetiva. Quando algo não é comprovado: **NÃO DETERMINADO PELO CÓDIGO ANALISADO.**

## Checklist após eliminação dos bloqueadores altos

| Item | Resultado | Evidência |
|---|---|---|
| inicialização | OK | `run.py` real iniciou em Windows e Ubuntu |
| banco | OK | NewsDb/VideoDb, migrations, persistência e transações cobertas |
| repositories | OK | NewsRepository/VideoRepository no composition root e E2E controlado |
| matching | OK | equivalence/golden tests preservados |
| notícias | OK | UI/runtime → collector controlado → matching → repository → SQLite → UI; smoke live anterior validou fonte real |
| vídeos | OK | pipeline real de runtime/repository/SQLite/UI preservado; smoke live anterior validou coletor real |
| demandas | OK | criar/remover/persistir/buscar; edição dedicada é NÃO APLICÁVEL ao Dashboard V5 ativo |
| termos | OK | termos de notícias e VideoTermStore persistem e afetam matching |
| fontes | OK | seleção ativa/desativada chega ao runner; seleção vazia de vídeo não coleta |
| histórico | OK | leitura/limpeza e histórico portable cobertos |
| coletores | OK | lógica/isolamento/timeout/retry cobertos; disponibilidade externa separada da equivalência |
| AutomationService | OK | relógio controlado → runner → repository → SQLite → estado/UI |
| retry | OK | sem camada de retry inventada; retries existentes preservados |
| timeout | OK | contratos dos collectors/subprocessos preservados |
| cancelamento | OK | busca cancela sem persistir resultado tardio; Extrator destrói processo ativo |
| proxy | OK | configuração real injetada no HttpClient; credencial não vai para log |
| credenciais | OK | DPAPI CurrentUser e compatibilidade .NET passam no Windows |
| startup | OK | Registry real passa no Windows e teste restaura estado |
| notificações | EM TESTE | wiring preservado; observação humana de toast/tray não é necessária para eliminar os bloqueadores altos do Passo 15 |
| UI | OK | MainWindow/navegação/entry point real passam |
| extrator | OK | `MIG-050` resolvido: helper oficial idêntico ao Kotlin, resource→runtime e chamada/cookies testados; shutdown coordenado |
| PDF | OK | funções principais continuam verdes; `MIG-061` continua PENDENTE e não foi promovido por associação |
| Editor de Vídeo | OK | janela integrada, preview, play/pause, seek, áudio, probe e exportação real validados |
| FFmpeg | OK | ferramenta preparada pela mesma origem/família do baseline para o gate; comando de produção executado com sucesso |
| FFprobe | OK | probe real e validação final do arquivo exportado executados |
| paths | OK | Windows em `Teste Edição Monitor`, com espaço/acento e CWD externo; Ubuntu CWD externo |
| temporários | OK para os bloqueadores do gate | media smoke conclui e remove diretório temporário após liberar source do player |
| shutdown | OK | MainWindow chama shutdown do Extrator e Editor antes do controller; helper real controlado é encerrado; source do QMediaPlayer é liberada |
| suite | OK | Windows 147/147; Ubuntu 144 pass + 3 skips exclusivamente Windows |
| end-to-end | OK para liberação do próximo passo de build | pipelines centrais + ferramentas bloqueadoras revalidados |

## Bloqueadores do Passo 15 e resolução

| ID | MIG | Severidade original | Problema | Causa raiz | Correção | Evidência final | Status |
|---|---|---|---|---|---|---|---|
| B14-01 | MIG-050 | ALTO | login interno Globoplay sem cadeia comprovada | Python procurava diretamente `data/extractor/runtime/GloboplayLoginHelper.exe` e não reproduzia a extração do resource Kotlin | `resolve_bundled_helper()` reproduz resource→runtime; helper source migrado byte a byte; UI chama helper e salva cookies pelo store | blob do helper é o mesmo `de8839c...`; testes de materialização, sem fallback externo e integração da UI | RESOLVIDO |
| B15-02 | MIG-116 | ALTO | ferramentas não participavam do `Sair` | arquitetura Python integrou ferramentas no mesmo processo enquanto a release Kotlin encerrava o editor separado | shutdown coordenado; Extrator cancela subprocessos e espera QThreads; helper é rastreado; editor para player, limpa source e fecha/delete top-level; MainWindow só encerra depois | regressões de shutdown + processo filho real + gate Windows | RESOLVIDO |
| B15-03 | MIG-070/071/072/074/075/076 | ALTO | mídia real não havia sido executada | ambiente do Passo 15 não tinha FFmpeg/FFprobe disponíveis | gate prepara FFmpeg/FFprobe a partir das fontes equivalentes do workflow original, sem empacotar; executa motor Python inalterado | `MEDIA SMOKE OK player_position=301ms seek=1000ms codec=h264 duration=2.000s resolution=320x240 fps=25/1 audio=aac sample_rate=44100 channels=1` | RESOLVIDO |

## Suíte final

### Windows — plataforma alvo

- TOTAL: **147**
- PASS: **147**
- FAIL: **0**
- ERROR: **0**
- SKIP: **0**
- XFAIL: **0**
- XPASS: **0**
- DURAÇÃO: **15.07 s** no workflow readiness do commit `c8a53b...`.

### Ubuntu — regressão cruzada

- TOTAL: **147**
- PASS: **144**
- FAIL: **0**
- ERROR: **0**
- SKIP: **3** — DPAPI real, compatibilidade .NET DPAPI e Registry real; todos passam no Windows.
- XFAIL: **0**
- XPASS: **0**
- DURAÇÃO: **2.26 s**.

## Mídia real

O gate Windows preparou `ffmpeg.exe` e `ffprobe.exe` apenas no workspace de teste, usando a mesma cadeia de fontes prevista pelo workflow Kotlin (BtbN n9.0 com fallback Gyan). Isso **não é portable, instalador nem release**.

Resultado real:

```text
MEDIA SMOKE OK player_position=301ms seek=1000ms codec=h264 duration=2.000s resolution=320x240 fps=25/1 audio=aac sample_rate=44100 channels=1
```

O comando de exportação de produção não foi reescrito e permanece literalmente equivalente ao motor PySide6 distribuído pela release de referência.

## Globoplay interno

O baseline Kotlin contém `tools/globoplay-login-helper.py` e `GloboplayLoginWindow.kt`. O helper source migrado em Python possui o mesmo blob Git `de8839c232e1857bb7b04cd079a5e7eafb755453` da fonte Kotlin. A correção reproduz a etapa que faltava no Python: resource `/globoplay-login-helper/GloboplayLoginHelper.exe` → `data/extractor/runtime/GloboplayLoginHelper.exe` → processo com `--output` e `--profile-dir` → cookies Netscape → `GloboplaySessionStore` protegido.

A autenticação humana contra o site externo não é automatizada nem simulada como sucesso. O pipeline interno e a equivalência do helper foram comprovados. A geração/inclusão física do `.exe` continua responsabilidade da futura etapa de build, não um bloqueador de migração do source.

## Shutdown / processos

- QThread não é encerrada com `terminate()`.
- Operação do Extrator é cancelada pelo próprio motor/process tree.
- helper Globoplay rastreado é destruído no shutdown.
- teste inicia um processo filho real e comprova seu término.
- Editor de Vídeo usa `WA_DeleteOnClose`, `player.stop()` e `player.setSource(QUrl())` antes do fechamento.
- o primeiro smoke real detectou handle preso no arquivo; a regressão final prova que o diretório temporário é removido normalmente.
- nenhum `ffmpeg`, `ffprobe` ou auxiliar permaneceu órfão nos jobs concluídos.

## Placeholders / skips / xfail

Nenhum placeholder crítico pertencente ao fluxo normal foi encontrado. Os controles deliberadamente não funcionais do editor continuam conforme `MIG-077`; não foram convertidos em recursos inventados.

Os únicos três skips são condicionais a sistemas não-Windows e executam como PASS no Windows. `XFAIL=0`, `XPASS=0`.

## Matriz final de bloqueadores

| ID | MIG | Módulo | Severidade original | Status após Passo 16 |
|---|---|---|---|---|
| B14-01 | MIG-050 | Extrator/Globoplay | ALTO | RESOLVIDO |
| B15-02 | MIG-116 | Lifecycle/Shutdown | ALTO | RESOLVIDO |
| B15-03 | MIG-070/071/072/074/075/076 | Editor de Vídeo/Mídia | ALTO | RESOLVIDO |

Contagem objetiva do gate:

- BLOQUEADORES CRÍTICOS: **0**
- BLOQUEADORES ALTOS: **0**
- BLOQUEADORES MÉDIOS: **0**
- BLOQUEADORES BAIXOS: **0**

Pendências de build (`MIG-079`–`083`), `MIG-061`, `MIG-114` e MIGs ainda `EM TESTE` continuam rastreadas e **não foram falsamente promovidas**. Elas não eram bloqueadores críticos/altos da matriz do Passo 15.

## Decisão

**APTO PARA PORTABLE**

Isto significa somente que o source está liberado para uma futura etapa de criação/validação do portable. **Nenhum portable, instalador, release ou merge foi criado neste passo.**
