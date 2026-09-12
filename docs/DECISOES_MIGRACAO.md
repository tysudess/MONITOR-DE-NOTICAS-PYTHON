# Decisões de migração

## Decisões anteriores preservadas

As decisões `DEC-001` a `DEC-032` continuam válidas e não são renumeradas. Resumo permanente:

| DEC | Escopo | Decisão preservada |
|---|---|---|
| DEC-001 | Runtime | Python 3.12.x |
| DEC-002 | UI toolkit | PySide6 6.9.1 |
| DEC-003 | Paths | raiz portable centralizada em AppPaths |
| DEC-004 | Binários | não substituir binários externos antes do passo próprio |
| DEC-005 | Git | desenvolvimento em `migration/python-foundation` |
| DEC-006 | SQLite | `sqlite3`, SQL explícito, sem ORM |
| DEC-007 | DAO/repository | não criar repository parcial no Passo 4 |
| DEC-008 | Banco real | fixtures temporárias; MIG de DB continuam EM TESTE |
| DEC-009 | VideoMatchPolicy | política mínima portada e validada no Passo 5 |
| DEC-010 | Matchers | manter matchers de notícia/vídeo separados |
| DEC-011 | Unicode | NFD + remoção Mn + regex equivalente |
| DEC-012 | VideoTermStore | persistência permanece bloqueada até contrato completo |
| DEC-013 | URLs | canonicalização com urllib mantendo saída |
| DEC-014 | Globoplay | prioridade estável booleana, sem score inventado |
| DEC-015 | Passo 5 | extrair somente regras determinísticas |
| DEC-016 | HTTP/parsing | requests + BeautifulSoup preservando contratos |
| DEC-017 | Proxy | HttpClient aceita proxies por injeção |
| DEC-018 | Globoplay parcial | Edições/Trechos permanecem EM TESTE |
| DEC-019 | Scheduler | thread de loop + lanes seriais equivalentes |
| DEC-020 | Relógio | datetime local do sistema |
| DEC-021 | Automation/repositories | portas NewsRunner/VideoRunner |
| DEC-022 | Retry/timeout | AutomationService não adiciona retry/timeout global |
| DEC-023 | SharedPreferences | properties + StringSet compatível |
| DEC-024 | Cancelamento | token cooperativo |
| DEC-025 | Proxy Desktop | ProxySettings preservando defaults/contrato |
| DEC-026 | Senha proxy | DPAPI em vez de plaintext |
| DEC-027 | DPAPI | ctypes + CryptProtectData/CryptUnprotectData CurrentUser |
| DEC-028 | Startup | winreg no mesmo HKCU Run; não gravar python de desenvolvimento |
| DEC-029 | Notificações | QSystemTrayIcon pela porta de notificação |
| DEC-030 | Processos | subprocess, shell=False, flags Windows e taskkill |
| DEC-031 | JNA/Credential Manager | não implementar: não encontrados na baseline |
| DEC-032 | CI Windows | validar DPAPI/Registry em Windows real e chave isolada |

Os detalhes históricos permanecem rastreáveis nos commits dos Passos 1 a 8.

## DEC-033
ID DA DECISÃO: DEC-033  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-094  
COMPONENTE: Shell principal da interface  
COMPORTAMENTO ORIGINAL: `DashboardV5Main.kt` usa Window Compose 1600×960, menu lateral, seções V5, fecha escondendo para tray e encerra pela ação `Sair`. O workflow final adiciona `VIDEO_EDITOR` após `EXTRACTOR`.  
DECISÃO: usar `QMainWindow` + sidebar + `QStackedWidget`, preservando ordem final de 12 seções, tamanho inicial, título, close-to-tray e menu do tray.  
JUSTIFICATIVA: reproduzir comportamento, sem tentar traduzir Compose estruturalmente.  
EVIDÊNCIA NO KOTLIN: `DashboardV5Main.kt` + `tools/integrate-video-editor-tab.py`, Build SHA df1701.  
IMPACTO: base da UI PySide6.  
REVERSÍVEL: Sim somente mantendo equivalência funcional.

## DEC-034
ID DA DECISÃO: DEC-034  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-095 a MIG-103, MIG-105  
COMPONENTE: Fronteira UI ↔ serviços  
COMPORTAMENTO ORIGINAL: Dashboard chama `DesktopControllerV5`; o Controller chama DB/repositories/automação, não implementa scraping dentro dos composables.  
DECISÃO: criar `MainUiController` fino, sem SQL/scraping/matching/scheduler nos widgets. Buscas reais exigem `AutomationPort` injetado.  
JUSTIFICATIVA: o destino ainda não possui business `NewsRepository`/`VideoRepository`; recriá-los dentro da UI violaria a arquitetura e a regra de não inventar.  
EVIDÊNCIA: `DashboardV5Main.kt`, `DesktopControllerV5.kt` e `repositories/__init__.py` no destino.  
IMPACTO: runtime padrão exibe dados locais/configurações, mas busca real fica indisponível até a composição futura.  
REVERSÍVEL: Não sem alterar separação de responsabilidades.

## DEC-035
ID DA DECISÃO: DEC-035  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-100  
COMPONENTE: Catálogo da tela Fontes  
COMPORTAMENTO ORIGINAL: `SourceCatalog` contém 13 fontes nacionais, 135 estaduais e 12 especializadas; `DesktopVideoSources.all` combina `VideoSourceCatalog.all` com dois extras Desktop.  
DECISÃO: portar integralmente o catálogo de notícias necessário à UI. Para vídeos, usar somente os dois extras já migrados e registrar `VIDEO_CATALOG_COMPLETE=False`; não duplicar silenciosamente `VideoSourceCatalog` neste passo.  
JUSTIFICATIVA: a tela Fontes precisa do catálogo, mas o catálogo base de vídeo pertence a uma lacuna anterior ainda não migrada.  
EVIDÊNCIA NO KOTLIN: `SourceCatalog.kt`, `DesktopVideoSources.kt`.  
IMPACTO: notícias/especializadas completas; seleção de fontes de vídeo permanece parcial.  
REVERSÍVEL: Sim quando o catálogo base for migrado.

## DEC-036
ID DA DECISÃO: DEC-036  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-104, MIG-058 a MIG-077  
COMPONENTE: Ferramentas externas na navegação  
COMPORTAMENTO ORIGINAL: Dashboard final possui acesso a Editor PDF, Extrator e Editor de Vídeo; cada um tem motor próprio.  
DECISÃO: preservar seções e navegação, mas usar página-placeholder explícita no Passo 9.  
JUSTIFICATIVA: o escopo exige integração visual apenas e proíbe migrar os motores agora.  
EVIDÊNCIA: Dashboard final + workflow V8.  
IMPACTO: ponto de acesso existe sem funcionalidade inventada.  
REVERSÍVEL: Sim quando cada motor for migrado no passo próprio.

## DEC-037
ID DA DECISÃO: DEC-037  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-102, MIG-093  
COMPONENTE: Campo de senha do proxy  
COMPORTAMENTO ORIGINAL: a tela Kotlin inicializa o campo com `c.proxyPassword`, portanto pode repor a senha na UI.  
DECISÃO: o Python usa `QLineEdit.Password`, limpa o campo após salvar e não repõe automaticamente o plaintext descriptografado em refresh.  
JUSTIFICATIVA: requisito explícito dos Passos 8 e 9 de não expor credencial desprotegida sem necessidade. O segredo continua em DPAPI CurrentUser.  
EVIDÊNCIA: `V5SettingsScreen` + regras de segurança do Passo 8.  
IMPACTO: diferença deliberada de UX por segurança; não altera armazenamento nem autenticação.  
REVERSÍVEL: somente mediante decisão explícita de aceitar maior exposição.

## DEC-038
ID DA DECISÃO: DEC-038  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-095 a MIG-103  
COMPONENTE: Atualização da UI / não bloqueio  
COMPORTAMENTO ORIGINAL: Dashboard usa tick de aproximadamente 250 ms e as buscas rodam fora do thread visual.  
DECISÃO: usar `QTimer` de 250 ms para sincronizar a página atual; `ProxySettings.test_connection` roda em `QThread`; buscas são delegadas ao AutomationService.  
JUSTIFICATIVA: manter GUI responsiva e não executar requests diretamente em handlers de widgets.  
EVIDÊNCIA: Dashboard V5 e arquitetura do AutomationService.  
IMPACTO: callbacks de workers não manipulam widgets diretamente.  
REVERSÍVEL: Sim se a segurança de thread Qt for preservada.

## DEC-039
ID DA DECISÃO: DEC-039  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-004, MIG-094, MIG-091  
COMPONENTE: Tray e comportamento ao fechar  
COMPORTAMENTO ORIGINAL: fechar a janela apenas oculta; tray possui Abrir, três buscas, Parar buscas e Sair.  
DECISÃO: usar `QSystemTrayIcon`, ignorar `closeEvent` normal e esconder; `Sair` habilita encerramento real, fecha controller e esconde tray.  
JUSTIFICATIVA: equivalência operacional direta.  
EVIDÊNCIA: `DashboardV5Main.kt`.  
IMPACTO: execução residente preparada; notificação usa o mesmo tray Qt.  
REVERSÍVEL: Não sem mudar UX comprovada.

## DEC-040
ID DA DECISÃO: DEC-040  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-105  
COMPONENTE: Testes PySide6  
COMPORTAMENTO ORIGINAL: produto alvo é Windows, mas a suíte anterior já executava em Windows/Ubuntu.  
DECISÃO: manter matriz Windows/Ubuntu, instalar no runner Linux somente libs de runtime Qt (`libegl1`, `libgl1`, `libxkbcommon-x11-0`) e executar Qt com `QT_QPA_PLATFORM=offscreen`.  
JUSTIFICATIVA: validar widgets reais sem depender de desktop interativo e sem pular testes de GUI.  
EVIDÊNCIA: regressão inicial do Passo 9 mostrou ausência de `libEGL.so.1`; após instalar runtime, a mesma suíte passou em ambos os sistemas.  
IMPACTO: smoke/integration tests reais de Qt entram na regressão contínua.  
REVERSÍVEL: Sim.

## DEC-041
ID DA DECISÃO: DEC-041  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-096, MIG-097, MIG-098, MIG-099, MIG-100, MIG-102  
COMPONENTE: Aprovação conservadora da UI  
COMPORTAMENTO ORIGINAL: telas dependem de business repositories, VideoTermStore, catálogo completo de vídeo e elementos visuais adicionais.  
DECISÃO: não marcar como `APROVADO` uma tela cujo caminho real ainda dependa de componente ausente ou cuja paridade funcional esteja incompleta, mesmo que o widget abra e o teste de GUI passe.  
JUSTIFICATIVA: seguir o critério do usuário de aprovação somente com integração funcional comprovada.  
EVIDÊNCIA: checklist do Passo 9 e lacunas observadas no destino.  
IMPACTO: vários MIGs de UI ficam `EM TESTE`/`BLOQUEADO`, evitando falso positivo de migração.  
REVERSÍVEL: status pode avançar quando as dependências forem concluídas.

## Regra de segurança

Nenhuma decisão autoriza logar senha, token, cookie, credential blob ou plaintext descriptografado. Fixtures e testes usam somente valores artificiais.

## Regra de equivalência visual

O Passo 9 não exige pixel-perfect. Diferenças naturais entre Compose e Qt são aceitáveis somente quando não removem funcionalidade. Melhorias visuais/UX não são implementadas durante a equivalência; lacunas permanecem documentadas.
