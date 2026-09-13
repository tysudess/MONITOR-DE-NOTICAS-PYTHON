# RELEASE CANDIDATE

## Identificação

- PROJETO: Monitor de Notícias Python
- REPOSITÓRIO: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- ORIGINAL HISTÓRICO: `tysudess/noticias-monitor`
- COMMIT VALIDADO: `0f9ec957b3e9f3fdf9b02f5dbe9bb0836310d60d`
- BRANCH: `migration/python-foundation`
- RUN: `34776048157`
- ZIP: `MONITOR-DE-NOTICIAS-PYTHON-portable-windows-x64.zip`
- SHA-256: `259739899fe044157d350ab077d877ef8dd9e024cd33939266e026e8df3563f4`
- TAMANHO ZIP: `651329315` bytes
- TAMANHO DESCOMPACTADO: `1262862742` bytes
- WINDOWS TESTADO: Microsoft Windows Server 2025 / NT 10.0.26100
- ARQUITETURA: x64
- STATUS: **PORTABLE VALIDADO**

## Versões

- versão do projeto: `0.0.1` (preservada de `pyproject.toml`)
- Python: `3.12.10`
- PySide6: `6.9.1`
- Qt: `6.9.1`
- empacotador: PyInstaller `6.15.0`, onedir
- FFmpeg: `n9.0.1-29-gad500d59cb-20260913`
- FFprobe: `n9.0.1-29-gad500d59cb-20260913`
- motor de preview: PySide6 QtMultimedia — `QMediaPlayer + QVideoWidget + QAudioOutput`
- PDF engine: `pypdf 6.18.0` + `pypdfium2 5.13.0/PDFium` + `Pillow 12.3.0`
- yt-dlp nightly: `2026.08.30.232658`
- yt-dlp stable: `2026.08.19`
- Deno: `2.9.6`
- outras dependências relevantes: requests, BeautifulSoup4, lxml e dependências transitivas empacotadas pelo PyInstaller

## Funcionalidades efetivamente exercitadas no candidato

O gate congelado percorreu a navegação das páginas do Monitor e fluxos controlados de Dashboard, Notícias, Vídeos, Demandas, Termos, Fontes, Histórico, Configurações, Automação, proxy/DPAPI, startup, Extrator, Editor PDF e Editor de Vídeo. Também executou preview, play/pause, seek, FFmpeg, FFprobe e exportação.

Notificação: evento/wiring foi exercitado; exibição visual humana de uma notificação nativa não foi observada manualmente.

## Limitações conhecidas

### LIMITAÇÃO

- O editor ativo preserva as ausências da baseline: split, delete/reorder de clipes, IN/OUT manual, undo/redo, compactação, concatenação e outras funções de placeholders não fazem parte do motor aprovado.
- Testes externos controlados não substituem uma sessão humana de avaliação visual de todas as telas.
- Integração com um proxy autenticado real externo não foi usada no gate; wiring/configuração/DPAPI foram exercitados.

### PENDÊNCIA DE EQUIVALÊNCIA, NÃO BUG COMPROVADO

- `MIG-061`: rotação/flip PDF tem suporte interno, mas ação visual ativa equivalente não foi comprovada.
- `MIG-114`: consumo do resolver de URL real do veículo para links Google News pelo Dashboard V5 ativo continua não comprovado. **NÃO DETERMINADO PELO CÓDIGO ANALISADO.**

### BUG

Nenhum bug funcional bloqueador permaneceu no ciclo final do portable.

## Bloqueadores de publicação pública

1. Completar/validar obrigações de licenças de terceiros para os binários e bibliotecas redistribuídos. O `THIRD_PARTY_NOTICES.txt` atual é um inventário resumido; conformidade jurídica integral é **NÃO DETERMINADO PELO CÓDIGO ANALISADO.**
2. Executar scanner dedicado de segredos sobre todo o histórico Git, inclusive blobs já removidos. A árvore atual e o ZIP validado estão limpos, mas a ausência em todo o histórico é **NÃO DETERMINADO PELO CÓDIGO ANALISADO.**

## Versionamento proposto

A versão formal já existente é `0.0.1`; ela deve ser preservada.

- tag sugerida: `v0.0.1`
- título sugerido: `Monitor de Notícias Python v0.0.1 — Windows Portable x64`

Nenhuma tag ou GitHub Release foi criada neste passo.
