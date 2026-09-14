# RELEASE READINESS — PASSO 24

## Estado técnico

**NOVO PORTABLE COM COMPLIANCE DOCUMENTAL: VALIDADO TECNICAMENTE**

- commit da build: `2c52d9b00e06cb6becb7265371c5d35ab45492f8`
- run: `34794644131`
- ZIP: `MONITOR-DE-NOTICIAS-PYTHON-portable-windows-x64.zip`
- tamanho ZIP: `477381768` bytes
- tamanho descompactado: `830499134` bytes
- SHA-256: `36e161e4ce27103b6668a4471fe381b03ec28c1b6231a9fd137fa2672cfd9ede`
- suíte: `149 passed`
- Windows: Microsoft Windows Server 2025 / NT 10.0.26100 / AMD64

O run completo passou: build limpa, smoke local, transporte do ZIP, hash idêntico no segundo Windows sem checkout, reextração, primeira execução, primeiro smoke, reabertura, movimentação, paths com espaços/acentos, segundo smoke, preview, seeks, FFmpeg/FFprobe, exportação, shutdown, órfãos 0, temporários, logs, segredos e dados pessoais.

PORT-001 a PORT-005 continuam **RESOLVIDOS**. MIG-079 a MIG-083 continuam satisfeitos.

## Compliance presente no ZIP

A build inclui `THIRD_PARTY_NOTICES.txt`, `LICENSES-MANIFEST.json` e `licenses/`. Foram gerados 45 arquivos de licença/notice.

O run independente `34795191703` baixou exatamente o artifact do run `34794644131`, verificou SHA-256/tamanho, extraiu em Windows limpo e confirmou:

- THIRD_PARTY_NOTICES = PASS
- licenses/ = PASS
- LICENSES-MANIFEST = PASS
- 45 arquivos = presentes e legíveis
- dados/paths locais nos textos adicionados = 0

## PUB-001 — LICENÇAS

**STATUS: BLOQUEADO**

O Passo 24 corrigiu o excesso de coleta do PySide6 no aplicativo principal e incluiu os textos/notices oficiais disponíveis para os componentes inventariados. Porém o FFmpeg/FFprobe efetivamente distribuído informa `--enable-gpl --enable-version3`, com `libx264` e `libx265` habilitados.

O ZIP contém a GPLv3 e o LICENSE do FFmpeg, mas o repositório/artefato não demonstra disponibilização do **código-fonte correspondente exato** da build FFmpeg redistribuída no mesmo canal da futura publicação. Portanto o simples acréscimo dos textos legais não é evidência suficiente para declarar compliance integral.

Também não foi comprovada a correspondência exata do agregado `THIRD_PARTY_LICENSES` coletado de upstream com o binário yt-dlp nightly `2026.08.30.232658`.

Assim, as incertezas bloqueadoras de redistribuição não são zero.

## PUB-002 — SEGREDOS

**STATUS: RESOLVIDO**

O resultado do Passo 23 permanece válido: Gitleaks 8.30.1 auditou o histórico relevante; segredos reais não tratados = 0. O novo ciclo técnico também terminou com `SEGREDOS_REAIS_ENCONTRADOS=0` e `DADOS_PESSOAIS_NO_ZIP=0`.

## Fonte histórica Kotlin

O repositório `tysudess/noticias-monitor` continua sendo a fonte histórica e não foi alterado pelo Passo 24.

## Decisão

**NÃO PRONTO PARA MERGE/RELEASE**

Motivo: **PUB-001 permanece BLOQUEADO apesar de o novo ZIP estar tecnicamente validado e conter os notices/textos inventariados.**
