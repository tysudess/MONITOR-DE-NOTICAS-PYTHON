# Migração Kotlin → Python

## Fonte da verdade

- Repositório original: `tysudess/noticias-monitor`
- Repositório destino: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- Baseline funcional: Build SHA `df1701ba5427a04954093e8ebed63f26abb2b2b7` + transformações do workflow da release V8.
- Branch de migração: `migration/python-foundation`.

O comportamento comprovado na baseline é a fonte da verdade. Lacunas não são preenchidas por suposição. Quando algo não é comprovado: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**.

## Estados permitidos

`PENDENTE`, `EM MIGRAÇÃO`, `EM TESTE`, `APROVADO`, `BLOQUEADO`.

## Estado após o Passo 9

Os Passos 1 a 8 permanecem preservados. O Passo 9 adiciona a shell principal PySide6, navegação, páginas principais, integração visual de proxy/startup/automação, catálogo de notícias da tela Fontes, tray/close-to-tray e testes de GUI reais em Qt offscreen.

A UI não duplica business logic. O destino ainda declara que os business `NewsRepository` e `VideoRepository` completos não foram migrados; por isso a execução real de notícias/vídeos/demanda individual permanece bloqueada na composição padrão. Os testes injetam uma `AutomationPort` fake somente para provar o encadeamento da UI, não para fingir engine de produção.

Editor PDF, Extrator e Editor de Vídeo aparecem somente como pontos de navegação/placeholder. Seus motores continuam fora do Passo 9.

## MIG trabalhados no Passo 9

- `MIG-004` — tray/execução residente: avançou para `EM TESTE`.
- `MIG-039` — startup visual: permanece `EM TESTE` até executável final.
- `MIG-040` — proxy visual: permanece `EM TESTE` até composição completa do transporte/repositories.
- `MIG-091` — notificação/tray: permanece `EM TESTE` até desktop interativo final.
- `MIG-094` — MainWindow/sidebar/QStackedWidget/close-to-tray: `EM TESTE`.
- `MIG-095` — Dashboard/Início: `EM TESTE`.
- `MIG-096` — tela Notícias: `BLOQUEADO` pela ausência do business NewsRepository.
- `MIG-097` — tela Vídeos: `BLOQUEADO` pela ausência do business VideoRepository e por lacuna de período personalizado.
- `MIG-098` — tela Demandas: `BLOQUEADO` para busca individual pela ausência do NewsRepository; CRUD local está testado.
- `MIG-099` — tela Termos: `BLOQUEADO` por `MIG-024` para termos de vídeo.
- `MIG-100` — tela Fontes: `BLOQUEADO` para equivalência integral porque `VideoSourceCatalog` base não existe no destino; notícias/especializadas estão portadas.
- `MIG-101` — Histórico: `APROVADO`.
- `MIG-102` — Configurações: `EM TESTE`.
- `MIG-103` — Parar buscas/progresso/status: `EM TESTE` até jobs reais dos repositories.
- `MIG-104` — integração visual de PDF/Extrator/Editor de Vídeo sem motores: `APROVADO` para o escopo do Passo 9.
- `MIG-105` — testes Qt/navegação/equivalência em Windows+Ubuntu: `APROVADO`.

## Checklist oficial

| MIG | Módulo | Funcionalidade | Status |
|---|---|---|---|
| MIG-001 | Infraestrutura | Baseline congelada df1701 + workflow | PENDENTE |
| MIG-002 | Infraestrutura | Resolução de raiz portable | PENDENTE |
| MIG-003 | Infraestrutura | SharedPreferences portable | EM TESTE |
| MIG-004 | Infraestrutura | Tray e execução residente | EM TESTE |
| MIG-005 | Banco | Schema news | EM TESTE |
| MIG-006 | Banco | Migrations runtime news/demands | EM TESTE |
| MIG-007 | Banco | Tabela terms e seed | EM TESTE |
| MIG-008 | Banco | CRUD/status de demandas | EM TESTE |
| MIG-009 | Banco | Deduplicação/upsert lógico de notícias | EM TESTE |
| MIG-010 | Banco | Schema videos | EM TESTE |
| MIG-011 | Banco | Compatibilidade sem migration automática de videos | EM TESTE |
| MIG-012 | Banco | Remoção de listings genéricos | EM TESTE |
| MIG-013 | Banco | Reparo de matches armazenados | EM TESTE |
| MIG-014 | Notícias | Janela padrão de 24h | PENDENTE |
| MIG-015 | Notícias | Google News RSS | APROVADO |
| MIG-016 | Notícias | Planejamento de queries por termo/fonte | PENDENTE |
| MIG-017 | Notícias | Identidade storyKey | APROVADO |
| MIG-018 | Notícias | Preservação da primeira captura/NOVO | APROVADO |
| MIG-019 | Notícias | Matching subjectMatches | APROVADO |
| MIG-020 | Notícias | Matching fonte/veículo | APROVADO |
| MIG-021 | Notícias | Collector direto Últimas Notícias | APROVADO |
| MIG-022 | Notícias | Busca individual de demanda | PENDENTE |
| MIG-023 | Vídeos | Janela padrão de 24h | PENDENTE |
| MIG-024 | Vídeos | VideoTermStore independente | BLOQUEADO |
| MIG-025 | Vídeos | VideoMatchPolicy | APROVADO |
| MIG-026 | Vídeos | Planejamento source scan x term query | PENDENTE |
| MIG-027 | Vídeos | Globoplay Edições | EM TESTE |
| MIG-028 | Vídeos | Globoplay Trechos | EM TESTE |
| MIG-029 | Vídeos | Globoplay Jarvis global | APROVADO |
| MIG-030 | Vídeos | Coleta YouTube canal | APROVADO |
| MIG-031 | Vídeos | Enriquecimento de página direta | APROVADO |
| MIG-032 | Vídeos | Canonical URLs e merge | APROVADO |
| MIG-033 | Vídeos | Classificação de fonte instável | PENDENTE |
| MIG-034 | Vídeos | Fontes Desktop extras g1/Domingo Espetacular | APROVADO |
| MIG-035 | Automação | Loop residente | APROVADO |
| MIG-036 | Automação | Intervalo automático de notícias | APROVADO |
| MIG-037 | Automação | Intervalo automático de demandas | APROVADO |
| MIG-038 | Automação | Horários automáticos de vídeos | APROVADO |
| MIG-039 | Windows | Iniciar com Windows | EM TESTE |
| MIG-040 | Windows | Proxy geral | EM TESTE |
| MIG-041 | Windows | Migração proxy-7db→proxy-7dn | APROVADO |
| MIG-042 | Controle | Cancelamento de buscas | EM TESTE |
| MIG-043 | Extrator | Cinco presets de qualidade | PENDENTE |
| MIG-044 | Extrator | Download genérico yt-dlp | PENDENTE |
| MIG-045 | Extrator | Retry de compatibilidade | PENDENTE |
| MIG-046 | Extrator | Fallback HTML genérico | PENDENTE |
| MIG-047 | Extrator | Fluxo R7/Record | PENDENTE |
| MIG-048 | Extrator | Fluxo Globoplay multicaminho | PENDENTE |
| MIG-049 | Extrator | Sessão Globoplay protegida | PENDENTE |
| MIG-050 | Extrator | Login interno Globoplay | PENDENTE |
| MIG-051 | Extrator | Probe/download YouTube normal | PENDENTE |
| MIG-052 | Extrator | Snapshot YouTube Live HLS | PENDENTE |
| MIG-053 | Extrator | Remux/transcode Live FFmpeg | PENDENTE |
| MIG-054 | Extrator | Compatibilidade H.264 | PENDENTE |
| MIG-055 | Extrator | Cancelamento e invalidação de callbacks | PENDENTE |
| MIG-056 | Extrator | Histórico/qualidade portable | PENDENTE |
| MIG-057 | Extrator | Atualizador seguro yt-dlp | PENDENTE |
| MIG-058 | PDF | Importação PDF/imagens/drop | PENDENTE |
| MIG-059 | PDF | Página em branco | PENDENTE |
| MIG-060 | PDF | Crop normalizado | PENDENTE |
| MIG-061 | PDF | Rotação e flip | PENDENTE |
| MIG-062 | PDF | Reordenação drag-and-drop | PENDENTE |
| MIG-063 | PDF | Undo/redo 30 snapshots | PENDENTE |
| MIG-064 | PDF | Capa padrão/custom | PENDENTE |
| MIG-065 | PDF | Qualidade de exportação | PENDENTE |
| MIG-066 | PDF | Exportação vetorial inalterada | PENDENTE |
| MIG-067 | PDF | Exportação raster transformada | PENDENTE |
| MIG-068 | Editor Vídeo | Launcher processo PySide6 | PENDENTE |
| MIG-069 | Editor Vídeo | Importação múltiplos vídeos | PENDENTE |
| MIG-070 | Editor Vídeo | Probe FFprobe | PENDENTE |
| MIG-071 | Editor Vídeo | Preview QMediaPlayer/QVideoWidget | PENDENTE |
| MIG-072 | Editor Vídeo | QAudioOutput/mute | PENDENTE |
| MIG-073 | Editor Vídeo | Timeline visual multiclip | PENDENTE |
| MIG-074 | Editor Vídeo | Seek global↔local | PENDENTE |
| MIG-075 | Editor Vídeo | Play/pause e avanço entre clips | PENDENTE |
| MIG-076 | Editor Vídeo | Exportação de trecho | PENDENTE |
| MIG-077 | Editor Vídeo | Placeholders sem inventar recursos | PENDENTE |
| MIG-078 | Editor Vídeo | IN/OUT manual NÃO DETERMINADO | PENDENTE |
| MIG-079 | Build | Entrada Desktop original | PENDENTE |
| MIG-080 | Build | Transformações do workflow original | PENDENTE |
| MIG-081 | Build | PyInstaller onedir do editor | PENDENTE |
| MIG-082 | Build | Cinco binários portáteis | PENDENTE |
| MIG-083 | Build | BUILD-SHA e hash do ZIP | PENDENTE |
| MIG-084 | Vídeos | Priorização estável de candidatos Globoplay | APROVADO |
| MIG-085 | Vídeos | Filtros/exclusões puros de candidato direto | APROVADO |
| MIG-086 | Vídeos | Coletor HTML genérico de portal/busca | APROVADO |
| MIG-087 | Networking | Transporte HTTP compatível/injetável | APROVADO |
| MIG-088 | Automação | Orquestração Desktop e lanes | APROVADO |
| MIG-089 | Automação | Progresso/status/durações | APROVADO |
| MIG-090 | Windows/Segurança | DPAPI CurrentUser compatível | EM TESTE |
| MIG-091 | Windows | Adaptador de notificação pelo tray | EM TESTE |
| MIG-092 | Windows | Processo oculto/árvore de processo | EM TESTE |
| MIG-093 | Segurança | Senha proxy DPAPI e migração segura | EM TESTE |
| MIG-094 | UI | MainWindow, sidebar, stack, tray, close-to-tray | EM TESTE |
| MIG-095 | UI | Dashboard/Início e ações rápidas | EM TESTE |
| MIG-096 | UI | Notícias, filtros, períodos, progresso e ações | BLOQUEADO |
| MIG-097 | UI | Vídeos, filtros, progresso, instabilidades e ações | BLOQUEADO |
| MIG-098 | UI | Demandas, CRUD e ações | BLOQUEADO |
| MIG-099 | UI | Gestão visual de termos | BLOQUEADO |
| MIG-100 | UI | Fontes, catálogo, filtros e seleção | BLOQUEADO |
| MIG-101 | UI | Histórico notícias/vídeos e limpeza | APROVADO |
| MIG-102 | UI | Configurações proxy/startup/automação | EM TESTE |
| MIG-103 | UI | Parar buscas, progresso e status | EM TESTE |
| MIG-104 | UI | Pontos visuais PDF/Extrator/Editor Vídeo | APROVADO |
| MIG-105 | UI/Testes | Smoke, navegação e equivalência Qt | APROVADO |

## Inventário das telas ativas

| Tela | Origem Kotlin | Acesso | Dados/serviço | Estado Python |
|---|---|---|---|---|
| Início | `V5HomeScreen` | sidebar HOME | Controller/DB/automação | migrada, EM TESTE |
| Notícias | `V5NewsScreen` | sidebar NEWS | NewsRepository/Controller | widget migrado, engine BLOQUEADO |
| Vídeos | `V5VideosScreen` | sidebar VIDEOS | VideoRepository/Controller | widget migrado, engine BLOQUEADO |
| Demandas | `V5DemandsScreen` | sidebar DEMANDS | NewsDb/NewsRepository | CRUD migrado, busca individual BLOQUEADA |
| Fontes | `V5SourcesScreen` | sidebar SOURCES | SourceCatalog/DesktopVideoSources | notícias completas, vídeo parcial |
| Histórico | `V5HistoryScreen` | sidebar HISTORY | NewsDb/VideoDb | APROVADO |
| Termos | `V5TermsScreen` | sidebar TERMS | NewsDb/VideoTermStore | notícia funcional, vídeo BLOQUEADO |
| Parar buscas | `V5StopScreen` | sidebar STOP | Controller/AutomationService | EM TESTE |
| Configurações | `V5SettingsScreen` | sidebar SETTINGS | prefs/proxy/startup/automação | EM TESTE |
| Editor PDF | `PdfEditorScreenV2` | sidebar PDF_EDITOR | motor PDF | placeholder visual |
| Extrator | `ExtractorVideoScreen` | sidebar EXTRACTOR | motor extrator | placeholder visual |
| Editor Vídeo | build patch + `VideoEditorScreen` | sidebar VIDEO_EDITOR | PySide editor externo | placeholder visual |

## Hierarquia da janela

- Título: `Monitor de Notícias - Windows Portable v4.0.2`.
- Tamanho inicial: 1600×960.
- Sidebar: 258.
- Fechar: oculta para tray.
- Sair: fecha controller e encerra a janela.
- Timer de UI: 250 ms.
- Estado maximizado inicial: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**.
- Tamanho mínimo explícito: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**.
- Posição inicial explícita: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**.

## Menu e navegação

A ordem final é:

`Início → Notícias → Vídeos → Demandas → Fontes → Histórico → Termos → Parar buscas → Configurações → Editor de PDF → Extrator de Vídeos → Editor de Vídeo`.

A última seção é adicionada pelo script de integração da release, portanto não foi inferida apenas do arquivo estático.

## Dashboard

Foram migrados os indicadores e ações principais. Não foram inventados KPIs. O bloco meteorológico/decorativo do Compose não foi reproduzido e nenhum serviço de clima novo foi criado.

## Notícias

A UI possui busca, `Só demandas`, períodos Hoje/24h/7d/30d/personalizado, botão buscar, parar, progresso/status e ações Abrir/WhatsApp/Copiar.

A execução real permanece bloqueada porque `NewsRepository` completo ainda não existe no destino. A UI não faz requests diretamente.

## Vídeos

A UI possui busca, períodos rápidos, executar/parar, progresso/status, fontes instáveis e ações Abrir/WhatsApp/Copiar. O período personalizado do Kotlin ainda não foi reproduzido. A execução real permanece bloqueada pelo `VideoRepository` ausente.

## Demandas

CRUD local de adicionar/excluir usa `NewsDb`. `Buscar todas` usa a porta de automação quando injetada. Busca individual aguarda o business `NewsRepository`; não foi simulada no runtime.

## Termos

Termos de notícias usam o CRUD real do `NewsDb`. Termos de vídeo permanecem visíveis como área da tela, mas não podem ser mutados porque `MIG-024` segue bloqueado.

## Fontes

Catálogo de notícias/especializadas portado integralmente: 160 fontes, 27 estados e 7 opções de região. A página inclui tabs, busca, região, estado, modo todos os veículos, selecionar/limpar visíveis e todas/nenhuma.

`VideoSourceCatalog` base ainda não foi migrado; somente `youtube-g1` e `youtube-domingo-espetacular` aparecem no catálogo de vídeo do destino. Isso é bloqueio explícito, não substituição.

## Histórico

Usa `NewsDb.listNews(2000)` e `VideoDb.listAll(2000)`, tabs e limpeza por tipo. Testes de DB/UI passaram.

## Configurações

Proxy usa infraestrutura segura do Passo 8 e teste de conexão em thread. Startup usa `StartupManager`. Automação grava as preferências reais já migradas.

O campo de senha usa modo password, é limpo após salvar e não repõe plaintext descriptografado no refresh. Isso difere do Kotlin por requisito explícito de segurança.

Cards completos de última/próxima execução e `Executar agora` por categoria ainda não foram reproduzidos; `MIG-102` permanece `EM TESTE`.

## Atalhos, double-click e menus de contexto

Nenhum keyboard shortcut ativo nem double-click foi encontrado no `DashboardV5Main.kt` revisado; portanto nenhum foi inventado.

Menus de contexto adicionais ao tray: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**.

## Testes do Passo 9

A suíte adiciona testes para:

- instanciar MainWindow;
- título e tamanho inicial;
- 12 seções e navegação completa;
- close-to-tray;
- termos e demandas CRUD;
- histórico local;
- chamadas manuais via AutomationPort fake;
- indisponibilidade explícita quando business repositories não existem;
- proxy/startup/campo password;
- catálogo de fontes;
- ordem/labels das seções;
- constantes visuais;
- placeholders de ferramentas.

A workflow executa `compileall` e toda a suíte em Windows e Ubuntu. Qt roda em `offscreen`; no Linux são instaladas apenas as libs de runtime necessárias. O último run do Passo 9 passou nos dois sistemas.

## Validação manual

Não foi realizada uma sessão humana interativa com desktop gráfico. A aplicação foi instanciada e todas as páginas foram percorridas por testes reais do Qt em modo offscreen nos dois sistemas. Portanto qualquer afirmação de inspeção visual humana seria incorreta.

## Regras permanentes

Os identificadores `MIG-001` a `MIG-105` são permanentes. Não renumerar, agrupar, reutilizar ou substituir números. Novos itens futuros devem receber identificadores após `MIG-105`.

Um MIG somente pode ser marcado `APROVADO` após comparação objetiva com a baseline e validação compatível com sua natureza. Widget existente com motor fake/stub ou dependência ausente não é aprovação funcional.
