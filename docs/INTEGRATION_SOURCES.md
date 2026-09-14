# Integrações externas preservadas — v0.0.7

Esta integração não reimplementa nem simplifica os programas recebidos. A build materializa os projetos originais em commits fixos e mantém os fontes integrais dos três programas adicionados ao Monitor.

| Integração | Repositório de origem | Commit fixado | Prova do arquivo recebido |
| --- | --- | --- | --- |
| Extrator de Notícias | `tysudess/Extrator-de-noticias-windows` | `ea43bb344d74dc2a32cc1d733aaabea54d763150` | `package.json` blob `72065b9f4bb489eebe2ce848d482022ee3a65fee` |
| Automação de Planilhas | `tysudess/automa-o-planilhas` | `51bd5386ea280edc2d56c6567be0113cfd84d2e5` | `package.json` blob `451a9ec3a7bdddda866922d841446e1c604b5034` |
| Capas | `tysudess/capas-windows-portable` | `87705432008b00f114d27d1f1645c2c89e649365` | `assets/principais_capas_cover.png` blob `a5eda7a1e3df8cfee064be3e8967abbfe59db250` |
| Editor de Vídeo | `tysudess/extrator-video-windows` | `92f031c22cf8c23c2f5dd15a1857a6df4186b97e` | `advanced_editor.py` blob `24c723c9f40946d1c13de0b9e23e55a182581e2d` |

Os blobs acima foram comparados com os arquivos dos ZIPs fornecidos antes da integração.

## Regra aplicada

- Extrator de Notícias: fonte integral e aplicativo Electron original.
- Automação de Planilhas: fonte integral e aplicativo Electron original.
- Capas: fonte integral, assets e Apps Script originais; o `MainWindow` original é hospedado dentro do Monitor sem editar seus arquivos.
- Extrator de Vídeos enviado: entra somente o Editor de Vídeo solicitado (`advanced_editor.py` + `range_slider.py`), sem trazer o shell do extrator.
- O Monitor apenas hospeda as interfaces e isola processos quando necessário. Motores, IPC, regras, persistência, coletores e algoritmos dos programas de origem não são reescritos.
