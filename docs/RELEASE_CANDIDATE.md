# RELEASE CANDIDATE — PASSO 24

## Identificação

- projeto: Monitor de Notícias Python
- repositório: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- branch: `migration/python-foundation`
- original histórico: `tysudess/noticias-monitor`

### Candidato funcional anterior

- commit: `0f9ec957b3e9f3fdf9b02f5dbe9bb0836310d60d`
- run: `34776048157`
- SHA-256: `259739899fe044157d350ab077d877ef8dd9e024cd33939266e026e8df3563f4`

### Novo candidato do Passo 24

- commit da build: `2c52d9b00e06cb6becb7265371c5d35ab45492f8`
- run: `34794644131`
- ZIP: `MONITOR-DE-NOTICIAS-PYTHON-portable-windows-x64.zip`
- tamanho ZIP: `477381768` bytes
- tamanho descompactado: `830499134` bytes
- SHA-256: `36e161e4ce27103b6668a4471fe381b03ec28c1b6231a9fd137fa2672cfd9ede`
- Windows: Microsoft Windows Server 2025 / NT 10.0.26100 / AMD64
- arquitetura: x64
- status técnico: **VALIDADO**
- status de publicação: **BLOQUEADO POR PUB-001**

## Versões

- projeto: `0.0.1`
- Python: `3.12.10`
- PySide6: `6.9.1`
- Qt: `6.9.1`
- PyInstaller: `6.15.0`
- yt-dlp nightly: `2026.08.30.232658`
- yt-dlp stable: `2026.08.19`
- Deno: `2.9.6`
- FFmpeg/FFprobe: `n9.0.1-29-gad500d59cb-20260913`
- preview: `QMediaPlayer + QVideoWidget + QAudioOutput`
- PDF: pypdf `6.18.0`, pypdfium2 `5.13.0`/PDFium, Pillow `12.3.0`

## Mudança do Passo 24

**CÓDIGO FUNCIONAL ALTERADO = NÃO.**

O candidato muda somente empacotamento/compliance:

- o aplicativo principal não usa mais `collect_all("PySide6")`; PyInstaller coleta o grafo Qt necessário pelos imports reais;
- `pypdfium2` mantém a coleta necessária ao motor PDF;
- a build adiciona `licenses/`, `LICENSES-MANIFEST.json` e THIRD_PARTY_NOTICES rastreável;
- o helper Globoplay permanece funcional e preserva seus imports QtWebEngine reais.

## Validação técnica

Suíte pré-build: 149/149 PASS.

O build local congelado e o segundo Windows independente comprovaram novamente navegação, notícias, vídeos, banco/persistência, deduplicação, automação, proxy/DPAPI, startup, notificação/wiring, Extrator, PDF, Editor de Vídeo, preview/play-pause, seeks 500/1000/1500, FFmpeg, FFprobe e exportação H.264/AAC.

O segundo smoke após movimentação também passou. Hash build/runner idêntico, processos órfãos 0, segredos reais 0 e dados pessoais evidentes 0.

## Compliance físico

Run independente `34795191703`: PASS.

O mesmo ZIP foi extraído em Windows independente e comprovou:

- `THIRD_PARTY_NOTICES.txt` presente;
- `LICENSES-MANIFEST.json` presente;
- `licenses/` presente;
- 45 arquivos de licença/notice legíveis;
- textos adicionados sem paths/dados locais do desenvolvedor.

## Bloqueador restante

**PUB-001 permanece BLOQUEADO.**

A build FFmpeg/FFprobe usada está explicitamente configurada com `--enable-gpl --enable-version3`, `libx264` e `libx265`. Os textos GPL estão presentes, mas o candidato não demonstra disponibilização do código-fonte correspondente exato da build redistribuída no mesmo canal de uma futura publicação. Logo, a presença dos textos não basta para declarar a obrigação de redistribuição integralmente satisfeita.

A correspondência exata do THIRD_PARTY_LICENSES coletado para o binário yt-dlp nightly também não está comprovada pelo artifact.

PUB-002 permanece RESOLVIDO e segredos reais não tratados = 0.

## Decisão

**NÃO PRONTO PARA MERGE/RELEASE**

Nenhuma tag, merge ou GitHub Release deve ser criada enquanto PUB-001 permanecer bloqueado.
