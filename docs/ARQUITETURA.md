# Arquitetura da migração Python

## Estado após o Passo 7

A fundação, SQLite, matching e coletores dos Passos 3–6 permanecem válidos. O Passo 7 adiciona a camada de automação do Windows baseada diretamente em `DesktopControllerV5` da baseline `df1701ba5427a04954093e8ebed63f26abb2b2b7`.

Não existe uma classe Kotlin ativa chamada `AutomationService` no Desktop V8 analisado. A classe Python `monitor_noticias.automation.AutomationService` é o nome arquitetural dado à extração do motor que no Kotlin vive dentro de `DesktopControllerV5`; comportamento, ordem, guards e cadências vêm do Kotlin.

A UI continua mínima. Windows startup/proxy, notificações nativas, PDF, Editor de Vídeo, extrator/downloader e empacotamento portable continuam fora deste passo.

## Camadas

- `monitor_noticias.app.preferences`: compatibilidade de SharedPreferences Desktop baseada em arquivo `.properties`.
- `monitor_noticias.automation.models`: `LiveSearchProgress` e contratos mínimos de resultado.
- `monitor_noticias.automation.clock`: relógio local injetável para testes; runtime usa relógio do sistema.
- `monitor_noticias.automation.settings`: chaves/defaults de automação da baseline.
- `monitor_noticias.automation.service`: scheduler de 30 s, guards, lanes, estado, progresso e cancelamento cooperativo.
- `monitor_noticias.collectors.*`: permanece responsável por rede/parsing; não é duplicado no scheduler.
- `monitor_noticias.matching`: permanece responsável por matching; não é duplicado no scheduler.
- `monitor_noticias.database`: permanece responsável por SQLite; o scheduler não contém SQL.

## Topologia de execução

O Kotlin usa `CoroutineScope(SupervisorJob() + Dispatchers.Default)`, `newsJob` e `videoJob` separados, com `newsBusy` compartilhado entre notícias/demandas e `videoBusy` separado.

O equivalente Python usa:

1. uma thread daemon para o loop de 30 segundos;
2. um executor serial (`max_workers=1`) para notícias/demandas;
3. um executor serial (`max_workers=1`) para vídeos.

Isso preserva a topologia observada: notícias e demandas são mutuamente exclusivas; vídeo pode rodar simultaneamente com uma delas. Não foram criados pools por fonte nem paralelismo adicional.

## Scheduling

### Notícias

Default 30 min; mínimo 15. Vencimento: `now - lastNewsAutoAt >= interval * 60000`. O timestamp é persistido antes de iniciar `search_news()`.

### Demandas

Default 60 min; mínimo 15. Usa a mesma lane de notícias e só é testada no `else if` após notícias; por isso notícia vencida tem prioridade. Timestamp também é persistido antes do job.

### Vídeos

Horários padrão: `08:00`, `12:00`, `15:00`, `19:00`, `21:00`. Usa horário local do sistema, compara apenas `HH:mm` e impede duplicação pela chave `yyyy-MM-dd-HH-mm` em `desktop_auto_video_slot`.

O loop não implementa catch-up explícito para um minuto perdido. Comportamento do sistema operacional em suspensão/retomada além dessa regra: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**.

## Execução manual e automática

A automação chama os mesmos métodos públicos usados por disparos manuais: notícias → `search_news`, demandas → `search_all_demands`, vídeos → `search_videos`. Dessa forma não existem dois motores com regras diferentes.

## Estado e progresso

Não foram inventados enums `IDLE/RUNNING/...`. O estado preserva os campos concretos do Controller: `newsBusy`, `videoBusy`, `status`, `videoStatus`, progresso de notícias/vídeos, durações e fontes de vídeo instáveis.

`LiveSearchProgress` reproduz os campos e a fração do Kotlin. O serviço expõe callback `on_state` desacoplado da UI; futura camada PySide6 pode transformar isso em sinais sem acoplar widgets ao motor.

## Retry e timeout

Não existe retry no scheduler Desktop analisado. Não existe timeout global de job comprovado. Logo a automação Python não adiciona nenhum. Retry/timeout continuam responsabilidade das camadas de coleta já migradas.

## Cancelamento

O Kotlin cancela o `Job` correspondente e a coroutine propaga `CancellationException`. O Python usa `CancellationToken` e preserva os mesmos guards/status. A equivalência durante uma chamada de I/O já bloqueada permanece `EM TESTE` até os repositories reais consumirem o token entre operações.

## Persistência

`SharedPreferences` grava em `data/prefs/monitor_prefs.properties`, mantendo escalares em texto e StringSet em Base64 URL-safe sem padding, separado por `|`. A gravação usa arquivo temporário e substituição.

Compatibilidade byte a byte com `java.util.Properties.store` ainda não foi confrontada; por isso MIG-003 está `EM TESTE`.

## Fronteira com repositories

Os business repositories completos (`NewsRepository`/`VideoRepository`) ainda não foram migrados no destino. Para não inventar uma implementação parcial dentro do scheduler, `AutomationService` depende de protocolos `NewsRunner` e `VideoRunner`.

Esses runners deverão, em passo próprio, conectar coletores + matching + DAOs com as regras exatas dos repositories Kotlin. Até isso ocorrer, o motor de scheduling pode ser validado deterministicamente com fakes, mas não é declarado integração end-to-end de rede/banco.

## Testes

64 testes passaram, 0 falhas, incluindo toda a regressão dos Passos 3–6. `compileall` passou. Os testes de automação usam relógio/fakes e não aguardam horários reais nem dependem da Internet.

## Ainda não migrado

- orchestration completa de `NewsRepository`/`VideoRepository`;
- ligação end-to-end dos runners com collectors/matching/DAO;
- cancelamento comprovado dentro de I/O bloqueante;
- compatibilidade byte a byte de SharedPreferences JVM;
- `VideoTermStore` persistente;
- proxy global e startup Windows;
- notificações Windows nativas;
- UI completa;
- Editor de Vídeo;
- Editor PDF;
- extrator/downloader;
- portable final.
