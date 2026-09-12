# Arquitetura da migração Python

## Estado após o Passo 6

A fundação do Passo 3, a camada SQLite do Passo 4 e o matching do Passo 5 permanecem válidos. O Passo 6 adiciona somente coletores HTTP/parsers isolados da baseline `df1701ba5427a04954093e8ebed63f26abb2b2b7`.

A UI continua mínima. AutomationService, schedulers, notificações Windows, PDF, Editor de Vídeo, extrator/downloader e empacotamento portable não foram iniciados.

## Fluxo de entrada

`run.py` → `monitor_noticias.app.application.Application` → `QApplication` → `monitor_noticias.ui.main_window.MainWindow`.

## Camadas existentes

- `monitor_noticias.app`: bootstrap, paths, logging e exceções.
- `monitor_noticias.database`: SQLite, `NewsDb`, `VideoDb`.
- `monitor_noticias.models`: `News`, `Demand`, `VideoItem`, `MediaSource`, `VideoSource`.
- `monitor_noticias.matching`: regras puras de notícias/vídeos.
- `monitor_noticias.networking`: transporte HTTP comum somente quando o contrato é compatível.
- `monitor_noticias.collectors.news`: Google News RSS e Últimas Notícias.
- `monitor_noticias.collectors.video`: Globoplay, YouTube, portal genérico e página direta.

## Networking

### `HttpClient`

Usa `requests.Session` e mantém:

- GET e POST JSON;
- timeouts de conexão/leitura separados;
- redirects habilitados;
- headers passados por coletor;
- limite de corpo quando o Kotlin usa `maxBodySize`;
- proxies opcionais por injeção, sem implementar ainda a configuração global do MIG-040.

Não existe retry genérico. Retry é responsabilidade de cada coletor quando comprovado no Kotlin.

## Coletores de notícias

### Google News

`GoogleNewsCollector` porta `NewsRepository.fetchGoogleNews`: URL pt-BR, GET, UA `MonitorNoticiasAndroid/3.0`, connect 8 s, read 10 s, XML RSS, campos `title/link/pubDate/description/source`, snippet máximo 500. Falha retorna `None`, como `runCatching(...).getOrNull()`.

### Últimas Notícias

`NewsLatestCollector` porta o coletor direto das seis fontes: CNN, Metrópoles, Folha, R7, Jovem Pan e O Globo. Mantém UA, Accept-Language, Referer Google, timeout 12 s, limite 3,5 MB, seleção de links/artigos, metadata e match local. O coletor retorna `Outcome(failed=True)` quando a página de listagem falha.

## Coletores de vídeo

### Globoplay Trechos

`GloboplayTrechosCollector` preserva o fluxo conhecido: rota estável → landing `/t/<token>` → seed de `/v/<id>` → descoberta por busca → até dois seeds → `/cenas/` → anchors/JSON serializado. Mantém timeout 14 s, corpo 8 MB, máximo 2 páginas de programa e máximo 48 trechos. MIG-028 permanece `EM TESTE` até confronto integral de todas as rotas estáveis.

### Globoplay Edições

`GloboplayEditionCollector` preserva descoberta de programa, identificação de edição por `dd/MM/yyyy`, janela do dia limitada a `capturedAt`, abertura da edição e extração de trechos. MIG-027 permanece `EM TESTE` porque limites específicos por categoria de fonte ainda exigem confronto integral com o catálogo Kotlin.

### Globoplay Jarvis

`GloboplayJarvisCollector` usa POST `https://cloud-jarvis.globo.com/graphql`, payload/operationName/query original, headers `x-platform-id`, `x-device-id`, `x-client-version`, connect 8 s/read 12 s e somente 2 tentativas com espera de 350 ms. Expande queries com a regra especial de 7 de Setembro e singularização comprovada. Mantém orçamento de 48 enriquecimentos de data em `/v/<id>`.

### YouTube

`YouTubeCollector` usa a aba `/videos` como caminho principal, detecta channelId, consulta RSS como apoio para data/descrição e prefere o item RSS quando o mesmo vídeo aparece em ambos. g1 e Domingo Espetacular mantêm os channel IDs oficiais do Desktop Kotlin. HTML usa timeout 18 s; RSS usa 16 s; máximo 40 itens.

### Portal HTML genérico

`WebsiteVideoCollector` representa `fetchWebsite/fetchSearchWebsite/fetchPageLinks`: monta a query com `searchPrefix`, resolve links relativos, aplica validação de URL específica, extrai título/summary e deduplica por canonicalKey. Ele retorna candidatos; não persiste no banco.

### Página direta

`DirectVideoPageResolver` representa `resolveDirectVideoPage`: canonical/og:url, título, descrição, JSON/metadata estruturada, data publicada, sinal de vídeo e summary enriquecido até 1800 caracteres.

## Matching e persistência

Os coletores reutilizam as funções do Passo 5. Não há cópia de matcher dentro dos coletores quando o Kotlin faz matching no repository. Nenhum coletor grava diretamente em SQLite; `NewsDb`/`VideoDb` continuam separados.

## Testes

O Passo 6 adiciona fixtures controladas, testes unitários, integração de transporte e golden cases. A suíte completa local, incluindo Passos 3–5, passou com 49 testes e 0 falhas. `compileall` também passou.

## Ainda não migrado

- orchestration completa de `NewsRepository`/`VideoRepository`;
- `AutomationService`/scheduler;
- classificação de fonte instável no fluxo completo;
- SharedPreferences/VideoTermStore persistente;
- proxy global/configuração/credenciais;
- UI completa;
- Windows notifications/startup;
- Editor de Vídeo;
- Editor PDF;
- extrator/downloader;
- empacotamento portable.
