# Migração Kotlin → Python

## Fonte da verdade

- Repositório original: `tysudess/noticias-monitor`
- Repositório destino: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- Baseline funcional: Build SHA `df1701ba5427a04954093e8ebed63f26abb2b2b7` + transformações do workflow V8.
- Branch de migração: `migration/python-foundation`.

O comportamento comprovado é a fonte da verdade. Lacunas não são preenchidas por suposição. Quando algo não é comprovado: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**.

## Estados permitidos

`PENDENTE`, `EM MIGRAÇÃO`, `EM TESTE`, `APROVADO`, `BLOQUEADO`.

## Estado após o Passo 12

Os Passos 1–11 permanecem preservados. O Passo 12 remove o placeholder do Editor de Vídeo e integra o editor efetivamente distribuído pela release V8.

A auditoria direta corrigiu uma premissa importante: o motor ativo da release não é `VideoEditorEngine.kt`. A cadeia efetiva é `DashboardV5Main` → `VideoEditorScreen.kt` → `PySideVideoEditorLauncher` → `video-editor/VideoEditorPySide/VideoEditorPySide.exe`, empacotado pelo workflow a partir de `video_editor_pyside/main.py`.

O editor ativo já é Python/PySide6 6.9.1 e usa QtMultimedia `QMediaPlayer` + `QVideoWidget` + `QAudioOutput`. Os arquivos Kotlin `VideoEditorEngine.kt`, `VideoEditorPreview.kt` e `VideoEditorProcess.kt` pertencem a uma implementação alternativa/legada mais rica e **não foram misturados** ao motor distribuído.

Por isso não foram inventados split, excluir/duplicar/reordenar clipe, drag-and-drop, thumbnails, zoom, IN/OUT manual, undo/redo, compactação, target-size, seleção de codec/resolução/FPS, concatenação, progresso ou cancelamento: o `main.py` ativo não implementa essas operações.

Portable final não foi iniciado.

## MIG trabalhados no Passo 12

- `MIG-068` — launcher/workspace PySide6: `EM TESTE`; integrado, mas a release original abre EXE separado e o portable final ainda não foi montado/testado.
- `MIG-069` — importação múltipla: `EM TESTE`; formatos, ordem, validação e UI preservados, sem teste humano com mídia real.
- `MIG-070` — probe FFprobe: `EM TESTE`; comando/parsing aprovados por teste determinístico, sem execução com o `ffprobe.exe` exato da release.
- `MIG-071` — preview: `EM TESTE`; mesmo QMediaPlayer/QVideoWidget preservado, sem teste real de decode/play/seek em desktop.
- `MIG-072` — áudio/mute: `EM TESTE`; mesmo QAudioOutput e volume 0,85, sem reprodução humana real.
- `MIG-073` — timeline multiclip: `APROVADO`; matemática, desenho, seleção, régua e playhead foram comparados/testados.
- `MIG-074` — seek global/local: `EM TESTE`; conversão matemática está aprovada, mas precisão efetiva do player ainda não foi medida com vídeo real.
- `MIG-075` — play/pause/avanço: `EM TESTE`; callbacks e sequência preservados, sem reprodução humana real.
- `MIG-076` — exportação de trecho: `EM TESTE`; comando FFmpeg literal está protegido, mas não houve exportação real + FFprobe final com o bundle aprovado.
- `MIG-077` — placeholders sem inventar: `APROVADO`.
- `MIG-078` — IN/OUT manual: `APROVADO` como ausência comprovada; `start_ms/end_ms` existem no modelo, mas a UI ativa não oferece edição manual e nada foi inventado.
- `MIG-110` — workspace do Editor de Vídeo integrado à MainWindow: `EM TESTE` até validação interativa/processo separado no portable.
- `MIG-111` — equivalência/regressão automatizada do Passo 12: `APROVADO`.

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

## Inventário funcional do Editor PDF ativo

### Código ativo x legado

- `PdfEditorScreenV2.kt`: **ATIVO**.
- `PdfEditorScreen.kt`: **LEGADO/ANTERIOR** para a release V8 analisada.
- patches `patch-pdf-editor-naval-layout.py` e `patch-pdf-editor-naval-layout-refine.py`: **ATIVOS NO BUILD**, alteram visual/layout e preservam funções.

### Funções ativas comprovadas

| Função | Entrada | Saída/efeito | MIG |
|---|---|---|---|
| Selecionar arquivos | múltiplos PDF/imagens suportadas | itens de páginas na ordem | MIG-058 |
| Selecionar PDFs | múltiplos PDF | cada página vira item | MIG-058 |
| File drop | PDF/imagens | mesmo importador | MIG-058 |
| Preview | página selecionada | render visual 120 dpi | MIG-058/MIG-108 |
| Miniaturas | páginas | render 58 dpi, max 56×84 | MIG-058/MIG-108 |
| Criar blank | ação UI | página branca 1240×1754 px | MIG-059 |
| Cortar | seleção retangular | crop normalizado | MIG-060 |
| Redimensionar | 75/90/100/110/125% | somente zoom visual | MIG-108 |
| Excluir | página selecionada | remove 1 item | MIG-063 |
| Ordenar | drag-and-drop | altera posição de 1 item | MIG-062 |
| Limpar | confirmação | remove todos os itens | MIG-063 |
| Undo/redo | snapshots | volta/refaz estado | MIG-063 |
| Capa | toggle + imagem custom | capa inicial opcional | MIG-064 |
| Gerar PDF | páginas + capa | novo arquivo `.pdf` | MIG-065/066/067 |

### Funções que não foram inventadas

Não foram encontradas como recursos ativos do V2 final: separar PDF, extrair páginas para arquivos separados, imprimir, compactar como operação própria, converter PDF→imagem, OCR, pesquisar/selecionar texto, abas multi-documento ou navegação first/prev/next/last.

Rotação/flip possuem métodos internos, mas nenhuma chamada ativa para `showTransformMenu()` foi encontrada; por isso `MIG-061` não foi promovido e a UI Python não expõe um botão novo.

## Inventário funcional do Editor de Vídeo ativo

### Ativo x legado

- `video_editor_pyside/main.py`: **ATIVO** — é o source usado pelo PyInstaller e copiado ao portable.
- `VideoEditorScreen.kt`: **ATIVO COMO LAUNCHER** — abre `VideoEditorPySide.exe`.
- `VideoEditorEngine.kt`, `VideoEditorPreview.kt`, `VideoEditorProcess.kt`: **LEGADO/ALTERNATIVO** para esta release; não alimentam o executável aberto pelo launcher final.

### Motor de preview

`PySide6==6.9.1` com `QMediaPlayer` + `QVideoWidget` + `QAudioOutput`, volume inicial 0,85. O Python mantém o mesmo motor. Backend interno de plataforma do QtMultimedia: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**.

### Funções ativas

| Função | Contrato | MIG |
|---|---|---|
| Abrir vídeos | múltiplos `.mp4/.mkv/.webm/.mov/.avi/.m4v` | MIG-069 |
| Probe | FFprobe JSON, timeout 60 s | MIG-070 |
| Preview | QMediaPlayer/QVideoWidget | MIG-071 |
| Áudio/mute | QAudioOutput, volume 0,85 | MIG-072 |
| Timeline | clipes sequenciais, seleção, régua, playhead | MIG-073 |
| Seek | global ↔ clipe/local em ms | MIG-074 |
| Reprodução | voltar 5 s, play/pause, avançar 5 s, sequência automática | MIG-075 |
| Exportar trecho | clipe selecionado → H.264/AAC MP4 | MIG-076 |
| Placeholders | funções inexistentes continuam declaradas como inexistentes | MIG-077 |
| IN/OUT | campos internos existem, mas não há UI manual ativa | MIG-078 |

Não existem no motor ativo thumbnails, zoom funcional, split, delete, duplicate, reorder, drag-and-drop, undo/redo, target-size, concat, progresso/cancelamento de exportação ou seleção de codec/resolução.

## Testes do Passo 12

A matriz `Python migration tests`, run `34726977912`, executou `compileall` e toda a regressão em Windows e Ubuntu no commit de código `d244779b1a0d582090b15d072437f6c2f0e51f78`; ambos os jobs concluíram `success`. No Windows, o pytest executou **132 testes** e todos passaram.

A primeira tentativa revelou dependência nativa real do QtMultimedia no runner Ubuntu (`libpulse.so.0`). O CI foi corrigido adicionando `libpulse0`; o código do editor não foi alterado para esconder a dependência.

Os testes cobrem contratos determinísticos, Qt offscreen, formatos, FFprobe mockado, matemática da timeline, motor QtMultimedia, comando FFmpeg e proteção contra funções inventadas. Não houve sessão humana interativa nem execução do `ffmpeg.exe`/`ffprobe.exe` exatos do bundle da release.

## Validação manual / integração real

Preview/áudio/seek/reprodução sequencial/exportação permanecem `EM TESTE` porque não houve teste humano com vídeos reais e binários do portable aprovado. A precisão real de seek do backend QtMultimedia é **NÃO DETERMINADO PELO CÓDIGO ANALISADO** e deve ser medida no ambiente Windows final.

## Regras permanentes

Os identificadores `MIG-001` a `MIG-111` são permanentes. Não renumerar, reutilizar ou substituir números. Um MIG só vira `APROVADO` após comparação objetiva e validação compatível com sua natureza.
