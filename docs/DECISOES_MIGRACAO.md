# Decisões de migração

## Decisões anteriores preservadas

As decisões `DEC-001` a `DEC-041` permanecem válidas, permanentes e não são renumeradas. O histórico detalhado permanece rastreável nos commits dos Passos 1 a 9. Resumo:

| DEC | Escopo | Decisão preservada |
|---|---|---|
| DEC-001 | Runtime | Python 3.12.x |
| DEC-002 | UI | PySide6 6.9.1 |
| DEC-003 | Paths | raiz portable centralizada em AppPaths |
| DEC-004 | Binários | não substituir binários externos antes do passo próprio |
| DEC-005 | Git | branch `migration/python-foundation` |
| DEC-006 | SQLite | sqlite3/SQL explícito, sem ORM |
| DEC-007–015 | Dados/matching | preservar contratos, sem repositories/score inventados |
| DEC-016–018 | HTTP/Globoplay | requests/parsing e proxy injetável, fluxos parciais explicitados |
| DEC-019–024 | Automação | scheduler/lanes/clock/ports/cancelamento equivalentes |
| DEC-025–032 | Windows/segurança | proxy, DPAPI, startup, tray, subprocessos e CI Windows |
| DEC-033–041 | UI Passo 9 | QMainWindow/stack, controller fino, catálogo, placeholders, senha segura, QThread, tray, CI Qt e aprovação conservadora |

Nenhuma decisão anterior é revogada pelo Passo 10.

## DEC-042
ID DA DECISÃO: DEC-042  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-043 a MIG-057, MIG-106, MIG-107  
COMPONENTE: Fonte da verdade do Extrator  
COMPORTAMENTO ORIGINAL: o arquivo estático `ExtractorVideoEngine.kt` no Build SHA ainda é transformado pelo workflow antes da compilação. `integrate-v8-extractor-tab.py`, `patch-extractor-generic-html.py`, seus patches encadeados e `patch-extractor-hidden-process.py` alteram roteamento, live, persistência, retry, R7, paths, cancelamento e subprocessos.  
DECISÃO: portar o **resultado efetivo do Build SHA `df1701...` + patches executados pela workflow**, e não o HEAD atual do branch nem o source Kotlin estático isolado.  
JUSTIFICATIVA: somente essa composição corresponde à release aprovada.  
EVIDÊNCIA: `.github/workflows/release-v8-extractor-tab-portable.yml`, Build SHA `df1701ba5427a04954093e8ebed63f26abb2b2b7`.  
IMPACTO: evita regressão para motor intermediário.  
REVERSÍVEL: Não sem mudar a baseline.

## DEC-043
ID DA DECISÃO: DEC-043  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-043 a MIG-054  
COMPONENTE: Motor de download  
COMPORTAMENTO ORIGINAL: o Extrator combina yt-dlp nightly, yt-dlp stable, FFmpeg, FFprobe, Deno, fallbacks HTML próprios e lógica própria de HLS/live.  
DECISÃO: manter essa composição. Python coordena os mesmos executáveis/argumentos e porta apenas a lógica que era Kotlin; não substituir tudo por biblioteca Python ou serviço alternativo.  
JUSTIFICATIVA: requisito de equivalência do motor já funcional.  
EVIDÊNCIA: `ExtractorVideoEngine.kt`, `YouTubeLiveSnapshot.kt`, fallbacks HTML e workflow.  
IMPACTO: os cinco binários continuam dependências externas da distribuição.  
REVERSÍVEL: Não sem alterar comportamento.

## DEC-044
ID DA DECISÃO: DEC-044  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-043, MIG-044, MIG-045  
COMPONENTE: Presets e retry  
COMPORTAMENTO ORIGINAL: cinco qualidades possuem selector primário e selector compatível. O retry compatível só ocorre para falhas de formato/player específicas, não autenticação.  
DECISÃO: copiar labels/selectors/limits literalmente e restringir retry às mesmas mensagens (`403`, forbidden, requested format, format unavailable, qualidade indisponível, player response).  
JUSTIFICATIVA: ampliar retry mudaria tentativas, erros e tráfego.  
EVIDÊNCIA: `EXTRACTOR_QUALITIES` + `patch-extractor-compat-retry.py`.  
IMPACTO: comportamento determinístico testável.  
REVERSÍVEL: Não sem mudar equivalência.

## DEC-045
ID DA DECISÃO: DEC-045  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-046, MIG-047, MIG-048  
COMPONENTE: Roteamento e fallback HTML  
COMPORTAMENTO ORIGINAL: YouTube, Globoplay, R7/Record e genérico têm caminhos distintos; HTML fallback testa no máximo 15 candidatos e preserva referer/UA.  
DECISÃO: manter quatro rotas separadas e os limites/filtros específicos de cada parser.  
JUSTIFICATIVA: unificar em parser genérico perderia regras da release.  
EVIDÊNCIA: `DirectMediaHtmlFallback.kt`, `R7HtmlFallback.kt`, `GloboplayHtmlFallback.kt`, patches de integração.  
IMPACTO: parsers continuam pequenos e fonte-específicos.  
REVERSÍVEL: Somente com prova de equivalência.

## DEC-046
ID DA DECISÃO: DEC-046  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-051, MIG-052, MIG-053, MIG-054  
COMPONENTE: YouTube Live  
COMPORTAMENTO ORIGINAL: apenas live ativa usa snapshot. O motor congela a playlist HLS no ponto atual, valida janela DVR, tenta remux e depois H.264/AAC; fallback yt-dlp usa `--download-sections` até o ponto atual.  
DECISÃO: portar o snapshot HLS em Python e proibir fallback ilimitado quando o início da live não puder ser determinado. `post_live` segue fluxo normal.  
JUSTIFICATIVA: seguir os patches finais da release e impedir download que acompanhe live indefinidamente.  
EVIDÊNCIA: `YouTubeLiveSnapshot.kt`, `patch-extractor-live-current-point.py`, `patch-extractor-youtube-live-status.py`.  
IMPACTO: HLS próprio permanece parte essencial do motor.  
REVERSÍVEL: Não sem mudar comportamento aprovado.

## DEC-047
ID DA DECISÃO: DEC-047  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-049, MIG-050  
COMPONENTE: Sessão/login Globoplay  
COMPORTAMENTO ORIGINAL: cookies Netscape são protegidos por DPAPI CurrentUser; login ocorre em helper Chromium/PySide6 empacotado, cuja senha nunca é recebida pelo Monitor.  
DECISÃO: reutilizar `DpapiTextStore` nativo do Passo 8 para o mesmo arquivo `globoplay.session.dpapi`; implementar o launcher do helper, mas **não inventar outro navegador ou login** se `GloboplayLoginHelper.exe` ainda não estiver no pacote.  
JUSTIFICATIVA: o Passo 10 exclui portable final/binário helper.  
EVIDÊNCIA: `GloboplaySessionStore.kt`, `GloboplayLoginWindow.kt`.  
IMPACTO: sessão segura está migrada; login real fica `BLOQUEADO` até o helper ser empacotado.  
REVERSÍVEL: launcher pode ser substituído apenas por mecanismo comprovadamente equivalente.

## DEC-048
ID DA DECISÃO: DEC-048  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-055, MIG-106  
COMPONENTE: Threading e cancelamento  
COMPORTAMENTO ORIGINAL: download roda fora da UI; cancelamento invalida callbacks/resultados antigos e encerra árvore do subprocesso.  
DECISÃO: `ExtractorPage` usa `QThread`, token de operação e `HiddenProcessRunner.destroy_tree`.  
JUSTIFICATIVA: preservar responsividade e impedir callback atrasado de alterar nova operação.  
EVIDÊNCIA: `patch-extractor-cancel-token.py`, `patch-extractor-hidden-process.py`.  
IMPACTO: nenhum download roda no thread principal.  
REVERSÍVEL: Não sem manter os dois níveis de cancelamento.

## DEC-049
ID DA DECISÃO: DEC-049  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-040, MIG-044 a MIG-053  
COMPONENTE: Proxy do Extrator  
COMPORTAMENTO ORIGINAL: o engine aceita proxy, mas `patch-extractor-portable-state.py` remove a UI própria e a release final chama `engine.download(..., "")` e `GloboplayLoginWindow(..., "")`; comentário indica conexão futura do proxy geral.  
DECISÃO: a tela Python do Passo 10 também envia proxy vazio. **Não conectar o proxy geral do Monitor ao Extrator nesta etapa.**  
JUSTIFICATIVA: conectar agora seria melhoria não presente na release aprovada.  
EVIDÊNCIA: `patch-extractor-portable-state.py`.  
IMPACTO: suporte interno de proxy permanece no engine para compatibilidade, mas não é ativado pela UI.  
REVERSÍVEL: Sim se passo futuro possuir evidência/decisão explícita.

## DEC-050
ID DA DECISÃO: DEC-050  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-057  
COMPONENTE: Atualizador yt-dlp  
COMPORTAMENTO ORIGINAL: baixa stable oficial, valida >1 MB e `--version`, preserva backup, substitui, valida instalação e só então apaga backup; em falha restaura/preserva.  
DECISÃO: manter o fluxo e nomes `yt-dlp.update.tmp.exe` / `yt-dlp.backup.exe`, timeouts e User-Agent comprovados.  
JUSTIFICATIVA: atualização não pode destruir o executável funcional.  
EVIDÊNCIA: `YtDlpUpdater.kt`.  
IMPACTO: updater isolado em `extractor/updater.py`.  
REVERSÍVEL: Não sem preservar segurança equivalente.

## DEC-051
ID DA DECISÃO: DEC-051  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-106, MIG-107  
COMPONENTE: Aprovação/testes do Passo 10  
COMPORTAMENTO ORIGINAL: funcionalidades dependem de sites externos e cinco binários presentes no portable.  
DECISÃO: CI Windows/Ubuntu aprova somente contratos determinísticos, UI e regressão. Downloads reais de YouTube/R7/Globoplay/live permanecem `EM TESTE` enquanto a etapa não possuir o bundle final dos binários/helper.  
JUSTIFICATIVA: não confundir mock/comando construído com teste real de mídia.  
EVIDÊNCIA: escopo do Passo 10 exclui portable final.  
IMPACTO: status conservadores mesmo com CI verde.  
REVERSÍVEL: status avança após teste de integração real controlado.

## DEC-052
ID DA DECISÃO: DEC-052  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-058 a MIG-067, MIG-108, MIG-109  
COMPONENTE: Fonte da verdade do Editor PDF  
COMPORTAMENTO ORIGINAL: `DashboardV5Main.kt` executa `PdfEditorScreenV2`; `PdfEditorScreen.kt` é implementação anterior. A release aplica somente os patches visuais `patch-pdf-editor-naval-layout.py` e `patch-pdf-editor-naval-layout-refine.py` sobre o V2.  
DECISÃO: migrar exclusivamente `PdfEditorScreenV2` + resultado dos dois patches visuais do workflow do Build SHA `df1701...`. Não misturar funções do editor legado.  
JUSTIFICATIVA: essa é a implementação efetivamente usada pela release aprovada.  
EVIDÊNCIA: Dashboard V5, workflow V8 e validações do PDF.  
IMPACTO: reduz risco de introduzir funções inexistentes no produto final.  
REVERSÍVEL: Não sem mudar a baseline.

## DEC-053
ID DA DECISÃO: DEC-053  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-058, MIG-060, MIG-064, MIG-066, MIG-067  
COMPONENTE: Bibliotecas PDF Python  
COMPORTAMENTO ORIGINAL: PDFBox 3.0.3 (`PDDocument`, `PDFRenderer`, `LayerUtility`, `LosslessFactory`) + ImageIO/TwelveMonkeys WebP/TIFF.  
DECISÃO: usar `pypdf==6.18.0` para montagem/exportação vetorial, `pypdfium2==5.13.0` para renderização PDF e `Pillow==12.3.0` para imagens/crop/raster.  
JUSTIFICATIVA: não existe uma única biblioteca Python equivalente ao conjunto PDFBox+ImageIO sem introduzir licença forte; a combinação reproduz as responsabilidades observadas.  
LICENÇAS: pypdf BSD-3-Clause; Pillow MIT-CMU; pypdfium2 Apache-2.0/BSD-3-Clause e PDFium BSD-style. O portable final deverá incluir os avisos/licenças de PDFium e dependências.  
IMPACTO: o motor fica modular sem OCR/conversores não existentes.  
REVERSÍVEL: somente mediante equivalência comprovada.

## DEC-054
ID DA DECISÃO: DEC-054  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-061  
COMPONENTE: Rotação e espelhamento  
COMPORTAMENTO ORIGINAL: o V2 contém `showTransformMenu`, `rotateSelected` e `flipSelected` e o modelo/exportador entende `rotation`/`flipX`; porém não foi encontrado caller ativo para `showTransformMenu` nem controle exigido pelo workflow final.  
DECISÃO: manter suporte interno de estado/exportação, mas **não criar botão/menu de rotação/flip na UI Python** e não promover MIG-061.  
JUSTIFICATIVA: expor uma função interna dormente como recurso visível seria inventar funcionalidade.  
EVIDÊNCIA: busca completa no `PdfEditorScreenV2.kt` + lista de controles validada pelo workflow.  
IMPACTO: MIG-061 permanece `PENDENTE`.  
REVERSÍVEL: pode avançar somente com evidência de acionamento real na baseline.

## DEC-055
ID DA DECISÃO: DEC-055  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-065, MIG-066, MIG-067  
COMPONENTE: Exportação vetorial x raster  
COMPORTAMENTO ORIGINAL: página PDF sem crop/rotação/flip usa `LayerUtility.importPageAsForm` em nova página de largura 595.276 pt; qualquer página transformada, imagem ou blank é rasterizada e embutida via `LosslessFactory`.  
DECISÃO: reproduzir a bifurcação. `pypdf.merge_transformed_page` é usado somente para conteúdo vetorial e `/Annots` é removido explicitamente, porque o merge do pypdf copiava anotações que o `importPageAsForm` original não incorpora. Raster usa RGB lossless/Flate.  
JUSTIFICATIVA: preservar conteúdo e dimensões sem adicionar estruturas que o PDFBox original não copia.  
EVIDÊNCIA: `appendVector`, `appendRaster`, `renderFinalPage` e teste que detectou `/Annots` na primeira tentativa Python.  
IMPACTO: metadata original, bookmarks/forms/anotações não são herdados automaticamente no novo documento, conforme o fluxo original de criação de `PDDocument`.  
REVERSÍVEL: Não sem mudar o resultado estrutural.

## DEC-056
ID DA DECISÃO: DEC-056  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-058, MIG-060, MIG-062, MIG-108  
COMPONENTE: Preview, miniaturas e zoom  
COMPORTAMENTO ORIGINAL: preview PDF usa render 120 dpi; miniatura usa render final 58 dpi e escala máxima 56×84; zoom varia de 50% a 300% em passos de 15%; Ajustar = 100%; Redimensionar oferece 75/90/100/110/125% e altera somente visualização. Seleção é única.  
DECISÃO: manter esses valores e semânticas literalmente. Não adicionar navegação primeira/anterior/próxima/última nem fit-width/fit-page, porque não existem no V2 ativo.  
JUSTIFICATIVA: “Redimensionar” não deve ser reinterpretado como alteração real do PDF.  
IMPACTO: preview em PDFium/PySide6 mantém o mesmo contrato funcional.  
REVERSÍVEL: Não sem mudar UX comprovada.

## DEC-057
ID DA DECISÃO: DEC-057  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-064  
COMPONENTE: Capa padrão/custom  
COMPORTAMENTO ORIGINAL: ordem `data/capa_padrao_usuario.png` → `data/capa_padrao.png` → recurso `/pdf-default-cover.b64` → fallback gerado. Configuração usa `data/config.json` com `custom_cover`.  
DECISÃO: copiar literalmente o `pdf-default-cover.b64` da baseline para `resources/`, preservar a mesma ordem e salvar capa custom como PNG em `data/capa_padrao_usuario.png`.  
JUSTIFICATIVA: gerar uma capa “parecida” seria perda visual evitável.  
IMPACTO: asset original passa a fazer parte do projeto Python.  
REVERSÍVEL: Não sem perder equivalência.

## DEC-058
ID DA DECISÃO: DEC-058  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-063, MIG-108  
COMPONENTE: Estado/undo/redo e threads  
COMPORTAMENTO ORIGINAL: undo/redo é snapshot integral de páginas+seleção, máximo 30; preview/exportações pesadas não devem bloquear a UI.  
DECISÃO: preservar snapshots e ordem síncrona das mutações; usar `QThread` para preview/exportação e `QThreadPool` apenas para miniaturas independentes. Não paralelizar mutações/reordenação/exportação de páginas.  
JUSTIFICATIVA: responsividade sem alterar a ordem/resultados.  
IMPACTO: Ctrl+Z/Ctrl+Y/Delete/Ctrl+S permanecem ativos.  
REVERSÍVEL: Não sem manter semântica equivalente.

## DEC-059
ID DA DECISÃO: DEC-059  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-066, MIG-067  
COMPONENTE: Salvamento/proteção do original  
COMPORTAMENTO ORIGINAL: o editor não edita o arquivo fonte em lugar; monta estado em memória e gera novo PDF por JFileChooser. Nome padrão é `RADAR DE NOTICIAS - MIDIA IMPRESSA.pdf` com capa, senão `documento.pdf`; `.pdf` é acrescentado quando necessário.  
DECISÃO: usar diálogo Save As equivalente e nunca modificar as entradas. Política custom de sobrescrita além do comportamento do diálogo nativo: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**.  
JUSTIFICATIVA: não inventar overwrite/renome automático.  
IMPACTO: testes verificam que o arquivo fonte permanece byte a byte inalterado.  
REVERSÍVEL: Não sem mudar segurança do original.

## DEC-060
ID DA DECISÃO: DEC-060  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-108, MIG-109  
COMPONENTE: Critério de aprovação do Passo 11  
COMPORTAMENTO ORIGINAL: editor desktop interativo Swing/PDFBox.  
DECISÃO: testes Qt offscreen Windows/Ubuntu e PDFs artificiais controlados podem aprovar contratos determinísticos e motor; a integração visual `MIG-108` permanece `EM TESTE` até inspeção humana em desktop interativo. Não declarar offscreen como “teste manual”.  
JUSTIFICATIVA: separar regressão automatizada de validação humana real.  
IMPACTO: MIG-109 pode ser `APROVADO` com CI verde; MIG-108 permanece conservador.  
REVERSÍVEL: status avança após teste manual real.

## Regra de segurança

Nenhuma decisão autoriza logar senha, token, cookie, blob DPAPI, plaintext descriptografado ou conteúdo sensível dos PDFs. O Extrator não faz bypass de DRM. PDFs de teste são artificiais e não pessoais.
