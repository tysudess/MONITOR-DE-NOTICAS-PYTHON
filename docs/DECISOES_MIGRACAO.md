# Decisões de migração

## Decisões anteriores preservadas

As decisões `DEC-001` a `DEC-024` continuam válidas e não são renumeradas. Resumo permanente:

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
| DEC-012 | VideoTermStore | persistência aguardava SharedPreferences |
| DEC-013 | URLs | canonicalização com urllib mantendo saída |
| DEC-014 | Globoplay | prioridade estável booleana, sem score inventado |
| DEC-015 | Passo 5 | extrair somente regras determinísticas |
| DEC-016 | HTTP/parsing | requests + BeautifulSoup preservando contratos |
| DEC-017 | Proxy futuro | HttpClient aceita proxies por injeção |
| DEC-018 | Globoplay parcial | Edições/Trechos permanecem EM TESTE |
| DEC-019 | Scheduler | thread de loop + lanes seriais equivalentes |
| DEC-020 | Relógio | datetime local do sistema |
| DEC-021 | Automation/repositories | portas NewsRunner/VideoRunner |
| DEC-022 | Retry/timeout | AutomationService não adiciona retry/timeout global |
| DEC-023 | SharedPreferences | propriedades + StringSet compatível, MIG-003 EM TESTE |
| DEC-024 | Cancelamento | token cooperativo, MIG-042 EM TESTE |

Os detalhes históricos continuam rastreáveis pelos commits anteriores da branch.

## DEC-025
ID DA DECISÃO: DEC-025  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-040, MIG-041, MIG-087  
COMPONENTE: Proxy global Desktop  
COMPORTAMENTO ORIGINAL: `DesktopControllerV5` mantém enabled, host, port, username e password; default host `proxy-7dn.mb`, porta 6060; migra `proxy-7db.mb`/vazio para `proxy-7dn.mb`; aplica HTTP e HTTPS e testa `https://www.google.com/generate_204`.  
DECISÃO: criar `ProxySettings` e continuar injetando proxies no `HttpClient`; quando disabled, não passar proxy.  
JUSTIFICATIVA: preservar a separação Controller/configuração → transporte sem criar tipo de proxy novo.  
EVIDÊNCIA NO KOTLIN: `DesktopControllerV5.kt`, Build SHA df1701.  
IMPACTO: MIG-040 `EM TESTE`; MIG-041 `APROVADO`.  
REVERSÍVEL: Sim, desde que o contrato permaneça igual.

## DEC-026
ID DA DECISÃO: DEC-026  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-040, MIG-093  
COMPONENTE: Senha do proxy  
COMPORTAMENTO ORIGINAL: o Controller Desktop grava `desktop_proxy_password` em SharedPreferences plaintext.  
DECISÃO: **não reproduzir plaintext**; armazenar senha em `data/prefs/desktop_proxy_password.dpapi` usando DPAPI CurrentUser. Se existir chave legada plaintext, proteger primeiro e removê-la somente depois de persistência protegida bem-sucedida.  
JUSTIFICATIVA: requisito explícito do Passo 8: não reduzir segurança e não guardar senha em texto puro.  
EVIDÊNCIA NO KOTLIN: `DesktopControllerV5.proxyPassword/saveProxy`; contrato DPAPI comprovado em `ExtractorPortableStateStore` e `GloboplaySessionStore`.  
IMPACTO: adaptação deliberada de segurança; host/porta/usuário/enable permanecem nas mesmas chaves.  
REVERSÍVEL: somente se houver decisão explícita de aceitar plaintext, o que violaria o Passo 8.

## DEC-027
ID DA DECISÃO: DEC-027  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-090, MIG-093  
COMPONENTE: DPAPI  
COMPORTAMENTO ORIGINAL: PowerShell chama `System.Security.Cryptography.ProtectedData.Protect/Unprotect`, entropy `null`, `DataProtectionScope.CurrentUser`; arquivo armazena Base64 do blob; payload original é UTF-8.  
DECISÃO: usar `ctypes` para `CryptProtectData`/`CryptUnprotectData` e `LocalFree`, sem pywin32 obrigatório; manter CurrentUser, sem entropy e Base64 externo.  
JUSTIFICATIVA: reproduzir diretamente a API nativa usada pelo .NET, sem subprocesso PowerShell para o novo secret store.  
EVIDÊNCIA NO KOTLIN: `ExtractorPortableStateStore.kt`, `GloboplaySessionStore.kt`.  
IMPACTO: teste de interoperabilidade Python ↔ .NET ProtectedData executável em Windows.  
REVERSÍVEL: Sim se outra implementação continuar byte/escopo compatível.

## DEC-028
ID DA DECISÃO: DEC-028  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-039  
COMPONENTE: Inicialização com Windows  
COMPORTAMENTO ORIGINAL: `reg add/delete` em `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`, value `MonitorDeNoticias`, REG_SZ, dado `"<current process command>"`.  
DECISÃO: usar `winreg` para escrever/remover exatamente o mesmo hive/path/name/type/data; em desenvolvimento não inferir `python.exe`, e sim só usar `sys.executable` automaticamente quando `sys.frozen`.  
JUSTIFICATIVA: mesmo efeito nativo, sem gravar caminho de desenvolvimento no Registro.  
EVIDÊNCIA NO KOTLIN: `DesktopControllerV5.configureWindowsStartup`.  
IMPACTO: MIG-039 permanece `EM TESTE` até executável final empacotado; construção/Registry isolado são testados.  
REVERSÍVEL: Sim.

## DEC-029
ID DA DECISÃO: DEC-029  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-091, MIG-088, MIG-089  
COMPONENTE: Notificações  
COMPORTAMENTO ORIGINAL: `DashboardV5Main` injeta callback no Controller e chama `trayState.sendNotification(Notification(title, message))`; erros são envolvidos por `runCatching`.  
DECISÃO: fornecer `WindowsTrayNotifier`, adaptador callable sobre `QSystemTrayIcon.showMessage(title, message)`, sem duração/ação/ícone adicional.  
JUSTIFICATIVA: PySide6 já é a UI alvo e o AutomationService já expõe a porta notify; não duplicar regras.  
EVIDÊNCIA NO KOTLIN: `DashboardV5Main.kt`.  
IMPACTO: falha de notificação é logada e não derruba automação. Clique/duração/ícone: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**.  
REVERSÍVEL: Sim.

## DEC-030
ID DA DECISÃO: DEC-030  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-092  
COMPONENTE: Processos Windows  
COMPORTAMENTO ORIGINAL: `HiddenWindowsProcess` usa ProcessBuilder, PowerShell oculto e `taskkill.exe /PID /T /F`; combina stderr/stdout.  
DECISÃO: usar `subprocess` com argv em lista, `shell=False`, cwd/environment explícitos, `CREATE_NO_WINDOW` + `STARTF_USESHOWWINDOW/SW_HIDE` e o mesmo taskkill para árvore.  
JUSTIFICATIVA: reproduz o efeito nativo e melhora segurança de quoting sem inventar shell.  
EVIDÊNCIA NO KOTLIN: `HiddenWindowsProcess.kt`.  
IMPACTO: chamadas específicas de ffmpeg/yt-dlp permanecem nos passos próprios.  
REVERSÍVEL: Sim.

## DEC-031
ID DA DECISÃO: DEC-031  
DATA: 2026-09-12  
MIG RELACIONADO: Passo 8  
COMPONENTE: JNA / Credential Manager  
COMPORTAMENTO ORIGINAL: nenhuma dependência JNA e nenhuma chamada `CredRead`/`CredWrite`/target de Credential Manager foram encontradas no módulo Desktop ativo.  
DECISÃO: não adicionar JNA, pywin32 Credential Manager, target name, credential type ou persistence mode.  
JUSTIFICATIVA: criar isso seria inventar uma estratégia inexistente.  
EVIDÊNCIA NO KOTLIN: `desktop/build.gradle.kts`, árvore/arquivos e revisão por referências.  
IMPACTO: relatório final registra “não usado / não migrado”.  
REVERSÍVEL: Sim caso futura evidência da baseline prove uso real.

## DEC-032
ID DA DECISÃO: DEC-032  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-039, MIG-040, MIG-090 a MIG-093  
COMPONENTE: Validação Windows  
COMPORTAMENTO ORIGINAL: DPAPI e Registry dependem de Windows real.  
DECISÃO: adicionar workflow de testes em matriz Ubuntu/Windows. No Windows, usar somente segredo fictício e chave isolada `HKCU\Software\MonitorDeNoticias\Tests\Step8`, removida ao final; nunca tocar a entrada real de startup nos testes automatizados.  
JUSTIFICATIVA: mocks não são prova suficiente para DPAPI/Registry.  
EVIDÊNCIA: requisito de validação do Passo 8.  
IMPACTO: MIGs nativos continuam `EM TESTE` até integração final mesmo com CI verde.  
REVERSÍVEL: Sim.

## Regra de segurança

Nenhuma decisão autoriza logar senha, token, cookie, credential blob ou plaintext descriptografado. Fixtures e testes usam somente valores artificiais.
