# RELEASE READINESS — PASSO 15

## Referência congelada

- Versão Kotlin de referência: release V8 `v8-extrator-v301-preview`, Build SHA `df1701ba5427a04954093e8ebed63f26abb2b2b7` + transformações do workflow `release-v8-extractor-tab-portable.yml`.
- Repositório Kotlin: `tysudess/noticias-monitor`.
- Commit Kotlin: `df1701ba5427a04954093e8ebed63f26abb2b2b7`.
- Data Kotlin: `2026-09-12T20:11:33Z`.
- Versão Python: migração PySide6, contrato visual v4.0.2; ainda sem release/tag Python.
- Repositório Python: `tysudess/MONITOR-DE-NOTICAS-PYTHON`.
- Branch: `migration/python-foundation`.
- Commit Python congelado no início do gate: `fb6773a534853645253c8641f2dace631333a8f8`.
- Data do commit Python congelado: `2026-09-13T01:10:37Z`.
- Data do gate: `2026-09-13`.

Regra: `OK` somente com evidência objetiva. Lacunas ficam como `FALHA`, `BLOQUEADO` ou `NÃO APLICÁVEL`. **NÃO DETERMINADO PELO CÓDIGO ANALISADO.** quando a fonte não permite afirmar o comportamento.

## Checklist final

| Item | Resultado | Evidência / observação |
|---|---|---|
| inicialização | OK | `python run.py` real iniciado em Ubuntu e Windows; bug de ordem de sinal do Extrator foi encontrado e corrigido |
| banco | OK | NewsDb/VideoDb criados na primeira execução; equivalência SQLite e persistência cobertas |
| repositories | OK | NewsRepository/VideoRepository no composition root e E2E controlado |
| matching | OK | golden/equivalence tests; casos positivos, negativos, acento/case e políticas de vídeo |
| notícias | OK | UI/runtime→collector fixture→matching→repository→SQLite→UI; smoke live do Passo 14 encontrou/persistiu 22 |
| vídeos | OK | UI/runtime→collector fixture→matching→repository→SQLite→UI; smoke live do Passo 14 coletou 15 itens |
| demandas | OK | criar/remover/persistir/buscar; edição dedicada é NÃO APLICÁVEL ao Dashboard V5 ativo porque não existe ação `Editar` no baseline |
| termos | OK | termos de notícias e VideoTermStore independentes; persistência após reabertura coberta |
| fontes | OK | seleção real chega aos runners; seleção vazia de vídeo não coleta nenhuma fonte |
| histórico | OK | leitura/limpeza SQLite e histórico portable do Extrator cobertos |
| coletores | OK | coletores têm testes de parsing/timeout/retry/isolamento; disponibilidade externa é separada da lógica |
| AutomationService | OK | scheduler real com relógio controlado, runners/repositories/SQLite reais |
| retry | OK | onde existe no Kotlin foi preservado; Jarvis retry exato coberto; AutomationService não inventa retry próprio |
| timeout | OK | timeouts dos collectors/subprocessos auditados e testes de contratos presentes; não houve execução live de todos os sites |
| cancelamento | OK | cancelamento de busca real testado; DB permanece consistente; Extrator tem cancelamento do processo ativo |
| proxy | OK | configuração injetada em HttpClient e UI testada; teste de proxy externo autenticado não foi realizado |
| credenciais | OK | DPAPI CurrentUser real e compatibilidade .NET passaram no Windows; campo de senha mascarado; não há persistência plain text comprovada |
| startup | OK | Registry real passou no Windows e o teste restaura estado; nenhuma entrada de teste deliberada foi deixada |
| notificações | EM TESTE | wiring tray/notifier existe; evento visual real de notificação Windows não foi observado por humano neste gate |
| UI | OK | MainWindow real, navegação e entry point completo iniciaram; validação visual humana completa não foi realizada |
| extrator | BLOQUEADO | workspace abre; init corrigido. Login interno Globoplay (`MIG-050`) permanece sem helper comprovado; lifecycle de QThreads/helper no shutdown permanece bloqueador alto |
| PDF | OK | motor e workspace têm testes de import/crop/reorder/undo/capa/vector/raster; rotação/flip visual dedicada permanece não comprovada (`MIG-061`) |
| Editor de Vídeo | BLOQUEADO | motor ativo e contratos cobertos, mas media smoke real não pôde rodar porque o runner Windows não possui FFmpeg/FFprobe; janela top-level no mesmo processo não tem cleanup explícito no exit principal |
| FFmpeg | BLOQUEADO | comandos foram auditados; os binários exatos ainda pertencem à futura montagem e não foram executados neste gate |
| FFprobe | BLOQUEADO | contrato/parsing testado, porém binário real não disponível no runner deste gate |
| paths | OK | entry point Windows passou em `Teste Edição Monitor` e CWD externo; Ubuntu também passou em CWD externo |
| temporários | EM TESTE | rollback/cleanup de vários módulos coberto; cleanup total em fechamento durante ferramenta ativa não está provado |
| shutdown | BLOQUEADO | MainWindow fecha controller/tray, porém não coordena explicitamente QThreads do Extrator nem janelas top-level do editor de vídeo |
| suite | OK | Windows 141/141; Ubuntu 138 pass + 3 skips exclusivamente Windows; 0 xfail |
| end-to-end | BLOQUEADO | pipelines centrais de notícias/vídeos/automação estão comprovados, mas ferramentas integradas ainda têm bloqueadores altos de lifecycle/binários reais |

## Bloqueadores recebidos do Passo 14

| ID | MIG | Componente | Problema | Comportamento Kotlin | Comportamento Python | Causa | Correção necessária | Teste | Resultado |
|---|---|---|---|---|---|---|---|---|---|
| B14-01 | MIG-050 | Extrator / Globoplay | Login interno dependente de helper | `GloboplayLoginWindow` espera helper interno | `ExtractorPage` espera `data/extractor/runtime/GloboplayLoginHelper.exe` | workflow V8 válido não comprova construção/cópia do helper | obter evidência do artefato/log ou reproduzir exatamente a cadeia comprovada | auditoria de source/workflow | BLOQUEADO |
| B14-02 | MIG-079–083 | Build | portable ainda não executado | release original monta binários/build/hash | propositalmente ainda não executado | fora do escopo até o próximo passo | executar somente quando gate estiver liberado | NÃO APLICÁVEL neste passo | PENDENTE |
| B14-03 | MIG-114 | Notícias/UI | consumo do resolver Google News não comprovado | resolver existe como componente, mas Dashboard V5 não mostrou chamada direta | resolver Python existe, UI usa link armazenado | fluxo ativo não comprovado | não inventar wiring; obter evidência | auditoria estática | PENDENTE, não classificado como bloqueador alto do core |

## Novos achados do Passo 15

| ID | MIG | Componente | Problema | Severidade | Correção / decisão | Status |
|---|---|---|---|---|---|---|
| B15-01 | MIG-106 | Extrator UI | `_quality_changed()` podia disparar antes de `cancel_button` existir e derrubava `run.py` | CRÍTICO | guard de inicialização com `getattr`; sem mudança de motor | CORRIGIDO |
| B15-02 | MIG-116 | Lifecycle ferramentas | saída principal não coordena QThreads do Extrator, possível helper Globoplay ativo e janelas top-level do Editor de Vídeo no mesmo processo | ALTO | não forçar encerramento de thread Python nem inventar lifecycle; precisa solução equivalente e teste de fechamento durante operação | BLOQUEADO |
| B15-03 | MIG-070/071/072/074/075/076 | Mídia real | FFmpeg/FFprobe não estão no PATH do runner Windows e não foram empacotados neste passo | ALTO para liberação | validar com os cinco binários exatos da montagem aprovada antes do portable | BLOQUEADO PARA O GATE |

## MIG-116 — novo ID permanente

**MIG-116 — Lifecycle/Shutdown das ferramentas integradas — BLOQUEADO.**

Escopo objetivo: ao escolher `Sair` com operação controlada ativa, coordenar encerramento/cancelamento de workers QThread do Extrator, processos auxiliares conhecidos e janelas top-level do Editor de Vídeo sem deixar processo órfão e sem corromper estado. O código atual não fornece prova suficiente desse cleanup. Não foi aplicada terminação forçada inventada.

Os IDs `MIG-001` a `MIG-116` passam a ser permanentes. Não renumerar nem reutilizar.

## Testes skip

| Teste | Motivo | Módulo | Crítico para portable? | Pode executar agora? | Resultado Windows |
|---|---|---|---|---|---|
| DPAPI real | requer Windows | segurança | sim | sim, no runner Windows | PASS |
| compatibilidade .NET DPAPI | requer Windows/.NET | segurança | sim | sim, no runner Windows | PASS |
| Registry real | requer Windows | startup | sim | sim, no runner Windows | PASS |

No Ubuntu os três ficam `SKIP` por plataforma. No Windows nenhum deles é skip. Nenhum skip crítico ficou sem execução na plataforma alvo.

## XFAIL

Nenhuma declaração `xfail` foi encontrada. `XFAIL=0`, `XPASS=0`.

## Suíte completa

### Windows — plataforma alvo

- TOTAL: **141**
- PASS: **141**
- FAIL: **0**
- ERROR: **0**
- SKIP: **0**
- XFAIL: **0**
- XPASS: **0**
- DURAÇÃO pytest: **10.77 s** no run de readiness de `c6754c...`.

### Ubuntu — regressão cruzada

- TOTAL: **141**
- PASS: **138**
- FAIL: **0**
- ERROR: **0**
- SKIP: **3**, todos Windows-only e executados com sucesso no Windows
- XFAIL: **0**
- XPASS: **0**
- DURAÇÃO pytest: **3.22 s**.

## Entry point / primeira execução / paths

O gate executou o `run.py` real, não módulos isolados. Após corrigir B15-01:

- Windows: iniciou a partir de CWD externo em uma cópia cujo caminho contém espaço e acento: `Teste Edição Monitor`;
- Ubuntu: iniciou a partir de CWD externo;
- `data/news.db`, `data/videos.db`, `logs/monitor-noticias.log` e `resources/monitor-icon.svg` foram resolvidos/criados na raiz da aplicação;
- nenhuma ocorrência de caminho absoluto de desenvolvedor, `.venv`, `site-packages` ou usuário específico foi encontrada em `src/` + `run.py` pela busca do gate.

## Persistência / reabertura

Há testes de persistência para SharedPreferences, termos, VideoTermStore, SQLite, capas/configurações e histórico. `VideoTermStore` foi explicitamente reaberto com nova instância de `SharedPreferences` e manteve o termo salvo. Não foi realizada sessão humana de fechar e reabrir cada tela; onde isso for necessário visualmente o MIG individual permanece `EM TESTE`.

## Placeholders / `pass`

A busca global encontrou ocorrências de `pass`, mas nenhuma delas representa funcionalidade normal deliberadamente omitida que deveria ser implementada para equivalência. Classificação:

- classes de exceção vazias (`DPAPI`, `AutomationCancelled`, erro do Extrator/PDF): **INOFENSIVA**;
- tolerância de parse/config/time inválidos, fechamento de DB e rollback/cleanup: **INOFENSIVA**;
- `MainWindow._state_changed`: no-op porque o timer de 250 ms sincroniza/atualiza UI; **INOFENSIVA no contrato atual**;
- `PdfEditorPage.refresh`: workspace mantém estado próprio; **INOFENSIVA**;
- placeholders visuais do Editor de Vídeo já documentados em `MIG-077`: **DELIBERADOS E EQUIVALENTES AO MOTOR ATIVO**.

O resíduo legado de `pages.py` que mencionava `MIG-024 BLOQUEADO` não é a tela de produção: a MainWindow usa `runtime_pages.TermsPage`. Classificação: **resíduo inofensivo**, não wiring ativo.

## Internet / disponibilidade externa

- lógica: validada com fixtures/golden data;
- integração: repositories/runners/SQLite/UI reais com bordas externas controladas;
- disponibilidade externa: smoke live do Passo 14 validou Google News e coletor g1 no momento daquela execução;
- mudança de site externo não é convertida automaticamente em falha de migração.

## Recursos obrigatórios da futura build

- `resources/monitor-icon.svg`;
- `resources/pdf-default-cover.b64`;
- Python 3.12 runtime congelado;
- PySide6/Qt 6.9.1, Shiboken e plugins Qt necessários, incluindo plataforma e QtMultimedia;
- PDFium fornecido por `pypdfium2`;
- Pillow e bibliotecas Python listadas abaixo;
- `bin/yt-dlp.exe` (nightly conforme workflow original);
- `bin/yt-dlp-stable.exe`;
- `bin/deno.exe` x64;
- `bin/ffmpeg.exe`;
- `bin/ffprobe.exe`;
- certificados CA do stack HTTP quando aplicável (`certifi`);
- integração Windows nativa: DPAPI e Registry, fornecidas pelo sistema operacional;
- `GloboplayLoginHelper.exe` somente se sua presença/cadeia válida for comprovada; no estado atual permanece `MIG-050 BLOQUEADO`.

Bancos não precisam ser pré-populados para primeira execução: são criados pelo aplicativo.

## Dependências do futuro portable

| Nome | Versão/Origem auditada | Finalidade | Precisa ser empacotada? | Licença / nota | Testada no gate? |
|---|---|---|---|---|---|
| Python | 3.12.x | runtime | SIM | PSF | SIM, 3.12 nos runners |
| PySide6 | 6.9.1 | UI + QtMultimedia | SIM | Qt for Python; distribuição conforme termos Qt/LGPL/GPL/comercial aplicáveis | SIM, import/UI; mídia real BLOQUEADA |
| shiboken6 | 6.9.1 | binding support | SIM | termos Qt for Python | SIM indiretamente |
| requests | >=2.32,<3 | HTTP | SIM | Apache-2.0 | SIM |
| beautifulsoup4 | >=4.12,<5 | HTML parsing | SIM | MIT | SIM |
| lxml | >=5,<7 | parsing | SIM | BSD-style | SIM |
| pypdf | 6.18.0 | PDF vetorial | SIM | BSD-3-Clause | SIM |
| pypdfium2 | 5.13.0 | render PDF/PDFium | SIM | wrapper BSD-3-Clause; PDFium/third-party notices aplicáveis | SIM |
| Pillow | 12.3.0 | imagens/raster | SIM | HPND | SIM |
| certifi | resolução atual do bundle | CA HTTP | SIM quando usado pelo requests | MPL-2.0 | SIM indiretamente |
| urllib3/charset-normalizer/idna | transitivas do requests | HTTP | SIM | licenças próprias; inventário final obrigatório no build | SIM indiretamente |
| yt-dlp nightly | `latest` no workflow original | downloads/probe | SIM | Unlicense no projeto yt-dlp | NÃO com binário exato neste gate |
| yt-dlp stable | `latest` no workflow original | fallback | SIM | Unlicense | NÃO com binário exato neste gate |
| Deno x64 | `latest` no workflow original | JS runtime yt-dlp | SIM | MIT | NÃO com binário exato neste gate |
| FFmpeg | distribuição escolhida pelo workflow original | mídia | SIM | build GPL conforme fonte selecionada; guardar notices/configuração | NÃO com binário exato neste gate |
| FFprobe | mesmo pacote FFmpeg | probe | SIM | mesma licença/build FFmpeg | NÃO com binário exato neste gate |
| Qt plugins/backends | 6.9.1 via PySide6 | plataforma/multimídia | SIM | termos Qt aplicáveis | PARCIAL |
| DPAPI/Registry | Windows | segurança/startup | NÃO, API do SO | Windows | SIM |

Versões transitivas exatas devem ser congeladas no passo de build. Não inventar um lock diferente antes disso.

## DLLs e backends

A build futura deve carregar as DLLs Qt/PySide6 e plugins realmente usados por `QApplication`, `QSystemTrayIcon`, `QMediaPlayer`, `QAudioOutput` e `QVideoWidget`. O backend multimídia nativo efetivamente escolhido no Windows é **NÃO DETERMINADO PELO CÓDIGO ANALISADO.** e deve ser identificado durante a validação da build, não adivinhado agora.

## Tamanho estimado

O ZIP Kotlin aprovado tinha `794,420,356` bytes. Como a futura build Python deverá carregar PySide6/Qt, runtime Python, PDFium e os cinco binários externos, a ordem de grandeza esperada é aproximadamente **0,8–1,0 GB compactado** e possivelmente **1–1,4 GB descompactado**. É apenas estimativa técnica; o tamanho real é **NÃO DETERMINADO PELO CÓDIGO ANALISADO.** até o build.

## Antivírus / falso positivo

Componentes com maior probabilidade de heurística:

- executável congelado/PyInstaller futuro;
- `yt-dlp.exe` e atualização/substituição do próprio binário;
- FFmpeg/FFprobe;
- Deno;
- criação/terminação de subprocessos ocultos;
- `taskkill /T /F` no helper de processo;
- chamadas WinAPI/DPAPI e escrita em `HKCU\\...\\Run`.

Nenhum comportamento foi alterado neste passo para reduzir falso positivo.

## Matriz final de bloqueadores

| ID | MIG | Módulo | Bloqueador | Severidade | Correção | Status |
|---|---|---|---|---|---|---|
| B15-02 | MIG-116 | lifecycle | shutdown não prova cleanup de QThreads/helper/janelas top-level | ALTO | definir cleanup equivalente + teste fechar-durante-operação + ausência de órfãos | BLOQUEADO |
| B14-01 | MIG-050 | Extrator/Globoplay | helper de login interno não comprovado na release válida | ALTO | comprovar helper no artefato/log ou migrar exatamente cadeia comprovada | BLOQUEADO |
| B15-03 | MIG-070/071/072/074/075/076 | Editor de Vídeo | preview/export/probe real não executados com os binários exatos que irão no pacote | ALTO | validar com binários exatos antes de build portable | BLOQUEADO PARA LIBERAÇÃO |
| P15-01 | MIG-079–083 | build | build/portable/hash ainda não executados por regra do Passo 15 | MÉDIO | executar somente depois de novo gate liberado | PENDENTE |
| P15-02 | MIG-114 | notícias/UI | consumo do resolver não comprovado | BAIXO | obter evidência; não inventar | PENDENTE |

## Decisão do gate

**NÃO APTO PARA PORTABLE**

Motivo: apesar de o entry point, pipelines centrais, bancos, matching, automation, segurança Windows e suíte determinística estarem saudáveis, ainda existem bloqueadores **ALTOS**: `MIG-050`, `MIG-116` e validação real de mídia com os binários exatos do futuro pacote. Pelo critério do Passo 15, a existência de qualquer bloqueador CRÍTICO ou ALTO impede a liberação.

Nenhum portable, instalador, merge ou release foi criado neste passo.
