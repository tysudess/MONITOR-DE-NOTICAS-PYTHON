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

## Regra de segurança

Nenhuma decisão autoriza logar senha, token, cookie, blob DPAPI ou plaintext descriptografado. O Extrator não faz bypass de DRM. Fixtures usam somente dados artificiais.
