# Arquitetura da migração Python

## Estado após o Passo 5

A fundação do Passo 3 e a camada SQLite do Passo 4 permanecem válidas. O Passo 5 adiciona somente regras puras de negócio/matching da baseline `df1701ba5427a04954093e8ebed63f26abb2b2b7`.

A UI continua mínima. Coletores HTTP, schedulers, automações e integrações Windows não foram ligados.

## Fluxo de entrada

`run.py` → `monitor_noticias.app.application.Application` → `QApplication` → `monitor_noticias.ui.main_window.MainWindow`.

## Caminhos e dados

`AppPaths` continua centralizando `resources/`, `data/`, `data/news.db`, `data/videos.db`, `bin/`, `logs/` e `temp/`.

A camada de dados continua em:

- `monitor_noticias.database.connection`
- `monitor_noticias.database.news_db`
- `monitor_noticias.database.video_db`

MIG-005 a MIG-013 permanecem `EM TESTE` por falta de banco runtime real para confronto final.

## Models

Persistidos: `News`, `Demand`, `VideoItem`.

Adicionados no Passo 5 somente porque são necessários às regras puras: `MediaSource` e `VideoSource`.

Os catálogos completos de fontes não foram migrados.

## Matching

### `monitor_noticias.matching.common`

Normalização: lowercase → Unicode NFD → remoção de marcas `Mn` → substituição de tudo que não seja `[a-z0-9]` por espaço → trim. `compact()` remove espaços depois da normalização.

### `monitor_noticias.matching.news_rules`

Porta `story_key`, `merge_news`, `reuse_historical_identity`, `subject_matches`, `demand_vehicle_matches`, `source_matches_strict` e `publisher_host_key` do `NewsRepository.kt`.

Notícias usam tokens exatos no fallback de `subjectMatches`; não usam flexões.

### `monitor_noticias.matching.video_match_policy`

Porta o objeto Kotlin `VideoMatchPolicy` usado pelo reparo do banco. Frase vazia retorna `false`.

### `monitor_noticias.matching.video_rules`

Porta regras puras privadas de `VideoRepository.kt`: matcher de vídeo do repository, equivalência de flexões, exceção de 7 de Setembro, `source_matches_demand`, canonicalização, merge, período, título/summary genéricos, validação de URL específica e prioridade estável de candidatos Globoplay.

A busca por rede e a resolução de páginas não fazem parte deste módulo.

### `monitor_noticias.matching.term_rules`

`clean_video_terms()` porta somente `VideoTermStore.clean`: trim, remoção de vazios, distinct case-insensitive e ordenação case-insensitive.

A persistência `VideoTermStore` continua bloqueada até MIG-003/SharedPreferences.

## Deduplicação lógica

Notícias: identidade editorial por `storyKey`; histórico consultado por link antes de storyKey; reencontro preserva link histórico e primeira `capturedAt`; merge acumula termos sem repetir e promove `important`/`demand`.

Vídeos: URLs são canonicalizadas antes do `canonicalKey`; YouTube converge para `/watch?v=<id>`; URL não-YouTube perde query/fragment; merge acumula termos, preserva demanda anterior quando a nova é vazia e usa `max(capturedAt)`.

## Prioridade e exclusões

Globoplay usa somente prioridade booleana: candidatos com match superficial de Termo/Demanda vêm primeiro, preservando a ordem original como desempate.

Filtros puros preservados: títulos curtos/genéricos, summaries genéricos, paths genéricos, validação específica por tipo de fonte e limite de palavra por token. Não há fuzzy matching, stemming, lematização, IA, embedding ou score adicional.

## Testes

O Passo 5 adiciona testes unitários e golden cases em `tests/equivalence/`, cobrindo acentos/case, palavra inteira x substring, frase multi-palavra, flexões, 7 de Setembro, canonicalização, prioridade estável e merge/deduplicação lógica.

## Módulos ainda não migrados nesta etapa

- coletores HTTP
- repositories completos de busca/rede
- automação/scheduler
- UI completa
- Windows/proxy/notificações
- editor de vídeo
- editor PDF
- extrator/downloader
- persistência completa do VideoTermStore
