# Migração Kotlin → Python

## Fonte da verdade

- Repositório original: `tysudess/noticias-monitor`
- Baseline Kotlin auditada: `df1701ba5427a04954093e8ebed63f26abb2b2b7` + transformações do workflow V8.
- Repositório destino: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- Branch: `migration/python-foundation`
- Commit Python congelado para o Passo 13: `6419ee336f3015bd466afa8c2ac4e961ca7c6ff3`.

O comportamento comprovado é a fonte da verdade. Lacunas não são preenchidas por suposição. Quando algo não é comprovado: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**.

## Estados permitidos

`PENDENTE`, `EM MIGRAÇÃO`, `EM TESTE`, `APROVADO`, `BLOQUEADO`.

## Passo 13 — conclusão da auditoria

A auditoria geral encontrou uma lacuna estrutural crítica: os componentes de coleta/matching existem parcialmente no Python, porém `NewsRepository` e `VideoRepository` de negócio não existem no destino e a aplicação real cria `MainWindow()` sem `AutomationService`. O próprio `MainUiController` informa que as buscas estão indisponíveis quando a automação não é injetada. Assim, a aplicação abre, lê bancos e renderiza telas, mas o fluxo operacional principal do Monitor não está ligado de ponta a ponta.

Também foi comprovado que o catálogo base `VideoSourceCatalog.kt` não foi migrado: a UI Python recebe apenas os dois extras Desktop (`youtube-g1` e `youtube-domingo-espetacular`). `VideoTermStore` independente continua ausente. A resolução de wrappers do Google News antes de abrir/copiar/compartilhar também não possui equivalente Python.

A suíte verde dos passos anteriores não invalida essas conclusões: há testes que explicitamente esperam `search_available == False` e apenas dois itens no catálogo de vídeos. Portanto, testes verdes não constituem equivalência global.

## Alterações de status produzidas pelo Passo 13

### Promovidos por equivalência direta revalidada

- `MIG-001`: baseline congelada e rastreada — `APROVADO`.
- `MIG-005` a `MIG-013`: schemas, migrations, CRUD/upserts e reparos SQLite — `APROVADO`; código e testes de equivalência foram comparados diretamente, inclusive banco antigo/migration/transações/Unicode.

### Rebaixados

- `MIG-035` a `MIG-038`: de `APROVADO` para `BLOQUEADO`. O scheduler/algoritmo existe isoladamente, mas a aplicação real não instancia nem inicia `AutomationService`, e seus runners de negócio não existem.

### Pendências que passam a BLOQUEADO pela dependência estrutural comprovada

- `MIG-014`, `MIG-016`, `MIG-022`, `MIG-023`, `MIG-026`, `MIG-033`.

### Novos MIGs encontrados pela análise reversa

- `MIG-112` — catálogo base completo `VideoSourceCatalog`: `BLOQUEADO`.
- `MIG-113` — `NewsRepository` + `VideoRepository` + wiring real da aplicação: `BLOQUEADO`.
- `MIG-114` — resolução de URL real do veículo para links Google News: `PENDENTE`.

## Checklist oficial após Passo 13

| MIG | Módulo | Funcionalidade | Status |
|---|---|---|---|
| MIG-001 | Infraestrutura | Baseline congelada df1701 + workflow | APROVADO |
| MIG-002 | Infraestrutura | Resolução de raiz portable | PENDENTE |
| MIG-003 | Infraestrutura | SharedPreferences portable | EM TESTE |
| MIG-004 | Infraestrutura | Tray e execução residente | EM TESTE |
| MIG-005 | Banco | Schema news | APROVADO |
| MIG-006 | Banco | Migrations runtime news/demands | APROVADO |
| MIG-007 | Banco | Tabela terms e seed | APROVADO |
| MIG-008 | Banco | CRUD/status de demandas | APROVADO |
| MIG-009 | Banco | Deduplicação/upsert lógico de notícias | APROVADO |
| MIG-010 | Banco | Schema videos | APROVADO |
| MIG-011 | Banco | Compatibilidade sem migration automática de videos | APROVADO |
| MIG-012 | Banco | Remoção de listings genéricos | APROVADO |
| MIG-013 | Banco | Reparo de matches armazenados | APROVADO |
| MIG-014 | Notícias | Janela padrão de 24h | BLOQUEADO |
| MIG-015 | Notícias | Google News RSS | APROVADO |
| MIG-016 | Notícias | Planejamento de queries por termo/fonte | BLOQUEADO |
| MIG-017 | Notícias | Identidade storyKey | APROVADO |
| MIG-018 | Notícias | Preservação da primeira captura/NOVO | APROVADO |
| MIG-019 | Notícias | Matching subjectMatches | APROVADO |
| MIG-020 | Notícias | Matching fonte/veículo | APROVADO |
| MIG-021 | Notícias | Collector direto Últimas Notícias | APROVADO |
| MIG-022 | Notícias | Busca individual de demanda | BLOQUEADO |
| MIG-023 | Vídeos | Janela padrão de 24h | BLOQUEADO |
| MIG-024 | Vídeos | VideoTermStore independente | BLOQUEADO |
| MIG-025 | Vídeos | VideoMatchPolicy | APROVADO |
| MIG-026 | Vídeos | Planejamento source scan x term query | BLOQUEADO |
| MIG-027 | Vídeos | Globoplay Edições | EM TESTE |
| MIG-028 | Vídeos | Globoplay Trechos | EM TESTE |
| MIG-029 | Vídeos | Globoplay Jarvis global | APROVADO |
| MIG-030 | Vídeos | Coleta YouTube canal | APROVADO |
| MIG-031 | Vídeos | Enriquecimento de página direta | APROVADO |
| MIG-032 | Vídeos | Canonical URLs e merge | APROVADO |
| MIG-033 | Vídeos | Classificação de fonte instável | BLOQUEADO |
| MIG-034 | Vídeos | Fontes Desktop extras | APROVADO |
| MIG-035 | Automação | Loop residente | BLOQUEADO |
| MIG-036 | Automação | Intervalo automático notícias | BLOQUEADO |
| MIG-037 | Automação | Intervalo automático demandas | BLOQUEADO |
| MIG-038 | Automação | Horários automáticos vídeos | BLOQUEADO |
| MIG-039 | Windows | Iniciar com Windows | EM TESTE |
| MIG-040 | Windows | Proxy geral | EM TESTE |
| MIG-041 | Windows | Migração proxy 7db→7dn | APROVADO |
| MIG-042 | Controle | Cancelamento de buscas | EM TESTE |
| MIG-043 | Extrator | Cinco presets de qualidade | APROVADO |
| MIG-044 | Extrator | Download genérico yt-dlp | EM TESTE |
| MIG-045 | Extrator | Retry de compatibilidade | APROVADO |
| MIG-046 | Extrator | Fallback HTML genérico | APROVADO |
| MIG-047 | Extrator | Fluxo R7/Record | EM TESTE |
| MIG-048 | Extrator | Fluxo Globoplay multicaminho | EM TESTE |
| MIG-049 | Extrator | Sessão Globoplay protegida | EM TESTE |
| MIG-050 | Extrator | Login interno Globoplay | BLOQUEADO |
| MIG-051 | Extrator | Probe/download YouTube normal | EM TESTE |
| MIG-052 | Extrator | Snapshot YouTube Live HLS | EM TESTE |
| MIG-053 | Extrator | Remux/transcode Live FFmpeg | EM TESTE |
| MIG-054 | Extrator | Compatibilidade H.264 | EM TESTE |
| MIG-055 | Extrator | Cancelamento e invalidação callbacks | EM TESTE |
| MIG-056 | Extrator | Histórico/qualidade portable | APROVADO |
| MIG-057 | Extrator | Atualizador seguro yt-dlp | EM TESTE |
| MIG-058 | PDF | Importação PDF/imagens/drop | APROVADO |
| MIG-059 | PDF | Página em branco | APROVADO |
| MIG-060 | PDF | Crop normalizado | APROVADO |
| MIG-061 | PDF | Rotação e flip | PENDENTE |
| MIG-062 | PDF | Reordenação drag-and-drop | APROVADO |
| MIG-063 | PDF | Undo/redo 30 snapshots | APROVADO |
| MIG-064 | PDF | Capa padrão/custom | APROVADO |
| MIG-065 | PDF | Qualidade exportação | APROVADO |
| MIG-066 | PDF | Exportação vetorial | APROVADO |
| MIG-067 | PDF | Exportação raster | APROVADO |
| MIG-068 | Editor Vídeo | Launcher PySide6 | EM TESTE |
| MIG-069 | Editor Vídeo | Importação múltipla | EM TESTE |
| MIG-070 | Editor Vídeo | Probe FFprobe | EM TESTE |
| MIG-071 | Editor Vídeo | Preview | EM TESTE |
| MIG-072 | Editor Vídeo | Áudio/mute | EM TESTE |
| MIG-073 | Editor Vídeo | Timeline multiclip | APROVADO |
| MIG-074 | Editor Vídeo | Seek global/local | EM TESTE |
| MIG-075 | Editor Vídeo | Play/pause/avanço | EM TESTE |
| MIG-076 | Editor Vídeo | Exportação trecho | EM TESTE |
| MIG-077 | Editor Vídeo | Placeholders sem inventar | APROVADO |
| MIG-078 | Editor Vídeo | IN/OUT manual ausente no motor ativo | APROVADO |
| MIG-079 | Build | Entrada Desktop original | PENDENTE |
| MIG-080 | Build | Transformações workflow | PENDENTE |
| MIG-081 | Build | PyInstaller editor | PENDENTE |
| MIG-082 | Build | Cinco binários portáteis | PENDENTE |
| MIG-083 | Build | BUILD-SHA/hash ZIP | PENDENTE |
| MIG-084 | Vídeos | Priorização Globoplay | APROVADO |
| MIG-085 | Vídeos | Filtros candidato direto | APROVADO |
| MIG-086 | Vídeos | Coletor HTML portal/busca | APROVADO |
| MIG-087 | Networking | HTTP injetável | APROVADO |
| MIG-088 | Automação | Orquestração/lanes | APROVADO |
| MIG-089 | Automação | Progresso/status/durações | APROVADO |
| MIG-090 | Windows/Segurança | DPAPI CurrentUser | EM TESTE |
| MIG-091 | Windows | Notificação tray | EM TESTE |
| MIG-092 | Windows | Processo oculto/árvore | EM TESTE |
| MIG-093 | Segurança | Senha proxy DPAPI | EM TESTE |
| MIG-094 | UI | MainWindow/sidebar/stack/tray | EM TESTE |
| MIG-095 | UI | Dashboard/Início | EM TESTE |
| MIG-096 | UI | Notícias | BLOQUEADO |
| MIG-097 | UI | Vídeos | BLOQUEADO |
| MIG-098 | UI | Demandas | BLOQUEADO |
| MIG-099 | UI | Termos | BLOQUEADO |
| MIG-100 | UI | Fontes | BLOQUEADO |
| MIG-101 | UI | Histórico | APROVADO |
| MIG-102 | UI | Configurações | EM TESTE |
| MIG-103 | UI | Parar buscas/status | EM TESTE |
| MIG-104 | UI | Pontos visuais ferramentas | APROVADO |
| MIG-105 | UI/Testes | Smoke/navegação/equivalência Qt | APROVADO |
| MIG-106 | UI/Extrator | Workspace PySide6 real do Extrator | EM TESTE |
| MIG-107 | Extrator/Testes | Equivalência e regressão automatizada Passo 10 | APROVADO |
| MIG-108 | UI/PDF | Workspace PySide6 real do Editor PDF | EM TESTE |
| MIG-109 | PDF/Testes | Equivalência e regressão automatizada Passo 11 | APROVADO |
| MIG-110 | UI/Vídeo | Workspace real do Editor de Vídeo integrado | EM TESTE |
| MIG-111 | Vídeo/Testes | Equivalência e regressão automatizada Passo 12 | APROVADO |
| MIG-112 | Vídeos/Catálogo | Catálogo base completo VideoSourceCatalog | BLOQUEADO |
| MIG-113 | Runtime/Repositories | NewsRepository + VideoRepository + wiring real da aplicação | BLOQUEADO |
| MIG-114 | Notícias/UI | Resolver URL real do veículo para links Google News | PENDENTE |

## Totais após auditoria

- Total: **114 MIGs**.
- `APROVADO`: **51**.
- `EM TESTE`: **36**.
- `PENDENTE`: **8**.
- `BLOQUEADO`: **19**.

## Bloqueadores de equivalência / portable

1. `MIG-113`: business repositories e wiring real da aplicação.
2. `MIG-112`: catálogo completo de vídeo.
3. `MIG-024`: termos de vídeo independentes.
4. `MIG-014/016/022/023/026/033/035–038`: fluxos que dependem dos repositories/wiring.
5. `MIG-096–100`: telas de negócio ainda bloqueadas em equivalência funcional.
6. `MIG-050`: helper/login Globoplay.
7. `MIG-079–083`: build/portable final ainda não executado.
8. validações reais ainda `EM TESTE` em Windows/FFmpeg/FFprobe/preview/extrator/PDF conforme seus MIGs.

## Regras permanentes

Os IDs `MIG-001` a `MIG-114` são permanentes. Não renumerar, reutilizar ou substituir. `APROVADO` significa equivalência objetiva dentro do escopo explícito do MIG, não apenas existência de código ou teste verde.
