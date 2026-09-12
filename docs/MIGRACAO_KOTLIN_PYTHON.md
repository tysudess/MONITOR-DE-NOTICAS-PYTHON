# Migração Kotlin → Python

## Fonte da verdade

- Repositório original: `tysudess/noticias-monitor`
- Repositório destino: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- Baseline funcional: Build SHA `df1701ba5427a04954093e8ebed63f26abb2b2b7` + transformações do workflow da release V8.
- Branch de migração: `migration/python-foundation`.

## Estados permitidos

`PENDENTE`, `EM MIGRAÇÃO`, `EM TESTE`, `APROVADO`, `BLOQUEADO`.

## Estado após o Passo 8

O Passo 8 adiciona somente infraestrutura de rede/proxy e integrações Windows comprovadas: configuração de proxy global, migração de host legado, senha protegida com DPAPI CurrentUser, startup por HKCU Run, notificação por tray, execução de subprocessos sem `shell=True` e testes Windows isolados. Interface completa, Editor de Vídeo, Editor PDF, extrator/downloader e portable final permanecem fora do escopo.

O Kotlin Desktop ativo **não usa JNA nem Windows Credential Manager**. Nenhum target de Credential Manager foi inventado. Também não foi encontrada persistência principal em AppData/LocalAppData/Documents/Downloads/ProgramData/UserProfile; o motor Desktop usa raiz portable e `data/`.

A baseline possui uma inconsistência objetiva: `DesktopControllerV5` usa default/migração `proxy-7dn.mb`, mas a tela do Build SHA ainda chama `saveProxy(..., "proxy-7db.mb", 6060, ...)`. Como a UI não é migrada neste passo, a camada Python preserva a regra do Controller e aceita host do chamador; não cria correção visual antecipada.

## MIG trabalhados no Passo 8

- `MIG-039` — Iniciar com Windows: `EM TESTE`.
- `MIG-040` — Proxy geral: `EM TESTE`.
- `MIG-041` — Migração `proxy-7db.mb` → `proxy-7dn.mb`: `APROVADO`.
- `MIG-087` — Transporte HTTP injetável: permanece `APROVADO`; passa a aceitar configuração real do proxy sem mudar o caminho sem proxy.
- `MIG-090` — DPAPI CurrentUser compatível com o formato comprovado: `EM TESTE`.
- `MIG-091` — Adaptador de notificações Windows/tray: `EM TESTE`.
- `MIG-092` — Processo oculto/árvore de processo Windows: `EM TESTE`.
- `MIG-093` — Senha de proxy protegida + migração de plaintext legado: `EM TESTE`.

`MIG-049` e `MIG-056` foram apenas referenciados porque seus arquivos Kotlin comprovam o contrato DPAPI; continuam `PENDENTE` porque pertencem ao extrator, que não foi migrado neste passo.

## Checklist oficial

| MIG | Módulo | Funcionalidade | Status |
|---|---|---|---|
| MIG-001 | Infraestrutura | Baseline congelada df1701 + workflow | PENDENTE |
| MIG-002 | Infraestrutura | Resolução de raiz portable | PENDENTE |
| MIG-003 | Infraestrutura | SharedPreferences portable | EM TESTE |
| MIG-004 | Infraestrutura | Tray e execução residente | PENDENTE |
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
| MIG-034 | Vídeos | Fontes Desktop extras g1/Domingo Espetacular | APROVADO |
| MIG-035 | Automação | Loop residente | APROVADO |
| MIG-036 | Automação | Intervalo automático de notícias | APROVADO |
| MIG-037 | Automação | Intervalo automático de demandas | APROVADO |
| MIG-038 | Automação | Horários automáticos de vídeos | APROVADO |
| MIG-039 | Windows | Iniciar com Windows | EM TESTE |
| MIG-040 | Windows | Proxy geral | EM TESTE |
| MIG-041 | Windows | Migração proxy-7db→proxy-7dn | APROVADO |
| MIG-042 | Controle | Cancelamento de buscas | EM TESTE |
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
| MIG-084 | Vídeos | Priorização estável de candidatos Globoplay | APROVADO |
| MIG-085 | Vídeos | Filtros/exclusões puros de candidato direto | APROVADO |
| MIG-086 | Vídeos | Coletor HTML genérico de portal/busca | APROVADO |
| MIG-087 | Networking | Transporte HTTP compatível e injetável para coletores | APROVADO |
| MIG-088 | Automação | Orquestração Desktop manual/automática e lanes de concorrência | APROVADO |
| MIG-089 | Automação | Progresso, status, durações e resultado operacional Desktop | APROVADO |
| MIG-090 | Windows/Segurança | DPAPI CurrentUser compatível | EM TESTE |
| MIG-091 | Windows | Adaptador de notificação pelo tray | EM TESTE |
| MIG-092 | Windows | Execução oculta e encerramento de árvore de processos | EM TESTE |
| MIG-093 | Networking/Segurança | Senha de proxy DPAPI e migração segura do legado | EM TESTE |

## Inventário Windows comprovado

| Função | Kotlin | API/mecanismo | Entrada | Saída | Risco | MIG |
|---|---|---|---|---|---|---|
| Proxy global | `DesktopControllerV5` | propriedades JVM + `Authenticator` | enable/host/port/user/pass | proxy HTTP/HTTPS | alto | MIG-040 |
| Migração host | `DesktopControllerV5.migrateProxyHost` | SharedPreferences | 7db/vazio | 7dn | baixo | MIG-041 |
| Teste proxy | `DesktopControllerV5.testProxyConnection` | Jsoup | configuração | sucesso/erro textual | médio | MIG-040 |
| Startup | `DesktopControllerV5.configureWindowsStartup` | `reg.exe` | bool + executável | HKCU Run | médio | MIG-039 |
| Notificação | `DashboardV5Main` | Compose Tray | título/mensagem | toast/tray | baixo | MIG-091 |
| DPAPI proxy extrator | `ExtractorPortableStateStore` | `ProtectedData` | texto UTF-8 | Base64 DPAPI | alto | MIG-090 |
| DPAPI sessão | `GloboplaySessionStore` | `ProtectedData` | cookies | Base64 DPAPI | alto | MIG-090 |
| Processo oculto | `HiddenWindowsProcess` | ProcessBuilder/PowerShell/taskkill | argv/env/cwd | processo/exit | médio | MIG-092 |

Credential Manager: **não encontrado**. JNA: **não encontrado**. Não há dependência JNA no módulo Desktop.

## Proxy

Defaults comprovados: desativado, host `proxy-7dn.mb`, porta `6060`, usuário/senha vazios. Porta é limitada a `1..65535`. Proxy pronto exige enabled + host + porta válida + usuário + senha. Labels preservados: `Proxy desativado`, `Proxy pronto`, `Proxy requer configuração`.

O transporte Python monta o mesmo proxy para HTTP e HTTPS e injeta em `requests`; quando desativado, `proxies=None`, preservando o caminho sem proxy. O teste usa `https://www.google.com/generate_204`, UA `Mozilla/5.0 MonitorDeNoticias/4.0.2`, timeout 12 s e aceita HTTP 200..399.

## SEGURANÇA DE CREDENCIAIS

### Contrato original protegido

Os stores do extrator usam Windows DPAPI com `DataProtectionScope.CurrentUser`, entropy adicional `null`, bytes UTF-8 e arquivo contendo Base64 do blob protegido. A implementação Python usa diretamente `CryptProtectData`/`CryptUnprotectData` via `ctypes`, sem depender de Python global ou pywin32.

### Senha do proxy Desktop

A baseline `DesktopControllerV5` grava `desktop_proxy_password` em SharedPreferences como texto. O Passo 8 proíbe explicitamente reduzir segurança ou manter senha em texto puro. Por isso a migração Python preserva todas as demais chaves e semânticas, mas move a senha para `data/prefs/desktop_proxy_password.dpapi` usando DPAPI CurrentUser.

Compatibilidade legada: se `desktop_proxy_password` existir em um arquivo antigo, o Python tenta protegê-lo primeiro e somente após sucesso remove a chave em claro. Se a proteção falhar, a chave não é apagada automaticamente. Senha, blob DPAPI e plaintext descriptografado nunca são registrados em log.

Credential Manager: **NÃO DETERMINADO PELO CÓDIGO ANALISADO como mecanismo usado; nenhuma chamada/target foi encontrada. Portanto não foi implementado.**

## Registry e startup

Contrato preservado:

- HIVE: `HKEY_CURRENT_USER`.
- PATH: `Software\Microsoft\Windows\CurrentVersion\Run`.
- VALUE NAME: `MonitorDeNoticias`.
- TYPE: `REG_SZ`.
- enable: valor é o caminho do executável entre aspas.
- disable: remove o valor.

O Python usa `winreg` diretamente em vez de `reg.exe`, reproduzindo a mesma API do Registro. Em desenvolvimento não grava caminho do interpretador: enable sem executável explícito só funciona quando `sys.frozen` indica o executável empacotado. Testes usam backend/chave isolados.

## Notificações

Os únicos eventos automáticos continuam os do `AutomationService`: notícias/demandas/vídeos novos. O adaptador chama `QSystemTrayIcon.showMessage(title, message)` e não adiciona ação, duração ou ícone. Duração, clique e ícone específicos: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**. Falha de notificação continua não derrubando a execução.

## Processos

`HiddenProcessRunner` usa lista de argumentos, `shell=False`, cwd e environment explícitos. No Windows usa `STARTF_USESHOWWINDOW/SW_HIDE` e `CREATE_NO_WINDOW`; PowerShell recebe `-WindowStyle Hidden`. Encerramento de árvore usa `taskkill.exe /PID <pid> /T /F`, com `kill()` como fallback. Não foi criado `shell=True`.

## Paths especiais

O motor Desktop analisado usa raiz portable e `data/`. Nenhum uso ativo de AppData, LocalAppData, Roaming, Documents, Downloads, Desktop, ProgramData ou UserProfile foi encontrado para essas funções. Portanto nenhuma pasta especial nova foi inventada.

## Testes do Passo 8

Foram adicionados testes unitários/equivalência para defaults, host legado, labels, porta, autenticação, ausência de senha, migração de plaintext, redaction, startup/Registry, notificações, execução de processo, argumentos com espaços e arquivo inexistente.

Há testes Windows reais isolados para:

- DPAPI round-trip com segredo fictício;
- interoperabilidade Python ↔ `.NET ProtectedData` CurrentUser;
- `winreg` em `HKCU\Software\MonitorDeNoticias\Tests\Step8`, com limpeza ao final.

A workflow `python-migration-tests.yml` executa a suíte completa em Ubuntu e Windows. Nenhuma fixture contém senha/token/cookie/blob real.

## Regras permanentes

Os identificadores `MIG-001` a `MIG-093` são permanentes. Não renumerar ou reutilizar. Um MIG somente pode ser marcado `APROVADO` após comparação objetiva com a baseline e validação compatível com sua natureza.
