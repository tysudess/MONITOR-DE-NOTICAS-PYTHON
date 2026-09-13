# Migração Kotlin → Python

## Fonte da verdade

- Repositório original: `tysudess/noticias-monitor`
- Baseline Kotlin auditada: `df1701ba5427a04954093e8ebed63f26abb2b2b7` + transformações do workflow V8.
- Repositório destino: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- Branch de integração: `migration/python-foundation`.
- Passo 13 congelou o Python em `6419ee336f3015bd466afa8c2ac4e961ca7c6ff3` para a auditoria.
- Passo 14 recompôs o runtime real e foi validado por CI determinístico e smoke live antes desta atualização documental.

O comportamento comprovado é a fonte da verdade. Lacunas não são preenchidas por suposição. Quando algo não é comprovado: **NÃO DETERMINADO PELO CÓDIGO ANALISADO.**

## Estados permitidos

`PENDENTE`, `EM MIGRAÇÃO`, `EM TESTE`, `APROVADO`, `BLOQUEADO`.

`APROVADO` significa equivalência objetiva dentro do escopo explícito do MIG. Existência de código, aparência semelhante ou teste verde isolado não bastam.

## Passo 14 — composição e runtime real

O bloqueio estrutural encontrado no Passo 13 foi removido sem reescrever os motores já migrados. O fluxo de produção passou a ser:

```text
run.py
  → Application
  → AppContainer
     → AppPaths / SharedPreferences
     → NewsDb / VideoDb
     → ProxySettings / HTTP
     → collectors existentes
     → NewsRepository / VideoRepository
     → RuntimeNewsRunner / RuntimeVideoRunner
     → AutomationService
     → RuntimeUiController
  → MainWindow
```

O `AppContainer` é composition root: ele monta dependências; não contém scraping, matching ou SQL de negócio.

Também foram ligados o `VideoTermStore` independente, catálogo base completo de vídeos, seleção real de fontes, runners de notícias/vídeos, busca individual de demanda no controller runtime, atualização da UI após as lanes terminarem, `newNewsLinks`/`newVideoLinks`, proxy dinâmico dos collectors e notificação tray.

### Evidência determinística

Workflow `Python migration tests`, run `34729628580`, head `b5f287b058031ae4b6ee7cb77e705a58a330dab4`:

- Windows: `compileall` aprovado e suíte completa aprovada;
- Ubuntu: `compileall` aprovado e suíte completa aprovada;
- suíte completa: **141 testes**, sem falha exibida pelo pytest.

Os testes de composição em `tests/integration/composition/` exercitam repository, matching, SQLite, automação e controller reais. Doubles são usados apenas na borda externa controlada quando necessário.

### Evidência live

Workflow `Passo 14 live smoke`, run `34729671873`, head `0c5a691c6cd1eb59bbabaa1dd4b57570cb9d735c`:

```text
LIVE NEWS OK found=22 new=22 stored=22
LIVE VIDEO COLLECTOR OK items=15
```

O smoke de notícias percorreu Google News real → `NewsRepository` → matching → `news.db`. O smoke de vídeo consultou o coletor real do canal g1.

### Google News URL resolver

O equivalente Python de `GoogleNewsUrlResolver.kt` existe. Entretanto, a revisão do `DashboardV5Main.kt` do baseline `df1701...` não comprovou uma chamada direta ao resolver nas ações visuais do dashboard. A UI Python atual abre/copia o link armazenado. Portanto, `MIG-114` **não é promovido por suposição** e permanece `PENDENTE` até existir evidência concreta do fluxo válido que deve consumi-lo.

### Placeholders

Os placeholders deliberados do editor de vídeo continuam deliberadamente não funcionais conforme `MIG-077`; não foram transformados em funcionalidades inventadas. O fallback de `MainUiController` sem automação permanece útil para testes/injeção, mas o caminho de produção usa `RuntimeUiController` montado pelo `AppContainer`.

## Checklist oficial após Passo 14

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
| MIG-014 | Notícias | Janela padrão de 24h | APROVADO |
| MIG-015 | Notícias | Google News RSS | APROVADO |
| MIG-016 | Notícias | Planejamento de queries por termo/fonte | APROVADO |
| MIG-017 | Notícias | Identidade storyKey | APROVADO |
| MIG-018 | Notícias | Preservação da primeira captura/NOVO | APROVADO |
| MIG-019 | Notícias | Matching subjectMatches | APROVADO |
| MIG-020 | Notícias | Matching fonte/veículo | APROVADO |
| MIG-021 | Notícias | Collector direto Últimas Notícias | APROVADO |
| MIG-022 | Notícias | Busca individual de demanda | EM TESTE |
| MIG-023 | Vídeos | Janela padrão de 24h | APROVADO |
| MIG-024 | Vídeos | VideoTermStore independente | APROVADO |
| MIG-025 | Vídeos | VideoMatchPolicy | APROVADO |
| MIG-026 | Vídeos | Planejamento source scan x term query | APROVADO |
| MIG-027 | Vídeos | Globoplay Edições | EM TESTE |
| MIG-028 | Vídeos | Globoplay Trechos | EM TESTE |
| MIG-029 | Vídeos | Globoplay Jarvis global | APROVADO |
| MIG-030 | Vídeos | Coleta YouTube canal | APROVADO |
| MIG-031 | Vídeos | Enriquecimento de página direta | APROVADO |
| MIG-032 | Vídeos | Canonical URLs e merge | APROVADO |
| MIG-033 | Vídeos | Classificação de fonte instável | EM TESTE |
| MIG-034 | Vídeos | Fontes Desktop extras | APROVADO |
| MIG-035 | Automação | Loop residente | APROVADO |
| MIG-036 | Automação | Intervalo automático notícias | APROVADO |
| MIG-037 | Automação | Intervalo automático demandas | APROVADO |
| MIG-038 | Automação | Horários automáticos vídeos | APROVADO |
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
| MIG-096 | UI | Notícias | EM TESTE |
| MIG-097 | UI | Vídeos | EM TESTE |
| MIG-098 | UI | Demandas | EM TESTE |
| MIG-099 | UI | Termos | EM TESTE |
| MIG-100 | UI | Fontes | EM TESTE |
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
| MIG-112 | Vídeos/Catálogo | Catálogo base completo VideoSourceCatalog | APROVADO |
| MIG-113 | Runtime/Repositories | NewsRepository + VideoRepository + wiring real da aplicação | APROVADO |
| MIG-114 | Notícias/UI | Resolver URL real do veículo para links Google News | PENDENTE |
| MIG-115 | Runtime/Composição | Composition root AppContainer e inicialização real do runtime | APROVADO |

## Totais após Passo 14

- Total: **115 MIGs**.
- `APROVADO`: **63**.
- `EM TESTE`: **43**.
- `PENDENTE`: **8**.
- `BLOQUEADO`: **1**.

## Pendências que permanecem fora da aprovação do Passo 14

1. `MIG-050`: helper/login interno Globoplay continua bloqueado.
2. `MIG-114`: resolver Google News existe, mas seu consumo pelo fluxo válido da UI não foi comprovado no baseline; não inventar wiring.
3. `MIG-079`–`MIG-083`: build/portable final ainda não foi executado.
4. `MIG-096`–`MIG-100`: wiring real foi destravado, mas validação humana de tela permanece `EM TESTE`.
5. Windows/DPAPI/processos, FFmpeg/FFprobe/preview, extrator, PDF e demais itens marcados `EM TESTE` continuam exigindo suas validações específicas.

## Regras permanentes

Os IDs `MIG-001` a `MIG-115` são permanentes. Não renumerar, reutilizar ou substituir. Novos achados recebem somente IDs posteriores. `APROVADO` vale apenas para o escopo objetivo do respectivo MIG.
