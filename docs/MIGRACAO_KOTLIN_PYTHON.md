# Migração Kotlin → Python

## Fonte da verdade

- Repositório original: `tysudess/noticias-monitor`
- Repositório destino: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- Baseline funcional: Build SHA `df1701ba5427a04954093e8ebed63f26abb2b2b7` + transformações do workflow da release V8.

## Estados permitidos

`PENDENTE`, `EM MIGRAÇÃO`, `EM TESTE`, `APROVADO`, `BLOQUEADO`.

## Estado após o Passo 7

O motor automático efetivo do Windows não está em uma classe Kotlin chamada `AutomationService`: ele reside em `DesktopControllerV5`, principalmente em `automationLoop()`, `searchNews()`, `searchAllDemands()`, `searchVideos()` e funções de cancelamento. O Python usa o nome `AutomationService` como camada desacoplada para portar esse motor, não para inventar um scheduler novo.

Aprovados neste passo por comparação estática direta e testes determinísticos: `MIG-035`, `MIG-036`, `MIG-037`, `MIG-038`, `MIG-088` e `MIG-089`.

`MIG-003` passou para `EM TESTE`: existe persistência `data/prefs/monitor_prefs.properties` com escalares e StringSet Base64 URL-safe, mas a compatibilidade byte a byte com um arquivo produzido pela JVM ainda não foi confrontada.

`MIG-042` passou para `EM TESTE`: a camada Python preserva guards, estados e cancelamento cooperativo, porém a interrupção de uma operação HTTP já bloqueada só poderá ser validada quando os repositories completos estiverem ligados ao token.

`MIG-014`, `MIG-016`, `MIG-022`, `MIG-023`, `MIG-026` e `MIG-033` continuam `PENDENTE`, pois pertencem à orchestration completa de `NewsRepository`/`VideoRepository`, que ainda não existe no destino. O AutomationService depende de portas (`NewsRunner`/`VideoRunner`) e não duplica coletores, matching ou SQL.

## Checklist oficial

| MIG | Módulo | Funcionalidade | Status |
|---|---|---|---|
| MIG-001 | Infraestrutura | Baseline congelada df1701 + workflow | PENDENTE |
| MIG-002 | Infraestrutura | Resolução de raiz portable | PENDENTE |
| MIG-003 | Infraestrutura | SharedPreferences portable | EM TESTE |
| MIG-004 | Infraestrutura | Tray e execução residente | PENDENTE |
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
| MIG-039 | Windows | Iniciar com Windows | PENDENTE |
| MIG-040 | Windows | Proxy geral | PENDENTE |
| MIG-041 | Windows | Migração proxy-7db→proxy-7dn | PENDENTE |
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
| MIG-087 | Networking | Transporte HTTP compatível e injetável para coletores | APROVADO |
| MIG-088 | Automação | Orquestração Desktop manual/automática e lanes de concorrência | APROVADO |
| MIG-089 | Automação | Progresso, status, durações e resultado operacional Desktop | APROVADO |

## Pipeline Desktop comprovado

### Notícias automáticas

`tick de 30 s` → `desktop_automatic_monitoring` → verifica `desktop_news_automatic` e intervalo → guard `newsBusy` → grava `desktop_auto_news_at` **antes** do job → chama o mesmo `searchNews()` usado manualmente → repository progressivo → progresso/status → resultado/notificação opcional → `finally`: duração e `newsBusy=false`.

Intervalo padrão: 30 minutos. Mínimo: 15 minutos.

### Demandas automáticas

No mesmo tick e na mesma lane de notícias: após verificar notícias, demandas entram somente no `else if`. Portanto, quando ambas estão vencidas, notícias têm prioridade. Guard: `newsBusy`. A timestamp `desktop_auto_demands_at` é gravada antes do job e é chamado o mesmo `searchAllDemands()` usado manualmente.

Intervalo padrão: 60 minutos. Mínimo: 15 minutos.

### Vídeos automáticos

No mesmo tick, mas em lane independente: verifica `desktop_video_automatic` e `videoBusy` → obtém hora local do sistema → compara `HH:mm` com `desktop_video_schedule_times` → monta chave `yyyy-MM-dd-HH-mm` → compara com `desktop_auto_video_slot` → grava slot e `desktop_auto_video_at` antes do job → chama o mesmo `searchVideos()` manual.

Horários padrão: `08:00`, `12:00`, `15:00`, `19:00`, `21:00`.

Não há catch-up explícito de um minuto de vídeo perdido. Comportamento específico do SO em suspensão/retomada, além dessa regra observável: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**.

## Concorrência e dupla execução

- notícias e demandas compartilham a mesma lane/guard e nunca iniciam juntas pelo Controller;
- vídeos usam lane/guard independente e podem coexistir com notícias ou demandas;
- disparo manual e automático usam os mesmos métodos;
- segundo disparo do mesmo grupo enquanto `busy=true` é ignorado;
- não existe paralelização por fonte adicionada pelo AutomationService.

No Python isso é reproduzido com um `ThreadPoolExecutor(max_workers=1)` para notícias/demandas, outro de um worker para vídeos e uma thread leve de scheduler. A escolha de threads evita bloquear a futura UI Qt, sem aumentar a concorrência observada no Kotlin.

## Retry e timeout

O `automationLoop()` Desktop não adiciona retry externo nem timeout global de job. Portanto o Python também não cria esses mecanismos. Retries e timeouts permanecem nas camadas onde já foram comprovados (por exemplo, coletores do Passo 6). Não há duplicação de retry.

Timeout global da automação completa: **NÃO DETERMINADO PELO CÓDIGO ANALISADO** — nenhum timeout desse tipo foi encontrado no motor Desktop analisado.

## Timezone e relógio

O scheduler de vídeos usa `LocalDateTime.now()`: horário local do sistema, sem timezone explícita e sem conversão UTC. A abstração `SystemClock` existe apenas para testes; em runtime usa relógio/local datetime do sistema.

Tratamento especial de alteração manual do relógio do Windows, suspensão/retomada e DST: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**. A regra comprovada continua sendo a comparação do minuto local atual e a chave diária/minuto.

## Progresso, estado e relatório operacional

`LiveSearchProgress` mantém exatamente: `active`, `kind`, `startedAt`, `finishedAt`, `completed`, `total`, `currentSource`, `currentQuery`, `found`, `newCount`, `errors`; `fraction` é `completed/total` limitado a 0..1 e zero quando `total<=0`.

O Desktop não possui um `AutoReport` rico no caminho analisado. O resultado operacional é composto por status textual, progresso, duração da última busca de notícias/vídeos, lista de fontes de vídeo instáveis e os objetos de resultado retornados pelos repositories. Não foi criado relatório “melhorado”.

## Persistência de automação

Persistidos no mesmo conceito de SharedPreferences Desktop:

- `desktop_automatic_monitoring`;
- `desktop_news_automatic`;
- `desktop_demand_automatic`;
- `desktop_video_automatic`;
- `desktop_news_interval`;
- `desktop_demand_interval`;
- `desktop_video_schedule_times`;
- `desktop_auto_news_at`;
- `desktop_auto_demands_at`;
- `desktop_auto_video_at`;
- `desktop_auto_video_slot`.

Estado transitório (`busy`, progress corrente, status e Futures/tokens) permanece em memória. Próxima execução calculada/persistida para o scheduler Desktop: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**; o código observado não persiste uma próxima execução.

## Integração pendente com repositories

O destino ainda não possui `NewsRepository` e `VideoRepository` completos. `AutomationService` recebe `NewsRunner` e `VideoRunner` por protocolo para que o Passo 7 possa validar scheduling/concorrência/estado sem recriar scraping, matching ou SQL. A ligação real dos coletores + matching + banco dentro desses repositories continua pendente.

## Testes do Passo 7

A suíte completa passou com 64 testes e 0 falhas, incluindo todos os testes anteriores. Foram adicionados casos de:

- defaults e mínimos;
- prioridade notícias sobre demandas;
- execução de demanda quando notícia não venceu;
- horário local exato de vídeo e chave anti-duplicação;
- ausência de catch-up para minuto perdido;
- coexistência notícia/vídeo;
- guard contra dupla execução;
- mesmo caminho manual/automático;
- cancelamento cooperativo e limpeza de busy;
- ausência de retry externo;
- cálculo de progresso;
- round-trip de preferências e StringSet Base64;
- golden cases de intervalos/slot.

`python -m compileall -q src` também passou.

## Regra de numeração

Os identificadores MIG-001 a MIG-089 são permanentes. Não renumerar, agrupar, reutilizar ou substituir números. Novos itens futuros devem receber novos identificadores após MIG-089.

## Regra de aprovação

Um MIG somente pode ser marcado `APROVADO` após comparação objetiva com a baseline válida. A existência de código Python “parecido” não é critério de aprovação.
