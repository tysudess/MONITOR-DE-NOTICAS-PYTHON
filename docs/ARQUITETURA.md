# Arquitetura da migração Python

## Fonte da verdade

A migração usa `tysudess/noticias-monitor`, Build SHA `df1701ba5427a04954093e8ebed63f26abb2b2b7`, **mais as transformações executadas por** `.github/workflows/release-v8-extractor-tab-portable.yml`. O destino é `tysudess/MONITOR-DE-NOTICAS-PYTHON`, branch `migration/python-foundation`.

A regra permanente é preservar o motor e o comportamento comprovados. Quando algo não é comprovado: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**.

## Arquitetura atual após o Passo 11

```text
Application
└─ MainWindow (PySide6 QMainWindow)
   ├─ páginas do Monitor migradas no Passo 9
   ├─ Editor de PDF [PdfEditorPage REAL]
   ├─ Extrator de Vídeos [ExtractorPage REAL]
   └─ Editor de Vídeo [placeholder]

PdfEditorPage (PySide6)
   ├─ importação PDF/imagens + file drop
   ├─ preview PDF/imagem
   ├─ miniaturas/lista
   ├─ crop normalizado
   ├─ página em branco
   ├─ excluir/reordenar
   ├─ undo/redo (30 snapshots)
   ├─ zoom/Redimensionar visual
   ├─ capa padrão/custom
   └─ GERAR PDF → PdfEditorModel

PdfEditorModel
   ├─ pypdf: montagem/exportação vetorial
   ├─ pypdfium2/PDFium: renderização de PDF
   ├─ Pillow: imagens/crop/raster
   ├─ data/config.json
   ├─ data/capa_padrao_usuario.png
   ├─ data/capa_padrao.png (opcional)
   └─ resources/pdf-default-cover.b64 (asset original)

ExtractorPage / ExtractorEngine
   ├─ yt-dlp nightly/stable
   ├─ ffmpeg / ffprobe / deno
   ├─ YouTube normal/live
   ├─ Globoplay
   ├─ R7/Record
   └─ fallback HTML
```

## Editor PDF — fonte ativa

A implementação efetivamente executada pelo Dashboard V5 é `PdfEditorScreenV2.kt`. `PdfEditorScreen.kt` é implementação anterior e não foi usada como fonte funcional do Passo 11.

O workflow da release protege a lógica base do V2 e, depois da integração do Extrator, aplica:

- `tools/patch-pdf-editor-naval-layout.py`;
- `tools/patch-pdf-editor-naval-layout-refine.py`.

Esses patches alteram o layout/HUD e validam a permanência das funções do motor; não substituem o PDFBox nem introduzem um motor PDF diferente.

## Motor PDF original

Biblioteca JVM principal:

- Apache PDFBox `3.0.3`, declarado em `desktop/build.gradle.kts`.

Classes/funções usadas no V2:

- `Loader.loadPDF` — abertura de PDFs;
- `PDFRenderer` — preview/rasterização;
- `PDDocument`, `PDPage`, `PDRectangle` — criação do documento final;
- `LayerUtility.importPageAsForm` — incorporação vetorial de página PDF sem transformação;
- `PDPageContentStream` + `Matrix` — escala/posicionamento;
- `LosslessFactory.createFromImage` — páginas rasterizadas.

Imagens usam `ImageIO`, com TwelveMonkeys WebP/TIFF `3.12.0` no classpath.

## Bibliotecas Python escolhidas

| Biblioteca | Versão | Papel no Passo 11 |
|---|---:|---|
| `pypdf` | 6.18.0 | montagem do PDF final e caminho vetorial |
| `pypdfium2` | 5.13.0 | renderização PDF para preview/crop/raster |
| `Pillow` | 12.3.0 | imagens, crop, flip/rotação interna e raster |
| `PySide6` | 6.9.1 | interface e workers Qt |

A escolha foi feita depois do inventário funcional. Não há OCR nem conversor genérico. pypdf é BSD-3-Clause; Pillow é MIT-CMU; pypdfium2 é Apache-2.0/BSD-3-Clause e distribui PDFium sob licença BSD-style. O portable final deverá carregar os avisos/licenças exigidos pelo PDFium e dependências.

## Modelo de páginas

Cada item preserva:

- `kind`: `PDF`, `IMAGE` ou `BLANK`;
- caminho de origem;
- índice de página PDF quando aplicável;
- rotação interna;
- flip horizontal interno;
- crop normalizado;
- `uid` para identidade durante reorder/undo.

A seleção ativa é única. Não há multi-select, Ctrl-select ou Shift-range comprovados no V2 ativo.

## Importação

`Arquivos` aceita múltiplos arquivos:

- `.pdf`;
- `.jpg` / `.jpeg`;
- `.png`;
- `.webp`;
- `.bmp`;
- `.tiff` / `.tif`.

`PDF` aceita múltiplos PDFs. Cada página de cada PDF vira um item separado na sequência. Uma imagem vira um item. File drop usa os mesmos formatos.

PDF protegido por senha não possui prompt nem bypass no original; falha de abertura é exibida como erro. O Python mantém esse comportamento.

## Preview, miniaturas e zoom

- PDF normal: render 120 dpi.
- Miniatura: `renderFinalPage(..., 58)` e redução máxima para 56×84, sem ampliar.
- Zoom: 50% a 300%, passos de 15%.
- `Ajustar`: 100%.
- `Redimensionar`: opções 75%, 90%, 100%, 110%, 125%; **altera somente a escala de visualização**, não as dimensões do PDF.
- Modos visuais: `Miniatural` e `Lista`, conforme o patch final da release.

Não existem controles ativos comprovados de primeira/anterior/próxima/última página, número de página, fit-width ou fit-page; não foram criados.

## Crop

O crop é armazenado normalizado (`x`, `y`, `w`, `h`) e aplicado após a transformação da imagem/página. A seleção gráfica exige área maior que 4 px. No render final, coordenadas são limitadas a 0..1; início usa `floor` e fim usa `ceil`, preservando ao menos 1 pixel.

## Reordenação, exclusão e limpar

A coluna de páginas usa seleção única e drag-and-drop de inserção. O item movido permanece selecionado. Excluir remove somente a página selecionada, sem confirmação e inclusive permite remover a última. `Limpar` pede confirmação e remove todas.

## Undo / redo

Snapshot integral de páginas + índice selecionado, limite de 30 estados. Entram no histórico: importação, criar blank, crop, funções internas de rotação/flip, excluir, reorder e limpar. Zoom e troca de capa não fazem parte do undo.

Atalhos ativos:

- `Ctrl+Z` — undo;
- `Ctrl+Y` — redo;
- `Delete` — excluir selecionada;
- `Ctrl+S` — exportar.

`Ctrl+O` não foi encontrado e não foi inventado.

## Rotação e flip

`PdfEditorScreenV2.kt` contém `showTransformMenu`, `rotateSelected` e `flipSelected`, e o estado/exportador entende esses campos. Porém não foi encontrado caller ativo para `showTransformMenu` nem controle de transformação validado pelo workflow final. O Python mantém suporte interno de estado/exportação, mas **não expõe botão/menu novo**. `MIG-061` permanece pendente até surgir evidência do acionamento ativo na baseline.

## Capa

Ordem comprovada:

1. `data/capa_padrao_usuario.png`, quando configurada;
2. `data/capa_padrao.png`, se existir;
3. recurso original `resources/pdf-default-cover.b64`;
4. fallback gerado, apenas se todos os anteriores falharem.

O recurso `pdf-default-cover.b64` foi copiado literalmente do Build SHA de referência. Capa custom aceita os mesmos formatos de imagem da UI e é convertida para PNG. `data/config.json` guarda `custom_cover: data/capa_padrao_usuario.png`.

## Exportação

O editor sempre monta um novo documento; arquivos de origem não são modificados.

Nome padrão do Save As:

- com capa: `RADAR DE NOTICIAS - MIDIA IMPRESSA.pdf`;
- sem capa: `documento.pdf`.

A extensão `.pdf` é acrescentada se ausente. Política custom de overwrite além do comportamento do diálogo nativo: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**.

### Qualidade

O enum original possui:

- Alta (recomendado): 450 dpi;
- Média: 300 dpi;
- Compacta: 220 dpi.

No layout final da release, o JComboBox de qualidade não é adicionado ao painel visível; por isso o valor efetivo fica no primeiro enum, HIGH/450 dpi. A UI Python também não inventa seletor e exporta no valor ativo HIGH.

### Caminho vetorial

Condição exata: item PDF, `rotation == 0`, `flipX == false`, `crop == null`.

O PDFBox original cria uma página nova de largura fixa `595.276 pt`, altura proporcional ao crop/media box, importa a página como Form XObject e a desenha escalada/centralizada. O Python usa pypdf para reproduzir a mesma geometria. Como `merge_transformed_page` copiava `/Annots`, o Python remove `/Annots` explicitamente para ficar alinhado ao `importPageAsForm` do PDFBox.

A criação de um documento novo significa que metadata do documento de origem, bookmarks/outlines e estruturas de formulário/anotações não são herdados automaticamente pelo fluxo original. O Python não tenta “preservar mais” que o original.

### Caminho raster

Usado para imagens, BLANK e qualquer página transformada. A imagem final é embutida lossless em RGB; largura de página `595.276 pt`, altura proporcional aos pixels. Página PDF transformada é renderizada no DPI da qualidade ativa antes da incorporação.

Não existe compactação genérica separada, divisão de PDF, extração de páginas para arquivos separados, impressão, OCR, busca de texto ou conversão PDF→imagem como recurso ativo.

## Threads

Operações pesadas não são feitas no thread GUI:

- preview/crop: `QThread`;
- exportação: `QThread`;
- miniaturas independentes: `QThreadPool`.

Mutações do modelo e ordem das páginas continuam sequenciais. O ciclo de vida do worker de exportação encerra o `QThread` tanto em sucesso quanto em falha.

## Testes do Passo 11

PDFs/imagens artificiais cobrem:

- importação múltipla e expansão de páginas;
- formatos permitidos;
- página em branco;
- excluir/reorder;
- undo/redo e limite 30;
- zoom/Redimensionar;
- crop normalizado;
- suporte interno de rotação/flip sem botão inventado;
- dimensões de saída de largura fixa;
- ordem final;
- rasterização de página transformada;
- capa custom e persistência;
- PDF protegido sem bypass;
- metadata/annotation behavior;
- original não sobrescrito;
- ausência de split/extract/print/OCR/compress/convert inventados;
- presença dos controles ativos na UI.

A matriz `Python migration tests` executou `compileall` e toda a suíte em Windows e Ubuntu. O run `34725866759` passou nos dois ambientes, com 116 testes no Windows. Qt roda em `offscreen`; isso **não é** validação manual humana do layout.

## Estado após o Passo 11

O placeholder do Editor PDF foi removido da MainWindow e substituído por `PdfEditorPage`. Extrator permanece funcional conforme Passo 10. Editor de Vídeo continua placeholder. Portable final não foi iniciado.

Pendências relevantes:

- inspeção manual humana do Editor PDF em desktop interativo (`MIG-108`);
- `MIG-061` rotação/flip permanece pendente porque o acionamento ativo não foi comprovado;
- portable final/licenças PDFium;
- Editor de Vídeo completo;
- pendências anteriores dos Passos 1–10 não relacionadas ao PDF.
