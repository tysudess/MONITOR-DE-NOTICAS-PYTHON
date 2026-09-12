# Migração Kotlin → Python

## Fonte da verdade

- Repositório original: `tysudess/noticias-monitor`
- Repositório destino: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- Baseline funcional: Build SHA `df1701ba5427a04954093e8ebed63f26abb2b2b7` + transformações do workflow da release V8.

## Estados permitidos

`PENDENTE`, `EM MIGRAÇÃO`, `EM TESTE`, `APROVADO`, `BLOQUEADO`.

Neste Passo 3 **nenhum MIG foi aprovado**. A fundação cria infraestrutura para os passos seguintes, mas não substitui os critérios de equivalência Kotlin × Python.

## Checklist oficial

| MIG | Módulo | Funcionalidade | Status |
|---|---|---|---|
| MIG-001 | Infraestrutura | Baseline congelada df1701 + workflow | PENDENTE |
| MIG-002 | Infraestrutura | Resolução de raiz portable | PENDENTE |
| MIG-003 | Infraestrutura | SharedPreferences portable | PENDENTE |
| MIG-004 | Infraestrutura | Tray e execução residente | PENDENTE |
| MIG-005 | Banco | Schema news | PENDENTE |
| MIG-006 | Banco | Migrations runtime news/demands | PENDENTE |
| MIG-007 | Banco | Tabela terms e seed | PENDENTE |
| MIG-008 | Banco | CRUD/status de demandas | PENDENTE |
| MIG-009 | Banco | Deduplicação/upsert lógico de notícias | PENDENTE |
| MIG-010 | Banco | Schema videos | PENDENTE |
| MIG-011 | Banco | Compatibilidade sem migration automática de videos | PENDENTE |
| MIG-012 | Banco | Remoção de listings genéricos | PENDENTE |
| MIG-013 | Banco | Reparo de matches armazenados | PENDENTE |
| MIG-014 | Notícias | Janela padrão de 24h | PENDENTE |
| MIG-015 | Notícias | Google News RSS | PENDENTE |
| MIG-016 | Notícias | Planejamento de queries por termo/fonte | PENDENTE |
| MIG-017 | Notícias | Identidade storyKey | PENDENTE |
| MIG-018 | Notícias | Preservação da primeira captura/NOVO | PENDENTE |
| MIG-019 | Notícias | Matching subjectMatches | PENDENTE |
| MIG-020 | Notícias | Matching fonte/veículo | PENDENTE |
| MIG-021 | Notícias | Collector direto Últimas Notícias | PENDENTE |
| MIG-022 | Notícias | Busca individual de demanda | PENDENTE |
| MIG-023 | Vídeos | Janela padrão de 24h | PENDENTE |
| MIG-024 | Vídeos | VideoTermStore independente | PENDENTE |
| MIG-025 | Vídeos | VideoMatchPolicy | PENDENTE |
| MIG-026 | Vídeos | Planejamento source scan x term query | PENDENTE |
| MIG-027 | Vídeos | Globoplay Edições | PENDENTE |
| MIG-028 | Vídeos | Globoplay Trechos | PENDENTE |
| MIG-029 | Vídeos | Globoplay Jarvis global | PENDENTE |
| MIG-030 | Vídeos | Coleta YouTube canal | PENDENTE |
| MIG-031 | Vídeos | Enriquecimento de página direta | PENDENTE |
| MIG-032 | Vídeos | Canonical URLs e merge | PENDENTE |
| MIG-033 | Vídeos | Classificação de fonte instável | PENDENTE |
| MIG-034 | Vídeos | Fontes Desktop extras g1/Domingo Espetacular | PENDENTE |
| MIG-035 | Automação | Loop residente | PENDENTE |
| MIG-036 | Automação | Intervalo automático de notícias | PENDENTE |
| MIG-037 | Automação | Intervalo automático de demandas | PENDENTE |
| MIG-038 | Automação | Horários automáticos de vídeos | PENDENTE |
| MIG-039 | Windows | Iniciar com Windows | PENDENTE |
| MIG-040 | Windows | Proxy geral | PENDENTE |
| MIG-041 | Windows | Migração proxy-7db→proxy-7dn | PENDENTE |
| MIG-042 | Controle | Cancelamento de buscas | PENDENTE |
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

## Regra de numeração

Os identificadores MIG-001 a MIG-083 são permanentes. Não renumerar, agrupar, reutilizar ou substituir números. Novos itens futuros devem receber novos identificadores após MIG-083.

## Regra de aprovação

Um MIG somente pode ser marcado `APROVADO` após comparação objetiva com a baseline válida. A existência de código Python “parecido” não é critério de aprovação.
