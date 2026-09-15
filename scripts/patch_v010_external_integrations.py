from __future__ import annotations

import sys
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Trecho esperado não encontrado em {path}: {old[:80]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_news(root: Path) -> None:
    main = root / "main.js"
    preload = root / "preload.js"
    html = root / "renderer" / "index.html"
    renderer = root / "renderer" / "renderer.js"

    replace_once(
        main,
        "function configurarConexao(opcoes = {}) {\n  const usarProxy = opcoes.usarProxy === true;\n  const config = carregarConfigProxyLocal();\n\n  if (!usarProxy) {\n    motor.prepararProxy('', '', { ...config, ATIVADO: false });\n    return { proxy: false, descricao: 'Conexão direta' };\n  }\n\n  const usuario = String(opcoes.usuario || '').trim();\n  const senha = String(opcoes.senha || '');\n  if (!usuario) throw new Error('Informe o usuário do proxy.');\n  if (!senha) throw new Error('Informe a senha do proxy.');\n\n  motor.prepararProxy(usuario, senha, { ...config, ATIVADO: true });\n  return { proxy: true, descricao: 'Proxy corporativo ativo' };\n}",
        "function configurarConexao(_opcoes = {}) {\n  // v0.0.10: uma única conexão proxy é definida pelo Monitor em Configurações.\n  const raw = String(process.env.MONITOR_PROXY_URL || process.env.HTTPS_PROXY || process.env.HTTP_PROXY || '').trim();\n  if (!raw) {\n    motor.prepararProxy('', '', { ATIVADO:false, SERVIDOR:'', PORTA:'', TIMEOUT_MS:45000, CERTIFICADO_CA:'' });\n    return { proxy:false, descricao:'Conexão direta' };\n  }\n  const parsed = new URL(raw);\n  const usuario = decodeURIComponent(parsed.username || '');\n  const senha = decodeURIComponent(parsed.password || '');\n  motor.prepararProxy(usuario, senha, {\n    ATIVADO:true,\n    SERVIDOR:parsed.hostname,\n    PORTA:Number(parsed.port || 80),\n    TIMEOUT_MS:45000,\n    CERTIFICADO_CA:''\n  });\n  return { proxy:true, descricao:'Proxy global do Monitor ativo' };\n}"
    )

    replace_once(
        main,
        "  mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));\n",
        "  mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));\n\n  // Ponte Monitor -> Extrator: o Monitor grava monitor-url.txt ao clicar em\n  // 'Extrair matéria'. O Electron consome o arquivo e preenche o textarea.\n  const monitorUrlFile = path.join(path.dirname(process.execPath), 'monitor-url.txt');\n  const consumeMonitorUrl = () => {\n    try {\n      if (!fs.existsSync(monitorUrlFile)) return;\n      const value = fs.readFileSync(monitorUrlFile, 'utf8').replace(/^\\uFEFF/, '').trim();\n      fs.unlinkSync(monitorUrlFile);\n      if (value && mainWindow && !mainWindow.isDestroyed()) mainWindow.webContents.send('monitor-url', value);\n    } catch (_) {}\n  };\n  const monitorUrlTimer = setInterval(consumeMonitorUrl, 350);\n  mainWindow.on('closed', () => clearInterval(monitorUrlTimer));\n  mainWindow.webContents.on('did-finish-load', consumeMonitorUrl);\n"
    )

    replace_once(
        main,
        "ipcMain.handle('extrair-materia', async (_event, opcoes) => extrairMateriaGUI(opcoes));\n",
        "ipcMain.handle('extrair-materia', async (_event, opcoes) => extrairMateriaGUI(opcoes));\nipcMain.handle('monitor-colar', async () => clipboard.readText());\n"
    )

    replace_once(
        preload,
        "  revisarTextoRigido: (texto) => ipcRenderer.invoke('revisar-texto-rigido', texto),\n  onStatus: (callback) => ipcRenderer.on('extracao-status', (_event, mensagem) => callback(mensagem))\n",
        "  revisarTextoRigido: (texto) => ipcRenderer.invoke('revisar-texto-rigido', texto),\n  colarDoClipboard: () => ipcRenderer.invoke('monitor-colar'),\n  onMonitorUrl: (callback) => ipcRenderer.on('monitor-url', (_event, value) => callback(value)),\n  onStatus: (callback) => ipcRenderer.on('extracao-status', (_event, mensagem) => callback(mensagem))\n"
    )

    replace_once(
        html,
        "          <button id=\"extrair\" class=\"btn btn-primary\" type=\"button\">\n            <span aria-hidden=\"true\">↓</span>\n            <span>Extrair matéria</span>\n          </button>\n",
        "          <button id=\"colarLink\" class=\"btn btn-ghost\" type=\"button\" title=\"Colar link da área de transferência\">\n            <span aria-hidden=\"true\">▣</span>\n            <span>Colar</span>\n          </button>\n          <button id=\"extrair\" class=\"btn btn-primary\" type=\"button\">\n            <span aria-hidden=\"true\">↓</span>\n            <span>Extrair matéria</span>\n          </button>\n"
    )

    replace_once(
        html,
        "      <details class=\"card proxy-card\" id=\"proxyCard\">",
        "      <details class=\"card proxy-card\" id=\"proxyCard\" style=\"display:none\" aria-hidden=\"true\">"
    )
    replace_once(
        html,
        "        <button class=\"nav-item\" type=\"button\" data-scroll=\"proxyCard\">",
        "        <button class=\"nav-item\" type=\"button\" data-scroll=\"proxyCard\" style=\"display:none\" aria-hidden=\"true\">"
    )

    replace_once(
        renderer,
        "const btnExtrair = document.getElementById('extrair');\n",
        "const btnExtrair = document.getElementById('extrair');\nconst btnColarLink = document.getElementById('colarLink');\n"
    )
    replace_once(
        renderer,
        "window.extratorAPI.onStatus((mensagem) => definirStatus(mensagem));\n",
        "window.extratorAPI.onStatus((mensagem) => definirStatus(mensagem));\n\nfunction receberLinkMonitor(value) {\n  const link = String(value || '').trim();\n  if (!link) return;\n  url.value = link;\n  url.dispatchEvent(new Event('input', { bubbles:true }));\n  url.focus();\n  sincronizarBotaoExtrair();\n  definirStatus('Link recebido do Monitor. Pronto para extrair.', 'ready');\n}\nwindow.extratorAPI.onMonitorUrl(receberLinkMonitor);\nbtnColarLink?.addEventListener('click', async () => {\n  try { receberLinkMonitor(await window.extratorAPI.colarDoClipboard()); }\n  catch (e) { definirStatus('Não foi possível colar o link: ' + (e?.message || e), 'error'); }\n});\n"
    )

    replace_once(
        renderer,
        "usarProxy.addEventListener('change', () => {\n  camposProxy.classList.toggle('oculto', !usarProxy.checked);\n  if (usarProxy.checked) usuario.focus();\n});\n",
        "usarProxy.checked = false;\ncamposProxy.classList.add('oculto');\n"
    )


def patch_sheet(root: Path) -> None:
    engine = root / "engine" / "index.js"
    replace_once(
        engine,
        "const PROXY = CONFIG.proxy || {};\nconst PROXY_ATIVO = Boolean(PROXY.ativo);\nconst PROXY_HOST = String(PROXY.host || \"\").trim();\nconst PROXY_PORT = Number(PROXY.porta || 0);\nconst PROXY_USUARIO = String(PROXY.usuario || \"\").trim();\nconst PROXY_SENHA = String(PROXY.senha || \"\");\n",
        "// v0.0.10: ignora proxy individual do config.json e usa somente o proxy\n// global herdado da aba Configurações do Monitor.\nconst MONITOR_PROXY_RAW = String(process.env.MONITOR_PROXY_URL || process.env.HTTPS_PROXY || process.env.HTTP_PROXY || '').trim();\nlet MONITOR_PROXY = null;\ntry { MONITOR_PROXY = MONITOR_PROXY_RAW ? new URL(MONITOR_PROXY_RAW) : null; } catch (_) { MONITOR_PROXY = null; }\nconst PROXY_ATIVO = Boolean(MONITOR_PROXY);\nconst PROXY_HOST = MONITOR_PROXY ? MONITOR_PROXY.hostname : '';\nconst PROXY_PORT = MONITOR_PROXY ? Number(MONITOR_PROXY.port || 80) : 0;\nconst PROXY_USUARIO = MONITOR_PROXY ? decodeURIComponent(MONITOR_PROXY.username || '') : '';\nconst PROXY_SENHA = MONITOR_PROXY ? decodeURIComponent(MONITOR_PROXY.password || '') : '';\n"
    )


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        raise SystemExit("uso: patch_v010_external_integrations.py <news-source> <sheet-source>")
    news = Path(argv[1]).resolve()
    sheet = Path(argv[2]).resolve()
    patch_news(news)
    patch_sheet(sheet)

    # v0.0.12 é um overlay adicional sobre a cópia de BUILD já preparada.
    # Os fontes auditáveis permanecem intactos porque build_external_integrations.ps1
    # os copia antes de chamar este script.
    from patch_v012_external_integrations import patch_news as patch_news_v012, patch_sheet as patch_sheet_v012
    patch_news_v012(news)
    patch_sheet_v012(sheet)

    print("V010_EXTERNAL_INTEGRATIONS_PATCHED=YES")
    print("V012_EXTERNAL_INTEGRATIONS_PATCHED=YES")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
