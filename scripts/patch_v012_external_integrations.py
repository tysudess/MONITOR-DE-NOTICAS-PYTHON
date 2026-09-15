from __future__ import annotations

"""Overlay v0.0.12 aplicado somente à cópia de BUILD das integrações Electron.

As cópias originais auditáveis continuam preservadas antes deste script.
"""

from pathlib import Path
import sys


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"âncora não encontrada: {label}")
    return text.replace(old, new, 1)


def patch_news(root: Path) -> None:
    renderer_path = root / "renderer" / "renderer.js"
    renderer = read(renderer_path)

    old = """async function substituirIssue(issue, sugestao) {
  const texto = resultado.textContent || '';
  const inicio = Number(issue.offset) || 0;
  const tamanho = Number(issue.length) || String(issue.palavra || '').length;
  const atual = texto.slice(inicio, inicio + tamanho);

  if (atual !== issue.palavra) {
    await revisarTextoRigido();
    return;
  }

  resultado.textContent = texto.slice(0, inicio) + sugestao + texto.slice(inicio + tamanho);
  resultadoVazio.classList.add('oculto');
  btnCopiar.disabled = false;
  await revisarTextoRigido({ automatico: true });
}
"""
    new = """async function substituirIssue(issue, sugestao) {
  const texto = resultado.textContent || '';
  const palavra = String(issue.palavra || '');
  let inicio = Math.max(0, Number(issue.offset) || 0);
  const tamanho = Math.max(0, Number(issue.length) || palavra.length);

  // O Chromium pode normalizar espaços/acentos no contentEditable e deslocar
  // o offset retornado pelo corretor. Reencontra somente a ocorrência próxima
  // da posição original, sem alterar qualquer outra palavra.
  if (texto.slice(inicio, inicio + tamanho) !== palavra) {
    const de = Math.max(0, inicio - 120);
    const ate = Math.min(texto.length, inicio + tamanho + 120);
    const local = texto.slice(de, ate).indexOf(palavra);
    if (local < 0) {
      await revisarTextoRigido();
      return;
    }
    inicio = de + local;
  }

  resultado.textContent = texto.slice(0, inicio) + String(sugestao) + texto.slice(inicio + tamanho);
  resultado.dispatchEvent(new Event('input', { bubbles: true }));
  resultadoVazio.classList.add('oculto');
  btnCopiar.disabled = false;
  await revisarTextoRigido({ automatico: true });
}
"""
    renderer = replace_once(renderer, old, new, "news substituirIssue")

    ctrl_v = r"""

// v0.0.12 — Ctrl+V explícito para campos do Electron incorporado.
document.addEventListener('keydown', async (event) => {
  if (!(event.ctrlKey || event.metaKey) || String(event.key).toLowerCase() !== 'v') return;
  const active = document.activeElement;
  const editable = active && (
    active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.isContentEditable
  );
  if (!editable || !window.extratorAPI?.colarDoClipboard) return;
  event.preventDefault();
  const pasted = String(await window.extratorAPI.colarDoClipboard() || '');
  if (!pasted) return;
  if (active === url) {
    const start = Number.isInteger(active.selectionStart) ? active.selectionStart : active.value.length;
    const end = Number.isInteger(active.selectionEnd) ? active.selectionEnd : start;
    active.value = active.value.slice(0, start) + pasted + active.value.slice(end);
    active.selectionStart = active.selectionEnd = start + pasted.length;
    active.dispatchEvent(new Event('input', { bubbles: true }));
    sincronizarBotaoExtrair();
    return;
  }
  if (active.isContentEditable) {
    document.execCommand('insertText', false, pasted);
    active.dispatchEvent(new Event('input', { bubbles: true }));
    return;
  }
  const start = Number.isInteger(active.selectionStart) ? active.selectionStart : active.value.length;
  const end = Number.isInteger(active.selectionEnd) ? active.selectionEnd : start;
  active.value = active.value.slice(0, start) + pasted + active.value.slice(end);
  active.selectionStart = active.selectionEnd = start + pasted.length;
  active.dispatchEvent(new Event('input', { bubbles: true }));
});
"""
    if "v0.0.12 — Ctrl+V explícito" not in renderer:
        renderer += ctrl_v
    write(renderer_path, renderer)


def patch_sheet(root: Path) -> None:
    main_path = root / "main.js"
    preload_path = root / "preload.js"
    html_path = root / "renderer" / "index.html"
    renderer_path = root / "renderer" / "renderer.js"

    main = read(main_path)
    preload = read(preload_path)
    html = read(html_path)
    renderer = read(renderer_path)

    main = replace_once(
        main,
        'const { app, BrowserWindow, ipcMain, shell } = require("electron");',
        'const { app, BrowserWindow, ipcMain, shell, clipboard } = require("electron");',
        "sheet clipboard import",
    )
    anchor = '  ipcMain.handle("config:open-folder",()=>{shell.openPath(baseDir());return {ok:true};});\n'
    if 'clipboard:read' not in main:
        main = replace_once(main, anchor, anchor + '  ipcMain.handle("clipboard:read",()=>clipboard.readText());\n', "sheet clipboard ipc")

    anchor_preload = '  openConfigFolder: () => ipcRenderer.invoke("config:open-folder"),\n'
    if 'readClipboard' not in preload:
        preload = replace_once(preload, anchor_preload, anchor_preload + '  readClipboard: () => ipcRenderer.invoke("clipboard:read"),\n', "sheet preload clipboard")

    # Mantém os elementos no DOM para preservar o renderer original, mas não
    # expõe uma segunda conexão proxy: a única fonte passa a ser Configurações do Monitor.
    proxy_start = '<div class="card-title config-subtitle">Proxy</div>'
    proxy_end = '<label>IDs dos grupos (um por linha)'
    if proxy_start in html and proxy_end in html:
        before, rest = html.split(proxy_start, 1)
        proxy_block, after = rest.split(proxy_end, 1)
        html = (
            before
            + '<div id="legacyProxyControls" style="display:none" aria-hidden="true">'
            + proxy_start + proxy_block
            + '</div><p class="muted">Proxy: conexão única definida na aba Configurações do Monitor.</p>'
            + proxy_end + after
        )
    html = html.replace('<div class="metric-row"><span>Proxy</span><b id="proxyStatus">--</b></div>', '<div class="metric-row"><span>Proxy</span><b id="proxyStatus">Monitor</b></div>')

    ctrl_v = r"""

// v0.0.12 — Ctrl+V explícito no Electron incorporado.
document.addEventListener('keydown', async (event) => {
  if (!(event.ctrlKey || event.metaKey) || String(event.key).toLowerCase() !== 'v') return;
  const active = document.activeElement;
  if (!active || !(active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.isContentEditable)) return;
  if (!window.api?.readClipboard) return;
  event.preventDefault();
  const pasted = String(await window.api.readClipboard() || '');
  if (!pasted) return;
  if (active.isContentEditable) {
    document.execCommand('insertText', false, pasted);
  } else {
    const start = Number.isInteger(active.selectionStart) ? active.selectionStart : active.value.length;
    const end = Number.isInteger(active.selectionEnd) ? active.selectionEnd : start;
    active.value = active.value.slice(0, start) + pasted + active.value.slice(end);
    active.selectionStart = active.selectionEnd = start + pasted.length;
  }
  active.dispatchEvent(new Event('input', { bubbles: true }));
  active.dispatchEvent(new Event('change', { bubbles: true }));
});
"""
    if "v0.0.12 — Ctrl+V explícito" not in renderer:
        renderer += ctrl_v

    write(main_path, main)
    write(preload_path, preload)
    write(html_path, html)
    write(renderer_path, renderer)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        raise SystemExit("uso: patch_v012_external_integrations.py <extrator-noticias> <automacao-planilhas>")
    news = Path(argv[1]).resolve()
    sheet = Path(argv[2]).resolve()
    patch_news(news)
    patch_sheet(sheet)
    print("V012_EXTERNAL_OVERLAY_OK=YES")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
