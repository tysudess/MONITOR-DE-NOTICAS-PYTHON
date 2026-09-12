# Decisões de migração

## DEC-001
ID DA DECISÃO: DEC-001  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-001, MIG-081  
COMPONENTE: Runtime Python  
COMPORTAMENTO ORIGINAL: O build V8 aprovado usa Python 3.12 para empacotar o Editor PySide6.  
DECISÃO: Adotar Python 3.12.x.  
JUSTIFICATIVA: Preservar a linha de runtime comprovada.  
EVIDÊNCIA NO KOTLIN: workflow da release V8 / Build SHA `df1701ba5427a04954093e8ebed63f26abb2b2b7`.  
IMPACTO: `requires-python >=3.12,<3.13`.  
REVERSÍVEL: Sim.

## DEC-002
ID DA DECISÃO: DEC-002  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-068 a MIG-077, MIG-081  
COMPONENTE: Toolkit de UI  
COMPORTAMENTO ORIGINAL: Editor final usa PySide6 6.9.1.  
DECISÃO: Manter PySide6 6.9.1.  
JUSTIFICATIVA: Não substituir toolkit já validado.  
EVIDÊNCIA NO KOTLIN: workflow/release V8.  
IMPACTO: Fundação Qt.  
REVERSÍVEL: Sim, mediante nova evidência.

## DEC-003
ID DA DECISÃO: DEC-003  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-002, MIG-003  
COMPONENTE: Paths  
COMPORTAMENTO ORIGINAL: Portable resolve dados relativamente à aplicação.  
DECISÃO: Centralizar em `AppPaths`, nunca CWD.  
JUSTIFICATIVA: Preservar comportamento portable.  
EVIDÊNCIA NO KOTLIN: `PortablePaths`/`Context.filesDir`.  
IMPACTO: caminhos centrais.  
REVERSÍVEL: Sim.

## DEC-004
ID DA DECISÃO: DEC-004  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-082  
COMPONENTE: Binários externos  
COMPORTAMENTO ORIGINAL: Portable contém FFmpeg/FFprobe e demais binários em `bin`.  
DECISÃO: Não baixar/substituir binários antes do passo próprio.  
JUSTIFICATIVA: evitar versão não comprovada.  
EVIDÊNCIA NO KOTLIN: workflow V8.  
IMPACTO: dependência permanece pendente.  
REVERSÍVEL: Sim.

## DEC-005
ID DA DECISÃO: DEC-005  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-001  
COMPONENTE: Git  
COMPORTAMENTO ORIGINAL: repositório destino estava vazio.  
DECISÃO: bootstrap mínimo em `main` e desenvolvimento em `migration/python-foundation`.  
JUSTIFICATIVA: necessidade técnica de commit-base.  
EVIDÊNCIA: estado observado do repositório destino.  
IMPACTO: isolamento da migração.  
REVERSÍVEL: Sim.

## DEC-006
ID DA DECISÃO: DEC-006  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-005 a MIG-013  
COMPONENTE: SQLite Python  
COMPORTAMENTO ORIGINAL: SQL explícito via sqlite-jdbc, WAL e busy timeout 5000.  
DECISÃO: usar `sqlite3` padrão, SQL explícito e `SQLiteConnection`, sem ORM.  
JUSTIFICATIVA: tradução direta.  
EVIDÊNCIA NO KOTLIN: `DesktopNewsDb.kt`, `DesktopVideoDb.kt`.  
IMPACTO: nenhuma dependência externa de banco.  
REVERSÍVEL: Sim.

## DEC-007
ID DA DECISÃO: DEC-007  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-005 a MIG-013  
COMPONENTE: DAO x repository  
COMPORTAMENTO ORIGINAL: repositories também executam rede/coletores.  
DECISÃO: Passo 4 migrou somente `NewsDb`/`VideoDb`.  
JUSTIFICATIVA: evitar repository parcial inventado.  
EVIDÊNCIA NO KOTLIN: responsabilidades dos arquivos ativos.  
IMPACTO: repositories completos permanecem futuros.  
REVERSÍVEL: Sim.

## DEC-008
ID DA DECISÃO: DEC-008  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-005 a MIG-013  
COMPONENTE: Banco real  
COMPORTAMENTO ORIGINAL: bancos runtime não são versionados.  
DECISÃO: fixtures SQLite temporárias e MIG em `EM TESTE` até banco real.  
JUSTIFICATIVA: não fingir confronto inexistente.  
EVIDÊNCIA NO KOTLIN: caminhos e DAOs da baseline.  
IMPACTO: aprovação final adiada.  
REVERSÍVEL: Sim.

## DEC-009
ID DA DECISÃO: DEC-009  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-013, MIG-025  
COMPONENTE: VideoMatchPolicy  
COMPORTAMENTO ORIGINAL: reparo de banco chama `VideoMatchPolicy.phraseMatches`.  
DECISÃO: no Passo 4 foi portada a política mínima necessária.  
JUSTIFICATIVA: MIG-013 depende dela.  
EVIDÊNCIA NO KOTLIN: `DesktopVideoDb.kt`, `VideoMatchPolicy.kt`.  
IMPACTO: Passo 5 agora valida e conclui MIG-025.  
REVERSÍVEL: Sim.

## DEC-010
ID DA DECISÃO: DEC-010  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-019, MIG-020, MIG-025  
COMPONENTE: Matchers separados  
COMPORTAMENTO ORIGINAL: `NewsRepository.subjectMatches`, `VideoMatchPolicy.phraseMatches` e `VideoRepository.phraseMatches` não possuem semântica idêntica.  
DECISÃO: manter implementações separadas.  
JUSTIFICATIVA: notícias não usam flexões; vídeo usa flexões/7 de Setembro; frase vazia é `false` no `VideoMatchPolicy` e `true` no matcher privado do `VideoRepository`.  
EVIDÊNCIA NO KOTLIN: `NewsRepository.kt`, `VideoMatchPolicy.kt`, `VideoRepository.kt`.  
IMPACTO: não existe um matcher genérico único.  
REVERSÍVEL: Não sem alterar comportamento.

## DEC-011
ID DA DECISÃO: DEC-011  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-019, MIG-020, MIG-025, MIG-084, MIG-085  
COMPONENTE: Normalização Unicode/regex  
COMPORTAMENTO ORIGINAL: JVM usa NFD, remove `\p{Mn}+`, troca `[^a-z0-9]+` por espaço e aplica trim.  
DECISÃO: em Python usar `unicodedata.normalize("NFD")`, remover caracteres `category == "Mn"` e aplicar `re.sub(r"[^a-z0-9]+", " ", ...)`.  
JUSTIFICATIVA: Python `re` não implementa `\p{Mn}` nativamente; a adaptação preserva o resultado.  
EVIDÊNCIA NO KOTLIN: normalizadores de `NewsRepository`, `VideoRepository` e `VideoMatchPolicy`.  
IMPACTO: mesma equivalência de acentos/case nos golden cases.  
REVERSÍVEL: Sim, desde que resultados permaneçam equivalentes.

## DEC-012
ID DA DECISÃO: DEC-012  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-024, MIG-003  
COMPONENTE: VideoTermStore  
COMPORTAMENTO ORIGINAL: termos de vídeo são persistidos em SharedPreferences com chaves `video_terms_v400*`.  
DECISÃO: não implementar persistência do VideoTermStore neste passo; portar somente a função pura de limpeza/ordenação. Marcar MIG-024 `BLOQUEADO` até MIG-003.  
JUSTIFICATIVA: não inventar storage temporário diferente.  
EVIDÊNCIA NO KOTLIN: `VideoTermStore.kt`.  
IMPACTO: regra conceitual testável; persistência ainda ausente.  
REVERSÍVEL: Sim.

## DEC-013
ID DA DECISÃO: DEC-013  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-032, MIG-085  
COMPONENTE: Canonicalização de URL  
COMPORTAMENTO ORIGINAL: `java.net.URI` canonicaliza YouTube e remove query/fragment de URLs não-YouTube.  
DECISÃO: usar `urllib.parse.urlsplit/urlunsplit` somente como adaptação sintática, preservando a mesma saída.  
JUSTIFICATIVA: equivalente padrão Python sem biblioteca externa.  
EVIDÊNCIA NO KOTLIN: `VideoRepository.canonicalizeUrl`.  
IMPACTO: golden cases protegem YouTube `/watch`, `/shorts`, `/live`, `youtu.be` e URL normal.  
REVERSÍVEL: Sim, se equivalência for mantida.

## DEC-014
ID DA DECISÃO: DEC-014  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-084  
COMPONENTE: Prioridade Globoplay  
COMPORTAMENTO ORIGINAL: `prioritizeGloboplayCandidates` ordena primeiro candidatos com match superficial de termo/demanda e preserva a ordem original como desempate.  
DECISÃO: reproduzir como ordenação estável booleana, sem pontuação adicional.  
JUSTIFICATIVA: não inventar score.  
EVIDÊNCIA NO KOTLIN: `VideoRepository.kt`.  
IMPACTO: matched primeiro, ordem original dentro dos grupos.  
REVERSÍVEL: Não sem alterar resultado.

## DEC-015
ID DA DECISÃO: DEC-015  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-017 a MIG-020, MIG-025, MIG-032, MIG-084, MIG-085  
COMPONENTE: Escopo do Passo 5  
COMPORTAMENTO ORIGINAL: as regras puras estão dentro dos repositories, mas rede/coletores são responsabilidades adicionais.  
DECISÃO: extrair somente regras determinísticas para `matching/`; não iniciar HTTP, scraping, scheduler ou UI.  
JUSTIFICATIVA: permite equivalência isolada sem criar comportamento acima da camada.  
EVIDÊNCIA NO KOTLIN: ordem e funções privadas dos repositories ativos.  
IMPACTO: coletores continuam pendentes.  
REVERSÍVEL: Sim.

## DEC-016
ID DA DECISÃO: DEC-016  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-015, MIG-021, MIG-027 a MIG-031, MIG-086, MIG-087  
COMPONENTE: HTTP e parsing HTML  
COMPORTAMENTO ORIGINAL: Kotlin usa HttpURLConnection/Jsoup com contratos próprios.  
DECISÃO: usar requests + BeautifulSoup preservando endpoints, headers, timeouts, redirects e limites.  
JUSTIFICATIVA: adaptação Python sem mudar estratégia.  
EVIDÊNCIA NO KOTLIN: repositories e coletores ativos.  
IMPACTO: dependências HTTP do Passo 6.  
REVERSÍVEL: Sim, se equivalência for mantida.

## DEC-017
ID DA DECISÃO: DEC-017  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-087, MIG-040  
COMPONENTE: Transporte injetável e proxy  
COMPORTAMENTO ORIGINAL: proxy é aplicado externamente pelo Controller/JVM.  
DECISÃO: HttpClient aceita proxies injetados, sem configuração/credenciais/UI.  
JUSTIFICATIVA: não antecipar MIG-040.  
EVIDÊNCIA NO KOTLIN: DesktopControllerV5 e coletores.  
IMPACTO: MIG-040 permanece PENDENTE.  
REVERSÍVEL: Sim.

## DEC-018
ID DA DECISÃO: DEC-018  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-027, MIG-028  
COMPONENTE: Aprovação parcial Globoplay Edições/Trechos  
COMPORTAMENTO ORIGINAL: catálogo/limites específicos por fonte.  
DECISÃO: manter EM TESTE até confronto integral do catálogo.  
JUSTIFICATIVA: não aprovar cobertura parcial.  
EVIDÊNCIA NO KOTLIN: GloboplayEditionCollector.kt e GloboplayTrechosCollector.kt.  
IMPACTO: aprovação final adiada.  
REVERSÍVEL: Sim após equivalência integral.

## DEC-019
ID DA DECISÃO: DEC-019  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-035 a MIG-038, MIG-088  
COMPONENTE: Engine de scheduling Desktop  
COMPORTAMENTO ORIGINAL: `DesktopControllerV5` usa `CoroutineScope(SupervisorJob()+Dispatchers.Default)`, loop com `delay(30_000L)`, `newsJob/newsBusy` e `videoJob/videoBusy` separados.  
DECISÃO: Python usa uma thread de loop + executor serial para notícias/demandas + executor serial independente para vídeos.  
JUSTIFICATIVA: preserva a topologia e evita bloquear futura UI sem paralelizar fontes.  
EVIDÊNCIA NO KOTLIN: `DesktopControllerV5.automationLoop`, `searchNews`, `searchAllDemands`, `searchVideos`.  
IMPACTO: notícias/demandas são mutuamente exclusivas; vídeos podem coexistir.  
REVERSÍVEL: Sim, desde que a topologia permaneça equivalente.

## DEC-020
ID DA DECISÃO: DEC-020  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-038, MIG-088  
COMPONENTE: Relógio/timezone  
COMPORTAMENTO ORIGINAL: vídeos usam `LocalDateTime.now()` e formatação local `HH:mm`; não há conversão UTC.  
DECISÃO: runtime Python usa datetime local do sistema; abstração de relógio existe apenas para testes determinísticos.  
JUSTIFICATIVA: testar agendamento sem esperar horas sem alterar regra.  
EVIDÊNCIA NO KOTLIN: `DesktopControllerV5.automationLoop`.  
IMPACTO: nenhuma timezone explícita adicionada.  
REVERSÍVEL: Sim.

## DEC-021
ID DA DECISÃO: DEC-021  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-088, MIG-014, MIG-016, MIG-022, MIG-023, MIG-026, MIG-033  
COMPONENTE: Fronteira AutomationService ↔ repositories  
COMPORTAMENTO ORIGINAL: Controller chama `NewsRepository` e `VideoRepository`; não reimplementa collectors/matching/SQL.  
DECISÃO: `AutomationService` recebe protocolos `NewsRunner`/`VideoRunner`; não criar repository parcial dentro do scheduler.  
JUSTIFICATIVA: os business repositories completos ainda não existem no destino e inventá-los violaria a separação dos passos.  
EVIDÊNCIA NO KOTLIN: `DesktopControllerV5`; no destino, `repositories/__init__.py` registra a ausência dos repositories completos.  
IMPACTO: scheduling é testável, integração end-to-end permanece pendente.  
REVERSÍVEL: Sim.

## DEC-022
ID DA DECISÃO: DEC-022  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-035 a MIG-038, MIG-087  
COMPONENTE: Retry e timeout da automação  
COMPORTAMENTO ORIGINAL: o loop Desktop não adiciona retry nem timeout global de job.  
DECISÃO: não adicionar retry externo ou timeout genérico no AutomationService; manter retries/timeouts nas camadas onde já existem.  
JUSTIFICATIVA: evitar retry duplicado e valores inventados.  
EVIDÊNCIA NO KOTLIN: `DesktopControllerV5.automationLoop` e métodos de busca.  
IMPACTO: uma falha do runner encerra aquela execução e o próximo disparo segue a cadência persistida.  
REVERSÍVEL: Não sem alterar comportamento.

## DEC-023
ID DA DECISÃO: DEC-023  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-003, MIG-024, MIG-035 a MIG-038  
COMPONENTE: SharedPreferences Desktop  
COMPORTAMENTO ORIGINAL: `data/prefs/monitor_prefs.properties`, `java.util.Properties`, gravação temporária e StringSet Base64 URL-safe sem padding separado por `|`.  
DECISÃO: implementar os tipos/chaves necessários em Python e manter MIG-003 `EM TESTE` até confronto com arquivo real produzido pela JVM.  
JUSTIFICATIVA: a semântica utilizada pela automação está coberta, mas equivalência byte a byte de escaping/comentários de `Properties.store` ainda não foi provada.  
EVIDÊNCIA NO KOTLIN: `desktop/src/main/kotlin/android/content/Context.kt`.  
IMPACTO: configurações e timestamps do scheduler persistem; VideoTermStore ainda não é aprovado.  
REVERSÍVEL: Sim.

## DEC-024
ID DA DECISÃO: DEC-024  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-042, MIG-088  
COMPONENTE: Cancelamento  
COMPORTAMENTO ORIGINAL: Kotlin cancela o Job/coroutine e trata `CancellationException`.  
DECISÃO: Python usa token cooperativo, preserva guards e textos de estado, mas MIG-042 fica `EM TESTE` até os repositories/HTTP consumirem o token entre operações.  
JUSTIFICATIVA: `Future.cancel()` não interrompe com segurança uma função Python já executando; fingir cancelamento forçado mudaria a semântica.  
EVIDÊNCIA NO KOTLIN: `stopNewsSearch`, `stopVideoSearch` e catches de `CancellationException`.  
IMPACTO: cancelamento de fakes/etapas cooperativas é comprovado; I/O bloqueante real ainda precisa validação.  
REVERSÍVEL: Sim.
