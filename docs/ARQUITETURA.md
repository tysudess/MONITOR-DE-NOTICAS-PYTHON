# Arquitetura da migração Python

## Estado após o Passo 4

A fundação do Passo 3 continua válida. O Passo 4 adiciona somente a camada de dados equivalente ao Desktop Kotlin da baseline `df1701ba5427a04954093e8ebed63f26abb2b2b7`.

## Fluxo de entrada

`run.py` → `monitor_noticias.app.application.Application` → `QApplication` → `monitor_noticias.ui.main_window.MainWindow`.

A UI continua mínima. Nenhuma tela de negócio foi migrada neste passo.

## Caminhos

`AppPaths` centraliza a raiz e deriva:

- `resources/`
- `data/`
- `data/news.db`
- `data/videos.db`
- `bin/`
- `logs/`
- `temp/`
- `bin/ffmpeg.exe`
- `bin/ffprobe.exe`

O Desktop Kotlin usa `Context.filesDir = PortablePaths.dataDir`; por isso os bancos permanecem em `data/news.db` e `data/videos.db`.

## Camada de dados

### `monitor_noticias.database.connection`

`SQLiteConnection` é a camada central de conexão. Usa `sqlite3` da biblioteca padrão, `sqlite3.Row`, `PRAGMA journal_mode=WAL` e `PRAGMA busy_timeout=5000`. Operações compostas usam `BEGIN`/`COMMIT` e `ROLLBACK` em erro.

### `monitor_noticias.database.news_db`

`NewsDb` reproduz o DAO Desktop Kotlin:

- cria `news`, `terms` e `demands` com o mesmo SQL;
- executa somente as migrations runtime comprovadas no Kotlin;
- aplica o seed `DEFAULT_MONITOR_TERMS` com `INSERT OR IGNORE`;
- implementa `insertNews`, `listRecent`, `listNews`, `listTerms`, `addTerm`, `removeTerm`, `listDemands`, `addDemand`, `updateDemandStatus`, `removeDemand` e `clearHistory`;
- preserva a primeira `captured_at` de notícia em conflito de link;
- promove `important` e `demand` somente de 0 para 1;
- substitui `matched_term`/`matched_demand` somente quando o valor novo não é vazio.

### `monitor_noticias.database.video_db`

`VideoDb` reproduz o DAO Desktop Kotlin:

- cria somente `videos` com o mesmo SQL;
- **não cria migration automática de colunas**, porque a baseline Kotlin também não cria;
- implementa `insert`, `removeInvalidListingEntries`, `repairStoredMatches`, `listRecent`, `listPeriod`, `listAll` e `clear`;
- preserva `captured_at` em conflito de link;
- mantém ordenação `published_at DESC, captured_at DESC`.

### Models persistidos

Foram migrados somente os models diretamente necessários à camada de persistência:

- `News`
- `Demand`
- `VideoItem`

Os nomes conceituais, campos, opcionais lógicos e defaults do Kotlin foram preservados. Models de UI, progresso de busca e resultados de coletores continuam pendentes.

### Dependência mínima de matching para reparo

`VideoDb.repairStoredMatches` no Kotlin chama `VideoMatchPolicy.phraseMatches`. Para não alterar MIG-013, foi portado apenas esse mecanismo exato como dependência interna da camada de dados.

Isso **não aprova nem conclui MIG-025**. O matching completo de busca continua pendente.

## Repositories

Os `NewsRepository.kt` e `VideoRepository.kt` originais combinam persistência com rede, coletores e regras de busca. Esses módulos não foram parcialmente recriados, porque isso produziria uma abstração nova e incompleta.

Nesta etapa, `NewsDb` e `VideoDb` são os DAOs persistentes ativos equivalentes. O pacote `repositories` permanece reservado para o passo em que os repositories de negócio completos puderem ser migrados com seus coletores.

## Banco original e testes

Nenhum banco runtime real foi modificado. O repositório Kotlin não contém cópias versionadas de `news.db` ou `videos.db`. Os testes de equivalência usam bancos temporários e fixtures criadas com o SQL literal da baseline.

Por essa razão, MIG-005 a MIG-013 permanecem em `EM TESTE`, aguardando confronto adicional com uma cópia real de banco existente antes de `APROVADO`.

## Módulos ainda placeholders

Continuam sem migração funcional:

- UI completa
- collectors/news
- collectors/video
- repositories de busca
- automation
- networking
- Windows integrations
- video editor
- PDF editor
- extraction/downloader

## Dependências

Nenhum ORM foi adicionado. A camada de dados usa exclusivamente `sqlite3` da biblioteca padrão do Python.
