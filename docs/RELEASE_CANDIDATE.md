# RELEASE CANDIDATE

## Identificação técnica validada

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
- STATUS TÉCNICO: **PORTABLE VALIDADO**
- STATUS DE PUBLICAÇÃO: **BLOQUEADO — NOVO CANDIDATO DE COMPLIANCE NECESSÁRIO**

O Passo 23 não altera o ZIP acima e não o apresenta como publicável.

## Versões comprovadas

- versão do projeto: `0.0.1`
- Python: `3.12.10`
- PySide6: `6.9.1`
- Qt: `6.9.1`
- PyInstaller: `6.15.0`, onedir
- FFmpeg: `n9.0.1-29-gad500d59cb-20260913`
- FFprobe: `n9.0.1-29-gad500d59cb-20260913`
- preview: PySide6 QtMultimedia (`QMediaPlayer + QVideoWidget + QAudioOutput`)
- PDF: `pypdf 6.18.0` + `pypdfium2 5.13.0/PDFium` + `Pillow 12.3.0`
- yt-dlp nightly: `2026.08.30.232658`
- yt-dlp stable: `2026.08.19`
- Deno: `2.9.6`

## Funcionalidades técnicas

O candidato permanece tecnicamente aprovado nos fluxos já validados: Dashboard, Notícias, Vídeos, Demandas, Termos, Fontes, Histórico, Configurações, Automação, proxy/DPAPI, startup, notificações/wiring, Extrator, Editor PDF, Editor de Vídeo, preview, play/pause, seek, FFmpeg, FFprobe e exportação.

Nenhum bug funcional bloqueador foi introduzido ou descoberto pelo Passo 23.

## Compliance de publicação — Passo 23

### PUB-001 — Licenças

**BLOQUEADO.**

O ZIP atual não deve ser publicado. A auditoria provou que o empacotamento coleta todo o PySide6 e inclui módulos Qt GPL-only para usuários open-source, além de QtWebEngine/Chromium. Também redistribui FFmpeg/FFprobe em build GPLv3-or-later, executáveis PyInstaller de yt-dlp classificados pelo upstream como GPLv3+, e PDFium com licenças de dependências que precisam acompanhar distribuições binárias.

A existência de eventual licença comercial Qt aplicável é **NÃO DETERMINADO PELO CÓDIGO/ARTEFATO ANALISADO**. O repositório também não estabelece um regime GPL da aplicação que permita concluir conformidade com os módulos GPL-only coletados.

O `THIRD_PARTY_NOTICES.txt` presente no ZIP é um inventário resumido e não é evidência suficiente do conjunto completo de obrigações aplicáveis.

**NOVA BUILD NECESSÁRIA POR COMPLIANCE = SIM.**

O próximo candidato deverá, antes de nova validação, delimitar os módulos realmente utilizados e incluir os textos/notices/fontes ou ofertas exigidos pelo regime de distribuição escolhido.

### PUB-002 — Segredos no histórico

**RESOLVIDO.**

Run de auditoria: `34791248748`.
Scanner: Gitleaks `8.30.1`.

- refs: todas as branches remotas e tags buscadas explicitamente;
- commits alcançáveis registrados: 168;
- branches remotas: 4;
- tags: 0;
- findings históricos: 2;
- classificação: 2 dados fictícios de teste (`fake_secret` para DPAPI);
- segredos reais históricos: 0;
- findings não determinados: 0;
- arquivos históricos sensíveis suspeitos: 0;
- blobs históricos >=5 MiB: 0;
- necessidade de revogação/rotação: NÃO;
- necessidade de reescrita do histórico: NÃO.

O ZIP exato também foi escaneado: 4 padrões em recursos de terceiros, todos classificados como falsos positivos; segredos reais no ZIP = 0; estado pessoal evidente = 0.

Detalhes: `docs/PUBLICATION_COMPLIANCE.md`.

## Limitações conhecidas anteriores

- O editor ativo preserva ausências da baseline já documentadas (split, delete/reorder, IN/OUT manual, undo/redo, compactação, concatenação etc.).
- O gate técnico não substitui inspeção visual humana integral.
- `MIG-061` e `MIG-114` continuam pendências de equivalência já documentadas, não bugs comprovados do portable.

## Versionamento proposto

A versão existente continua `0.0.1`.

- tag anteriormente sugerida: `v0.0.1`;
- título anteriormente sugerido: `Monitor de Notícias Python v0.0.1 — Windows Portable x64`.

**Não criar tag/release enquanto PUB-001 estiver bloqueado.**

## Decisão

**NÃO PRONTO PARA MERGE/RELEASE**
