# Arquitetura da migração Python

## Fonte da verdade

A migração usa `tysudess/noticias-monitor`, Build SHA `df1701ba5427a04954093e8ebed63f26abb2b2b7`, mais as transformações do workflow da release V8. O destino é `tysudess/MONITOR-DE-NOTICAS-PYTHON`, branch `migration/python-foundation`.

A regra permanente é preservar o motor e o comportamento comprovados. Quando uma dependência necessária ainda não existe no destino, a camada superior não a recria por conveniência.

## Arquitetura atual após o Passo 9

```text
Application
└─ MainWindow (PySide6 QMainWindow)
   ├─ Sidebar
   │  ├─ Início
   │  ├─ Notícias
   │  ├─ Vídeos
   │  ├─ Demandas
   │  ├─ Fontes
   │  ├─ Histórico
   │  ├─ Termos
   │  ├─ Parar buscas
   │  ├─ Configurações
   │  ├─ Editor de PDF [placeholder visual]
   │  ├─ Extrator de Vídeos [placeholder visual]
   │  └─ Editor de Vídeo [placeholder visual]
   ├─ QStackedWidget
   │  ├─ HomePage
   │  ├─ NewsPage
   │  ├─ VideosPage
   │  ├─ DemandsPage
   │  ├─ SourcesPage
   │  ├─ HistoryPage
   │  ├─ TermsPage
   │  ├─ StopPage
   │  ├─ SettingsPage
   │  └─ três páginas-placeholder de ferramentas
   └─ QSystemTrayIcon
      ├─ Abrir
      ├─ Buscar notícias agora
      ├─ Buscar vídeos agora
      ├─ Buscar demandas agora
      ├─ Parar buscas
      └─ Sair

UI widgets
   ↓
MainUiController
   ├─ NewsDb / VideoDb
   ├─ SharedPreferences
   ├─ ProxySettings
   ├─ StartupManager
   └─ AutomationService/AutomationPort [injetável]

AutomationService
   ↓
NewsRunner / VideoRunner
   ↓
Business repositories [ainda ausentes no destino]
```

## Regra UI x lógica

Widgets PySide6 não contêm SQL, scraping, matching nem scheduling. `MainUiController` é uma camada fina que:

- carrega listas recentes do banco;
- executa CRUD já disponível de termos de notícias e demandas;
- limpa históricos;
- lê/grava preferências de seleção de fontes;
- chama `ProxySettings` e `StartupManager`;
- encaminha comandos ao `AutomationService` quando uma porta real é injetada;
- sincroniza status/progresso do serviço para a UI.

O destino ainda não possui os business `NewsRepository` e `VideoRepository` completos. Por isso a `MainWindow` padrão não fabrica runners falsos. Os botões de busca ficam indisponíveis no runtime padrão até essa composição existir. Nos testes, uma porta fake é injetada apenas para validar o encadeamento UI → controller → service.

## MainWindow

Contrato reproduzido do Dashboard V5 ativo:

- título: `Monitor de Notícias - Windows Portable v4.0.2`;
- tamanho inicial: 1600×960;
- sidebar de 258 px;
- `QStackedWidget` para as páginas principais;
- timer Qt de 250 ms para sincronização visual segura no thread da GUI;
- fechar a janela oculta para o tray;
- encerramento real ocorre pela ação `Sair`;
- menu do tray reproduz as ações do Kotlin;
- ícone `monitor-icon.svg` foi preservado do projeto original.

Tamanho mínimo, estado inicial maximizado e posição inicial específica: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**.

## Navegação e seções

A ordem final considera a transformação de build que adiciona `VIDEO_EDITOR` depois de `EXTRACTOR`:

1. Início
2. Notícias
3. Vídeos
4. Demandas
5. Fontes
6. Histórico
7. Termos
8. Parar buscas
9. Configurações
10. Editor de PDF
11. Extrator de Vídeos
12. Editor de Vídeo

Editor PDF, Extrator e Editor de Vídeo possuem somente integração visual neste passo. Seus motores não foram migrados.

## Telas principais

### HomePage

Reproduz os indicadores de notícias, vídeos, vídeos recentes, demandas, fontes, resumo operacional e ações rápidas. Não cria KPI novo.

O bloco meteorológico/decorativo e alguns detalhes puramente visuais do Compose não foram reproduzidos neste passo; isso não foi substituído por outra fonte ou API.

### NewsPage

Contém:

- busca textual por título/fonte/termo/demanda;
- filtro `Só demandas`;
- períodos Hoje, 24 horas, 7 dias, 30 dias e período personalizado;
- execução, parada, progresso e status;
- tabela de resultados;
- abrir, WhatsApp e copiar link.

A execução real fica condicionada à futura composição do business repository.

### VideosPage

Contém busca textual, períodos rápidos, execução/parada, progresso/status, painel de fontes instáveis e ações Abrir/WhatsApp/Copiar.

O período personalizado da tela Kotlin ainda não foi reproduzido. O editor de vídeo permanece fora do escopo.

### DemandsPage

Reproduz a tela ativa do V5: veículo, assunto, Adicionar, Buscar todas, listagem, última busca, encontrados, novos, Buscar e Excluir. Não foi inventada edição inline nem status visual que não existiam na tela ativa.

A busca individual de uma demanda permanece bloqueada pela ausência do business `NewsRepository`.

### TermsPage

Termos de notícias usam o CRUD existente em `NewsDb`. A coluna de termos de vídeo é visível, mas sua mutação permanece bloqueada porque `VideoTermStore` ainda é `MIG-024 BLOQUEADO`.

### SourcesPage

Usa tabs Notícias/Vídeos/Mídia especializada e reproduz:

- busca textual;
- Região;
- Estado;
- `TODOS OS VEÍCULOS — SEM EXCEÇÃO`;
- Selecionar visíveis;
- Limpar visíveis;
- Todas;
- Nenhuma;
- checkboxes por fonte.

O catálogo de notícias foi portado do `SourceCatalog.kt`: 13 nacionais + 135 estaduais + 12 especializadas = 160 fontes.

O catálogo base de vídeos (`VideoSourceCatalog.kt`) ainda não possui módulo equivalente no destino. A UI usa apenas os dois extras Desktop já migrados: `youtube-g1` e `youtube-domingo-espetacular`. `VIDEO_CATALOG_COMPLETE=False` registra explicitamente essa lacuna.

### HistoryPage

Tabs Notícias/Vídeos, carregando `listNews(2000)` e `listAll(2000)`, com limpeza por tipo.

### StopPage

Exibe status de Notícias/Demandas e Vídeos e encaminha `stop_news_search`, `stop_video_search` e `stop_all_searches` ao serviço quando disponível.

### SettingsPage

Conecta:

- proxy enabled/host/port/user/password;
- salvar e aplicar;
- teste de proxy em `QThread`, sem bloquear a GUI;
- automação geral/notícias/demandas/vídeos;
- intervalos de notícias/demandas;
- horários de vídeo;
- startup Windows.

O campo de senha usa `Password` e é limpo após salvar. Ao atualizar a tela, o Python não repõe a senha descriptografada no campo. Essa é uma adaptação deliberada de segurança, registrada em decisão de migração.

A tela Kotlin possui cards mais ricos de automação com `Executar agora`, última/próxima execução. A versão Python atual ainda não reproduz todos esses elementos visuais, portanto a tela permanece `EM TESTE`.

## Networking e segurança

`ProxySettings` continua responsável pelo proxy autenticado e mantém senha em DPAPI CurrentUser. A UI nunca persiste senha diretamente.

`StartupManager` continua usando HKCU Run e evita gravar caminho de desenvolvimento. A opção visual existe, mas validação do executável final depende do passo portable.

`WindowsTrayNotifier` usa `QSystemTrayIcon.showMessage(title, message)`; as regras de quando notificar permanecem no `AutomationService`.

## Processos

`HiddenProcessRunner` permanece fora dos widgets e usa `shell=False`, argv em lista e flags Windows comprovadas. O Passo 9 não adicionou chamadas de FFmpeg/FFprobe/yt-dlp.

## Model/View e atualização

As páginas de notícias, vídeos, demandas e histórico usam `QTableWidget`; fontes e termos usam `QListWidget`. A UI atualiza apenas a página corrente a cada 250 ms, além dos refreshes explícitos após CRUD/configuração.

Operações de proxy usam worker thread. Buscas reais são responsabilidade do `AutomationService` e não fazem `requests` diretamente no clique da UI.

## Atalhos, duplo clique e contexto

Na revisão do `DashboardV5Main.kt` ativo não foram encontrados contratos ativos de keyboard shortcut ou double-click. Portanto nenhum atalho novo foi criado.

Menus de contexto específicos além do tray: **NÃO DETERMINADO PELO CÓDIGO ANALISADO** na tela ativa revisada.

## Testes de UI

`tests/unit/test_ui_step9.py` usa Qt em modo `offscreen` e valida:

- criação da MainWindow;
- título/tamanho;
- 12 entradas de navegação;
- navegação para cada página;
- close-to-tray;
- CRUD de termo/demanda;
- histórico DB;
- encadeamento com AutomationPort fake;
- ausência explícita de engine quando repositories não existem;
- campo de senha;
- proxy/startup;
- catálogo de fontes.

`tests/equivalence/test_ui_equivalence.py` protege ordem/labels das seções, constantes visuais principais, catálogo de notícias e placeholders de ferramentas.

A workflow de migração instala as libs Qt necessárias no Ubuntu e executa `compileall` + toda a suíte em Windows e Ubuntu, com `QT_QPA_PLATFORM=offscreen`. O último run do Passo 9 passou nos dois sistemas.

## Diferenças Compose → PySide6 registradas

- `Window` Compose → `QMainWindow`;
- navegação por composables condicionais → `QStackedWidget`;
- `LazyColumn`/cards → tabelas/listas/widgets Qt;
- `TrayState` → `QSystemTrayIcon`;
- estado Compose observado por recomposição → `MainUiController` + timer Qt no thread da GUI;
- ícones Material não foram copiados como pacote de assets; a navegação usa símbolos locais simples sem dependência remota.

Não se exige pixel-perfect; perdas funcionais não são aceitas e, onde existem lacunas, os MIGs permanecem não aprovados.

## Pendências deliberadas após o Passo 9

- composição real de `NewsRepository`/`VideoRepository` no destino;
- busca individual de demanda;
- `VideoTermStore` persistente;
- catálogo base `VideoSourceCatalog` no destino;
- período personalizado da tela de vídeos;
- cards completos de automação com última/próxima execução e `Executar agora`;
- alguns estados vazios/badges visuais do Compose;
- bloco meteorológico/decorativo do dashboard;
- teste humano em desktop interativo; a validação automatizada atual é Qt offscreen em Windows/Ubuntu;
- Editor PDF completo;
- Extrator independente;
- Editor de Vídeo completo;
- portable final.
