# Migração Kotlin → Python

## Fonte da verdade

- Repositório original: `tysudess/noticias-monitor`
- Repositório destino: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- Baseline funcional: Build SHA `df1701ba5427a04954093e8ebed63f26abb2b2b7` + transformações do workflow V8.
- Branch de migração: `migration/python-foundation`.

O comportamento comprovado é a fonte da verdade. Lacunas não são preenchidas por suposição. Quando algo não é comprovado: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**.

## Estados permitidos

`PENDENTE`, `EM MIGRAÇÃO`, `EM TESTE`, `APROVADO`, `BLOQUEADO`.

## Estado após o Passo 10

Os Passos 1–9 permanecem preservados. O Passo 10 substitui o placeholder visual do Extrator pela implementação PySide6 integrada e porta o motor efetivo da release: cinco presets, yt-dlp nightly/stable, Deno, FFmpeg/FFprobe, roteamento YouTube/Globoplay/R7/genérico, fallbacks HTML, snapshot HLS de live, compatibilidade H.264, cancelamento, histórico/qualidade portable, sessão Globoplay DPAPI e updater seguro.

Editor PDF, Editor de Vídeo e portable final não foram iniciados.

O source correto do Extrator não é somente `ExtractorVideoEngine.kt`: o workflow da release executa patches antes da compilação. O Passo 10 usa `df1701...` + `integrate-v8-extractor-tab.py` + `patch-extractor-generic-html.py` e patches encadeados + `patch-extractor-hidden-process.py` como contrato final.

## MIG trabalhados no Passo 10

- `MIG-043` — cinco presets: `APROVADO` por comparação literal/testes.
- `MIG-044` — download genérico yt-dlp: `EM TESTE` até download real com binários da release.
- `MIG-045` — retry compatível: `APROVADO` por equivalência determinística.
- `MIG-046` — fallback HTML genérico: `APROVADO` para parser/ordem/filtros; integração externa coberta por `MIG-044`.
- `MIG-047` — R7/Record: `EM TESTE` até teste real externo.
- `MIG-048` — Globoplay multicaminho: `EM TESTE` até teste real externo.
- `MIG-049` — sessão Globoplay DPAPI: `EM TESTE` para integração completa; proteção DPAPI base já existe/testada.
- `MIG-050` — login interno Globoplay: `BLOQUEADO` porque `GloboplayLoginHelper.exe` pertence ao empacotamento/portable excluído deste passo.
- `MIG-051` — YouTube normal: `EM TESTE` até mídia real.
- `MIG-052` — snapshot YouTube Live: `EM TESTE` até live real controlada.
- `MIG-053` — remux/transcode live: `EM TESTE` até FFmpeg real do pacote.
- `MIG-054` — H.264: `EM TESTE` até arquivo real; comando/decisão testados.
- `MIG-055` — cancelamento/invalidação: `EM TESTE` até subprocesso real do bundle; árvore/token testados.
- `MIG-056` — histórico/qualidade portable: `APROVADO`.
- `MIG-057` — updater seguro yt-dlp: `EM TESTE` até atualização real controlada.
- `MIG-106` — UI PySide6 do Extrator integrada ao Monitor: `EM TESTE`.
- `MIG-107` — regressão/equivalência automatizada do Passo 10: `APROVADO`.

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
| MIG-058 | PDF | Importação PDF/imagens/drop | PENDENTE |
| MIG-059 | PDF | Página em branco | PENDENTE |
| MIG-060 | PDF | Crop normalizado | PENDENTE |
| MIG-061 | PDF | Rotação e flip | PENDENTE |
| MIG-062 | PDF | Reordenação drag-and-drop | PENDENTE |
| MIG-063 | PDF | Undo/redo 30 snapshots | PENDENTE |
| MIG-064 | PDF | Capa padrão/custom | PENDENTE |
| MIG-065 | PDF | Qualidade exportação | PENDENTE |
| MIG-066 | PDF | Exportação vetorial | PENDENTE |
| MIG-067 | PDF | Exportação raster | PENDENTE |
| MIG-068 | Editor Vídeo | Launcher PySide6 | PENDENTE |
| MIG-069 | Editor Vídeo | Importação múltipla | PENDENTE |
| MIG-070 | Editor Vídeo | Probe FFprobe | PENDENTE |
| MIG-071 | Editor Vídeo | Preview | PENDENTE |
| MIG-072 | Editor Vídeo | Áudio/mute | PENDENTE |
| MIG-073 | Editor Vídeo | Timeline multiclip | PENDENTE |
| MIG-074 | Editor Vídeo | Seek global/local | PENDENTE |
| MIG-075 | Editor Vídeo | Play/pause/avanço | PENDENTE |
| MIG-076 | Editor Vídeo | Exportação trecho | PENDENTE |
| MIG-077 | Editor Vídeo | Placeholders sem inventar | PENDENTE |
| MIG-078 | Editor Vídeo | IN/OUT manual NÃO DETERMINADO | PENDENTE |
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

## Inventário do Extrator final

### Dependências externas da release

| Arquivo | Papel |
|---|---|
| `bin/yt-dlp.exe` | engine principal/nightly |
| `bin/yt-dlp-stable.exe` | engine stable preferido no Globoplay |
| `bin/ffmpeg.exe` | merge/remux/transcode/live |
| `bin/ffprobe.exe` | codec de vídeo |
| `bin/deno.exe` | runtime JS passado ao yt-dlp |

O workflow baixa versões `latest`; versão exata de yt-dlp/Deno: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**. FFmpeg tenta BtbN n9.0 e depois Gyan; a fonte concreta do ZIP aprovado é **NÃO DETERMINADO PELO CÓDIGO ANALISADO** sem inspeção do artefato/log.

### Fontes/rotas

- YouTube/YouTu.be → probe; normal ou live.
- Globoplay/`globo:` → stable yt-dlp, sessão DPAPI, múltiplas tentativas.
- R7/Record → página + candidatos HTML.
- Outros → mídia direta ou yt-dlp + fallback HTML.

### Qualidades

`360p`, `480p`, `720p HD`, `1080p Full HD`, `Melhor disponível`; default `480p`. Selectors/compat permanecem literais conforme documentação de arquitetura.

### Output

Pasta `Videos/`; template `%(title).150B [%(id)s].%(ext)s`; merge/remux para MP4. Live própria usa `<title> [LIVE-ATE-AGORA <timestamp>] [<id>].mp4`.

### Proxy

O engine suporta parâmetro proxy, mas a release final remove o proxy próprio e chama o Extrator com string vazia. O proxy geral do Monitor **não foi ligado** no Passo 10 porque isso seria alterar o comportamento aprovado.

### Globoplay

Sessão salva em `data/extractor/globoplay.session.dpapi`, DPAPI CurrentUser. O login real requer `data/extractor/runtime/GloboplayLoginHelper.exe`, que não é empacotado neste passo e mantém `MIG-050 BLOQUEADO`.

## Testes do Passo 10

Testes unitários/equivalência cobrem presets, selectors, classificação, normalização R7, parser HTML, histórico/qualidade, construção do comando yt-dlp, progresso, retry, FFprobe/H.264, cancelamento e contrato visual da tela.

A workflow executou `compileall` e a suíte completa em Windows e Ubuntu e passou nos dois ambientes. No run Windows foram executados **102 testes** (`72 + 30` na saída compacta do pytest).

## Validação manual / integração externa

Não foi executado download humano real de YouTube/R7/Globoplay/live com o bundle final da release, porque o Passo 10 exclui o portable final e o repositório alvo não contém os cinco executáveis/helper. Seria incorreto chamar mocks/fixtures de teste real. Por isso os MIGs dependentes de mídia externa permanecem `EM TESTE` e o login helper `BLOQUEADO`.

## Regras permanentes

Os identificadores `MIG-001` a `MIG-107` são permanentes. Não renumerar/reutilizar. Um MIG só vira `APROVADO` após comparação objetiva e validação compatível com sua natureza.
