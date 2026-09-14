# PUBLICATION COMPLIANCE — PASSO 24

## Referência anterior

- portable funcional validado: `0f9ec957b3e9f3fdf9b02f5dbe9bb0836310d60d`
- run anterior: `34776048157`
- SHA-256 anterior: `259739899fe044157d350ab077d877ef8dd9e024cd33939266e026e8df3563f4`

## Novo candidato de compliance

- commit da build: `2c52d9b00e06cb6becb7265371c5d35ab45492f8`
- run: `34794644131`
- ZIP: `MONITOR-DE-NOTICIAS-PYTHON-portable-windows-x64.zip`
- tamanho ZIP: `477381768` bytes
- tamanho descompactado: `830499134` bytes
- SHA-256: `36e161e4ce27103b6668a4471fe381b03ec28c1b6231a9fd137fa2672cfd9ede`
- suíte pré-build: `149 passed`
- segundo Windows independente: PASS
- verificação independente dos arquivos de compliance: run `34795191703`, PASS

Nenhum arquivo em `src/` foi alterado no Passo 24.

# PUB-001 — LICENÇAS

## Mudanças realizadas

O `MonitorDeNoticias.spec` deixou de executar `collect_all("PySide6")`. PyInstaller passou a seguir os imports reais do aplicativo. O log do novo build confirma no aplicativo principal QtCore, QtGui, QtWidgets, QtNetwork, QtMultimedia e QtMultimediaWidgets; os módulos Qt Graphs, Qt HTTP Server, Qt Network Authorization e Qt Quick 3D que apareciam por coleta global não aparecem no grafo principal do novo candidato.

O helper Globoplay continua empacotando os módulos Qt realmente importados por ele, incluindo QtWebEngine. Nenhum motor ou comportamento funcional foi removido; o smoke local e os dois smokes externos passaram.

A build agora cria:

- `THIRD_PARTY_NOTICES.txt` rastreável;
- `LICENSES-MANIFEST.json`;
- diretório `licenses/`;
- licença do runtime Python;
- textos de licença/notice fornecidos pelas distribuições Python instaladas para PySide6/Qt/Shiboken, requests/transitivas, BeautifulSoup, lxml, pypdf, pypdfium2/PDFium, Pillow e demais itens do inventário;
- textos oficiais de FFmpeg;
- LICENSE e THIRD_PARTY_LICENSES de yt-dlp stable/nightly;
- licença do Deno.

A build registrou `PORTABLE_LICENSE_FILE_COUNT=45`. Um Windows independente baixou o artifact exato, recalculou SHA/tamanho, extraiu e confirmou os 45 arquivos legíveis, o manifest e THIRD_PARTY_NOTICES; nenhum texto adicionado continha path/dado local do ambiente de desenvolvimento.

## Inventário resumido

| Componente | Versão | Redistribuído | Evidência de licença/notice no novo ZIP | Status |
|---|---:|---|---|---|
| Python runtime | 3.12.10 | SIM | `licenses/python-runtime/LICENSE.txt` | OK para texto |
| PySide6 / Qt / Shiboken | 6.9.1 | SIM | arquivos oficiais das distribuições instaladas em `licenses/python/` | OK para textos; obrigações de distribuição permanecem condicionadas ao regime Qt aplicável |
| requests + transitivas | build registrada | SIM | arquivos oficiais em `licenses/python/` | OK para textos |
| beautifulsoup4 / soupsieve | build registrada | SIM | arquivos oficiais em `licenses/python/` | OK para textos |
| lxml | 6.1.3 | SIM | arquivos oficiais em `licenses/python/` | OK para textos |
| pypdf | 6.18.0 | SIM | arquivos oficiais em `licenses/python/` | OK para textos |
| pypdfium2 / PDFium | 5.13.0 | SIM | arquivos oficiais em `licenses/python/` | OK para textos/notices disponíveis na distribuição |
| Pillow | 12.3.0 | SIM | arquivos oficiais em `licenses/python/` | OK para texto |
| yt-dlp stable | 2026.08.19 | SIM | LICENSE + THIRD_PARTY_LICENSES | OK para textos |
| yt-dlp nightly | 2026.08.30.232658 | SIM | LICENSE + THIRD_PARTY_LICENSES upstream | OK para textos; correspondência exata do agregado ao build nightly não é comprovada pelo artifact |
| Deno | 2.9.6 | SIM | `licenses/deno/LICENSE.md` | OK para texto |
| FFmpeg / FFprobe | n9.0.1-29-gad500d59cb-20260913 | SIM | COPYING.GPLv3 + LICENSE.md | BLOQUEADO para publicação |

## Bloqueador restante de PUB-001

O segundo runner registrou a configuração efetiva do FFmpeg com `--enable-gpl --enable-version3` e `--enable-libx264 --enable-libx265`. Portanto a build distribuída está no regime GPLv3 aplicável ao conjunto efetivamente habilitado.

O novo ZIP inclui os textos GPL/FFmpeg, mas **não inclui nem demonstra disponibilização do código-fonte correspondente exato da build FFmpeg/BtbN e de seus componentes GPL no mesmo canal da distribuição**. A documentação oficial do FFmpeg recomenda explicitamente distribuir o source correspondente exatamente aos binários e hospedá-lo junto da distribuição binária. Esse requisito objetivo não foi satisfeito por este candidato apenas com `COPYING.GPLv3.txt` e `LICENSE.md`.

Além disso, para o yt-dlp nightly, o arquivo THIRD_PARTY_LICENSES coletado de upstream não prova por si só correspondência byte-a-byte com a build nightly `2026.08.30.232658`.

Por isso, sem inventar conclusão jurídica:

**PUB-001 — BLOQUEADO**

**LICENÇAS INCERTAS/BLOQUEADORAS RESTANTES > 0**

O candidato do Passo 24 melhora e comprova a presença dos notices/textos, mas ainda não demonstra todas as obrigações necessárias para publicação pública.

# PUB-002 — SEGREDOS

Permanece **RESOLVIDO** conforme Passo 23.

- scanner: Gitleaks 8.30.1
- segredos reais históricos: 0
- findings não determinados: 0
- segredos reais não tratados: 0
- nova validação técnica do ZIP: `SEGREDOS_REAIS_ENCONTRADOS=0`
- dados pessoais evidentes no ZIP: 0

# Resultado do Passo 24

- novo ZIP técnico: VALIDADO
- notices/textos no ZIP: PASS
- PUB-001: BLOQUEADO
- PUB-002: RESOLVIDO
- merge/tag/release: NÃO executados

**NÃO PRONTO PARA MERGE/RELEASE**
