# Arquitetura da migração Python

## Fonte da verdade

A migração usa `tysudess/noticias-monitor`, Build SHA `df1701ba5427a04954093e8ebed63f26abb2b2b7`, mais as transformações do workflow V8. O destino é `tysudess/MONITOR-DE-NOTICAS-PYTHON`, branch `migration/python-foundation`.

## Estado após o Passo 8

A fundação, SQLite, models, matching, coletores e AutomationService permanecem separados. O Passo 8 acrescenta somente infraestrutura de rede/proxy e integrações Windows comprovadas. UI completa, PDF, Editor de Vídeo, extrator independente e build portable final permanecem pendentes.

Fluxo de camadas relevante:

`AutomationService` → porta de notificação → `WindowsTrayNotifier`

`collectors`/futuros repositories → `HttpClient` → proxy injetado por `ProxySettings`

`ProxySettings` → `SharedPreferences` para dados não secretos + `DpapiTextStore` para senha

`StartupManager` → `winreg` → HKCU Run

`HiddenProcessRunner` → `subprocess`/Win32 flags + `taskkill.exe`

## Networking

### HttpClient

Continua usando `requests.Session`, timeouts separados quando o coletor os define, redirects e headers próprios. O caminho sem proxy continua `proxies=None`. O Passo 8 não introduz retry genérico nem proxy SOCKS.

### ProxySettings

Responsabilidades:

- carregar `desktop_proxy_enabled`;
- carregar/migrar `desktop_proxy_host`;
- limitar `desktop_proxy_port` a 1..65535;
- carregar `desktop_proxy_username`;
- obter senha exclusivamente do secret store protegido;
- construir proxy HTTP/HTTPS para `requests`;
- executar o teste `generate_204` com o contrato da baseline.

Defaults: host `proxy-7dn.mb`, porta 6060, disabled, username/senha vazios.

A baseline contém um conflito entre a tela (`proxy-7db.mb`) e o Controller (migração/default `proxy-7dn.mb`). Como o Passo 8 não migra a UI, a camada mantém o contrato do Controller e não altera a tela original.

## SEGURANÇA DE CREDENCIAIS

### DPAPI

`monitor_noticias.windows.dpapi` chama diretamente:

- `CryptProtectData`;
- `CryptUnprotectData`;
- `LocalFree`.

Escopo: CurrentUser, equivalente a `DataProtectionScope.CurrentUser`.

Entropy adicional: `null`/ausente.

Encoding do segredo: UTF-8.

Persistência: Base64 do blob DPAPI em arquivo texto. Nenhum plaintext é versionado ou persistido pelo novo caminho.

Imports de DLL são lazy: em não-Windows, importar o pacote não falha; a operação DPAPI levanta `WindowsIntegrationUnavailable` somente se chamada.

### Senha do proxy

A baseline Desktop armazena `desktop_proxy_password` em SharedPreferences. Por requisito explícito do Passo 8, o Python não mantém esse risco. A senha passa para `data/prefs/desktop_proxy_password.dpapi`.

Migração legada segura:

1. detectar chave plaintext antiga;
2. proteger com DPAPI CurrentUser;
3. persistir o blob protegido;
4. somente depois remover `desktop_proxy_password` do `.properties`.

Falha em proteger não apaga a senha legada. Logs nunca recebem senha, token, blob ou plaintext descriptografado. Mensagens de erro do teste de proxy redigem a senha crua e percent-encoded.

### Credential Manager

Não foram encontradas chamadas `CredRead`/`CredWrite`, target name, credential type ou persistence mode na baseline Desktop. Não existe dependência JNA no módulo. Logo Credential Manager e JNA não foram implementados.

## Windows Registry / startup

`StartupManager` preserva:

- HIVE: HKCU;
- path: `Software\Microsoft\Windows\CurrentVersion\Run`;
- value: `MonitorDeNoticias`;
- type: `REG_SZ`;
- dado: caminho do executável entre aspas;
- disable: delete do value.

Diferença técnica: Python usa `winreg`, não chama `reg.exe`. O efeito no Registro é o mesmo. Para evitar caminho de desenvolvimento, `StartupManager.configure(True)` sem caminho explícito somente grava quando `sys.frozen` está ativo. Testes injetam caminho/backend isolados.

## Notificações Windows

O Kotlin envia `Notification(title, message)` pelo TrayState. O Python usa `WindowsTrayNotifier`, um adaptador sobre `QSystemTrayIcon.showMessage(title, message)`. Não adiciona duração, ação ou ícone não comprovados. Falha permanece não fatal.

Eventos continuam pertencendo ao AutomationService:

- notícias/demandas quando há novos resultados;
- vídeos quando há novos vídeos relevantes.

A camada Windows não duplica regra de negócio.

## Execução de processos

`HiddenProcessRunner` substitui `HiddenWindowsProcess` com a mesma responsabilidade operacional:

- argv não vazio;
- cwd explícito;
- environment adicional;
- stderr pode ser unido ao stdout;
- PowerShell recebe `-WindowStyle Hidden` quando necessário;
- Windows usa `STARTF_USESHOWWINDOW`, `SW_HIDE` e `CREATE_NO_WINDOW`;
- `shell=False` sempre;
- timeout encerra árvore;
- `taskkill.exe /PID /T /F` encerra descendentes no Windows;
- exit code e output são retornados.

Não foi migrado nenhum comando específico de ffmpeg/ffprobe/yt-dlp neste passo; apenas a infraestrutura nativa compartilhável.

## Paths Windows

A baseline Desktop usa `PortablePaths.appRoot` e `data/`. Não foi encontrado uso ativo de AppData, LocalAppData, Roaming, Documents, Downloads, Desktop, ProgramData ou UserProfile para o núcleo deste passo. Não há nova camada de known folders.

## Matriz Kotlin/API → Python

| Kotlin / mecanismo | API real | Python |
|---|---|---|
| `ProtectedData.Protect/Unprotect(CurrentUser)` via PowerShell | Windows DPAPI | `ctypes` + `CryptProtectData/CryptUnprotectData` |
| `reg add/delete` HKCU Run | Windows Registry | `winreg` |
| Compose `trayState.sendNotification` | Shell/tray notification Qt | `QSystemTrayIcon.showMessage` |
| `ProcessBuilder` + PowerShell hidden | CreateProcess/console flags | `subprocess.Popen`, `CREATE_NO_WINDOW`, `STARTF_USESHOWWINDOW` |
| `taskkill.exe /PID /T /F` | process-tree termination | mesmo `taskkill.exe`, argv seguro |
| JVM proxy properties + Authenticator | authenticated HTTP proxy | `requests` proxies com credenciais percent-encoded |

JNA → Python: não aplicável; JNA não existe na baseline ativa.

Credential Manager → Python: não aplicável; nenhum uso foi encontrado.

## Integração com coletores

`ProxySettings.requests_proxies()` entrega o dicionário usado pelo `HttpClient`. Com proxy desativado, retorna `None`, preservando testes e comportamento dos coletores do Passo 6. A orquestração completa dos repositories continua pendente, portanto `MIG-040` permanece `EM TESTE`.

## Integração com AutomationService

O AutomationService já recebe uma porta `notify(title, message)`. O Passo 8 fornece `WindowsTrayNotifier` para essa porta. Nenhum scheduler, sequência ou regra de notificação foi duplicado.

## Testes

Cobertura adicionada:

- proxy disabled/defaults;
- host legado 7db→7dn;
- porta e autenticação;
- senha ausente;
- migração de plaintext para secret store;
- ausência de segredo no `.properties`;
- redaction em erro;
- contrato do teste generate_204;
- Registry/startup por backend fake;
- adaptador de notificação;
- subprocess exit/stdout/stderr/argumento com espaços/arquivo ausente;
- DPAPI real Windows;
- interoperabilidade DPAPI Python ↔ .NET ProtectedData;
- Registry real em chave de teste isolada e limpa ao final.

A workflow `Python migration tests` executa `compileall` e a suíte completa em Ubuntu e Windows. Os testes específicos de DPAPI/Registry são pulados fora do Windows e executados no job Windows.

## Pendências deliberadas

- UI de configurações completa;
- composição real de repositories e coletores com ProxySettings;
- teste visual de toast/tray no desktop interativo;
- validação do startup no executável final empacotado;
- integração final dos stores DPAPI do extrator/Globoplay;
- Credential Manager: não existe na baseline, portanto não é pendência de implementação;
- caminhos especiais Windows: não usados no motor analisado.
