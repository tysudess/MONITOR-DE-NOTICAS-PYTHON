# RELEASE READINESS — PASSO 23

## Estado oficial

**PORTABLE WINDOWS TÉCNICO: VALIDADO**

**PUBLICAÇÃO DO ZIP ATUAL: BLOQUEADA POR PUB-001**

O candidato técnico aprovado continua sendo exatamente o artefato produzido a partir de `0f9ec957b3e9f3fdf9b02f5dbe9bb0836310d60d` no run `34776048157`. O Passo 23 não rebuildou e não modificou esse ZIP.

- repositório: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- branch do artefato: `migration/python-foundation`
- workflow de build: `Passo 17 - Windows Portable`
- commit do artefato: `0f9ec957b3e9f3fdf9b02f5dbe9bb0836310d60d`
- ZIP: `MONITOR-DE-NOTICIAS-PYTHON-portable-windows-x64.zip`
- tamanho ZIP: `651329315` bytes
- tamanho descompactado: `1262862742` bytes
- SHA-256: `259739899fe044157d350ab077d877ef8dd9e024cd33939266e026e8df3563f4`
- plataforma validada: Microsoft Windows Server 2025 / NT 10.0.26100 / AMD64
- suíte: `149 passed`

## Gate técnico

Permanece integralmente aprovado: build, ZIP, hash, segundo runner, reextração, primeiro smoke, reabertura, movimentação, paths com espaços/acentos, segundo smoke, shutdown, processos órfãos, temporários, logs, segredos e dados pessoais do ciclo técnico.

PORT-001 a PORT-005 permanecem **RESOLVIDOS**. Os MIGs de portable aprovados no Passo 22 não são revertidos pela auditoria de publicação.

## PUB-001 — LICENÇAS

**STATUS: BLOQUEADO**

A auditoria comprovou que o empacotamento validado usa `collect_all("PySide6")` e inclui módulos Qt além dos realmente necessários, inclusive módulos que a documentação oficial do Qt lista como GPL-only para usuários open-source (`Qt Graphs`, `Qt HTTP Server`, `Qt Network Authorization`, `Qt Quick 3D`). A build foi feita com a distribuição pública de PySide6 via pip; eventual licença comercial Qt aplicável ao projeto é **NÃO DETERMINADO PELO CÓDIGO/ARTEFATO ANALISADO**.

Também são redistribuídos componentes com obrigações próprias, incluindo QtWebEngine/Chromium, FFmpeg/FFprobe com build GPL (`--enable-gpl --enable-version3`), executáveis PyInstaller de yt-dlp que o upstream classifica como GPLv3+, e PDFium/pypdfium2 cujo upstream exige licenças de dependências junto à distribuição binária.

A inspeção do artifact exato encontrou o `THIRD_PARTY_NOTICES.txt`, mas o conjunto atual não fornece evidência suficiente para declarar satisfeitas todas as obrigações de redistribuição.

**ARTEFATO VALIDADO PRECISA SER ALTERADO PARA CONFORMIDADE.**

**NOVA BUILD + NOVO CICLO DE VALIDAÇÃO NECESSÁRIOS: SIM.**

Nenhuma alteração foi aplicada ao ZIP neste passo.

## PUB-002 — SEGREDOS EM TODO O HISTÓRICO

**STATUS: RESOLVIDO**

Auditoria dedicada executada no run `34791248748` com Gitleaks `8.30.1`, checkout completo e fetch explícito das branches/tags.

Escopo registrado:
- 168 commits alcançáveis pelo Git;
- 4 branches remotas;
- 0 tags;
- Gitleaks reportou 164 commits efetivamente percorridos em seu modo `git`.

Resultado histórico:
- findings Gitleaks: 2;
- regra: `generic-api-key`;
- ambos em `scripts/pyi_runtime_portable_validation.py`;
- classificação: **DADOS DE TESTE**, pois o código histórico os declara explicitamente `fake_secret`, `somente dado fictício`, com literais `SEGREDO-FICTICIO-PASSO17/18` usados para testar DPAPI;
- segredos reais: **0**;
- findings não determinados: **0**;
- objetos históricos com nomes sensíveis suspeitos: **0**;
- blobs históricos >=5 MiB: **0**.

A única correspondência textual a marcador de private key veio do próprio padrão de busca do workflow de auditoria; Gitleaks não encontrou chave privada real.

O ZIP exato também foi escaneado após revalidação de SHA-256/tamanho. Houve 4 findings `generic-api-key` em recursos de terceiros (`qtwebengine_resources.pak` e `pypdfium2/internal/consts.py`), classificados como falsos positivos de recursos/constantes de terceiros. Segredos reais no ZIP: **0**. Estado pessoal evidente: **0**.

**SEGREDOS REAIS NÃO TRATADOS = 0**

Revogação/rotação: **NÃO necessária**.
Reescrita de histórico: **NÃO necessária**.

## Documento detalhado

Ver `docs/PUBLICATION_COMPLIANCE.md`.

## Fonte histórica Kotlin

Fonte funcional de referência: `df1701ba5427a04954093e8ebed63f26abb2b2b7` + transformações comprovadas do workflow V8. O repositório Kotlin não foi alterado no Passo 23.

## Decisão

**NÃO PRONTO PARA MERGE/RELEASE**

Motivo: **PUB-001 BLOQUEADO E NOVO PORTABLE NECESSÁRIO PARA COMPLIANCE DE LICENÇAS.**
