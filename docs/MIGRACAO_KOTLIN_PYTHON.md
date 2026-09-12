# Migração Kotlin → Python

## Fonte da verdade

- Repositório original: `tysudess/noticias-monitor`
- Repositório destino: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- Baseline funcional: Build SHA `df1701ba5427a04954093e8ebed63f26abb2b2b7` + transformações do workflow V8.
- Branch de migração: `migration/python-foundation`.

O comportamento comprovado é a fonte da verdade. Lacunas não são preenchidas por suposição. Quando algo não é comprovado: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**.

## Estados permitidos

`PENDENTE`, `EM MIGRAÇÃO`, `EM TESTE`, `APROVADO`, `BLOQUEADO`.

## Estado após o Passo 11

Os Passos 1–10 permanecem preservados. O Passo 11 substitui o placeholder do Editor PDF pela implementação PySide6 real baseada exclusivamente no `PdfEditorScreenV2.kt` ativo da baseline, incluindo o resultado dos patches visuais executados pelo workflow da release.

O Editor PDF Kotlin ativo usa Apache PDFBox `3.0.3` + ImageIO/TwelveMonkeys. O Python usa `pypdf==6.18.0`, `pypdfium2==5.13.0` e `Pillow==12.3.0`, cada biblioteca limitada ao papel necessário para reproduzir o comportamento comprovado.

Não foram adicionados split, extração de páginas para arquivos separados, impressão, OCR, compressão genérica, conversão genérica, múltiplos documentos/abas ou navegação de primeira/anterior/próxima/última página porque essas funções não aparecem como recursos ativos do V2 final.

Editor de Vídeo e portable final não foram iniciados.

## MIG trabalhados no Passo 11

- `MIG-058` — importação PDF/imagens/file drop: `APROVADO`.
- `MIG-059` — página em branco: `APROVADO`.
- `MIG-060` — crop normalizado: `APROVADO`.
- `MIG-061` — rotação/flip: `PENDENTE`; métodos internos existem, mas acionamento ativo na UI final não foi comprovado e não foi inventado.
- `MIG-062` — reordenação drag-and-drop: `APROVADO`.
- `MIG-063` — undo/redo com 30 snapshots: `APROVADO`.
- `MIG-064` — capa padrão/custom: `APROVADO`; o asset `pdf-default-cover.b64` foi copiado literalmente da baseline.
- `MIG-065` — qualidade de exportação: `APROVADO` para o comportamento ativo; enum 450/300/220 preservado e UI final permanece efetivamente em HIGH/450 dpi porque o selector não é exposto no layout final.
- `MIG-066` — exportação vetorial: `APROVADO`.
- `MIG-067` — exportação raster: `APROVADO`.
- `MIG-108` — workspace PySide6 real do Editor PDF: `EM TESTE` até inspeção humana em desktop interativo.
- `MIG-109` — equivalência/regressão automatizada do Passo 11: `APROVADO`.

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
| MIG-108 | UI/PDF | Workspace PySide6 real do Editor PDF | EM TESTE |
| MIG-109 | PDF/Testes | Equivalência e regressão automatizada Passo 11 | APROVADO |

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

## Motor e exportação

PDFBox 3.0.3 é o motor original. O Python reproduz a divisão:

- PDF sem crop/rotação/flip → caminho vetorial;
- imagem, blank ou página transformada → caminho raster.

A página final usa largura fixa de `595.276 pt` e altura proporcional. No caminho vetorial, o conteúdo é escalado/centralizado. No caminho raster, a imagem ocupa a página inteira proporcional.

O documento fonte nunca é alterado. Metadata original e estruturas de documento não são automaticamente herdadas porque o original cria um novo `PDDocument`; testes protegem essa semântica, inclusive ausência de `/Annots` herdado no caminho vetorial.

## Capa e persistência

- `data/config.json`;
- `data/capa_padrao_usuario.png`;
- `data/capa_padrao.png` opcional;
- `resources/pdf-default-cover.b64` copiado literalmente da baseline.

## Testes do Passo 11

Os testes usam somente PDFs/imagens artificiais. Cobrem importação, múltiplas páginas, imagem, blank, crop, reorder, delete, undo/redo, zoom, dimensões, caminho raster/vetorial, capa custom, PDF protegido, preservação do arquivo fonte, metadata/anotações e contrato da GUI.

A workflow `Python migration tests`, run `34725866759`, concluiu `success` em Windows e Ubuntu no commit de código `cea24a89fd30699a1357e113c8256e544a21258c`. No job Windows, o pytest executou **116 testes** e todos passaram.

## Validação manual

Não houve sessão humana interativa com desktop gráfico neste passo. A GUI foi instanciada e testada com Qt `offscreen` nos dois sistemas. Portanto `MIG-108` permanece `EM TESTE` e não é apresentado como validação manual concluída.

## Regras permanentes

Os identificadores `MIG-001` a `MIG-109` são permanentes. Não renumerar, reutilizar ou substituir números. Um MIG só vira `APROVADO` após comparação objetiva e validação compatível com sua natureza.
