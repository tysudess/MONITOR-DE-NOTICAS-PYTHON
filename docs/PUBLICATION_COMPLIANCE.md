# PUBLICATION COMPLIANCE — PASSO 23

## Estado congelado

- repositório: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- branch: `migration/python-foundation`
- commit do portable tecnicamente validado: `0f9ec957b3e9f3fdf9b02f5dbe9bb0836310d60d`
- run validado: `34776048157`
- ZIP: `MONITOR-DE-NOTICIAS-PYTHON-portable-windows-x64.zip`
- tamanho: `651329315` bytes
- SHA-256: `259739899fe044157d350ab077d877ef8dd9e024cd33939266e026e8df3563f4`

O Passo 23 não altera a validade técnica desse ZIP. A auditoria abaixo trata somente de publicação.

# PUB-001 — CONFORMIDADE DAS LICENÇAS REDISTRIBUÍDAS

## Resultado

**PUB-001 — BLOQUEADO**

**ARTEFATO VALIDADO PRECISA SER ALTERADO PARA CONFORMIDADE.**

Consequência: **NOVA BUILD + NOVO CICLO DE VALIDAÇÃO SERÃO NECESSÁRIOS** antes de publicação. Nenhum rebuild foi executado no Passo 23.

## Evidência de composição do portable

O `MonitorDeNoticias.spec` usado na build faz `collect_all("PySide6")` e `collect_all("pypdfium2")`, incluindo datas, binários e hidden imports. O log da build validada confirma que módulos Qt adicionais foram efetivamente analisados/empacotados, entre eles `QtGraphs`, `QtHttpServer`, `QtNetworkAuth`, `QtQuick3D`, `QtWebEngineCore` e outros.

O script da build baixa e redistribui também:

- `yt-dlp.exe` nightly;
- `yt-dlp-stable.exe`;
- `deno.exe`;
- `ffmpeg.exe`;
- `ffprobe.exe`.

A inspeção do ZIP exato do run `34776048157`, com hash e tamanho novamente verificados, encontrou como arquivo de licença/notice de topo identificado pelo gate de auditoria apenas:

- `MonitorDeNoticias/THIRD_PARTY_NOTICES.txt`.

O arquivo atual é um inventário resumido; não substitui todos os textos/avisos/ofertas de código-fonte que possam ser exigidos pelas licenças aplicáveis.

## Dependências Python da build validada

| Pacote | Versão da build | Finalidade | Produção | Redistribuído pelo PyInstaller | Licença comprovada | Status de compliance |
|---|---:|---|---|---|---|---|
| PySide6 | 6.9.1 | UI/Qt | SIM | SIM | LGPLv3/GPLv3/comercial, conforme módulos/distribuição | BLOQUEADO — composição inclui módulos GPL-only e licença comercial não comprovada |
| PySide6-Essentials | 6.9.1 | Qt essencial | SIM | SIM | regime Qt/PySide6 | BLOQUEADO junto ao Qt |
| PySide6-Addons | 6.9.1 | módulos Qt adicionais | SIM | SIM | regime Qt/PySide6 | BLOQUEADO junto ao Qt |
| shiboken6 | 6.9.1 | binding runtime | SIM | SIM | regime Qt for Python | BLOQUEADO junto ao Qt |
| requests | 2.34.2 | HTTP | SIM | SIM | Apache-2.0 | texto/notice deve ser preservado no candidato de compliance |
| charset-normalizer | 3.5.1 | dependência requests | SIM | SIM | MIT | texto/notice deve ser preservado |
| idna | 3.19 | dependência requests | SIM | SIM | BSD-3-Clause | texto/notice deve ser preservado |
| urllib3 | 2.7.0 | dependência requests | SIM | SIM | MIT | texto/notice deve ser preservado |
| certifi | 2026.7.22 | CA bundle | SIM | SIM | MPL-2.0 | obrigações de notice/texto devem ser preservadas |
| beautifulsoup4 | 4.15.0 | parsing HTML | SIM | SIM | MIT | texto/notice deve ser preservado |
| soupsieve | 2.9.2 | dependência BeautifulSoup | SIM | SIM | MIT | texto/notice deve ser preservado |
| lxml | 6.1.3 | parsing XML/HTML | SIM | SIM | BSD-3-Clause | texto/notice e licenças nativas aplicáveis devem ser preservados |
| pypdf | 6.18.0 | PDF | SIM | SIM | BSD-3-Clause | texto/notice deve ser preservado |
| pypdfium2 | 5.13.0 | PDFium/renderização | SIM | SIM | BSD-3-Clause / Apache-2.0 + licenças do PDFium/dependências | BLOQUEADO — upstream exige que licenças do PDFium/dependências acompanhem distribuição binária |
| Pillow | 12.3.0 | imagem/PDF | SIM | SIM | MIT-CMU | texto/notice deve ser preservado |
| typing_extensions | 4.16.0 | transitiva | SIM | SIM quando alcançada | PSF-2.0 | texto/notice aplicável |
| pytest | 9.1.1 | testes | NÃO | NÃO (`excludes=["pytest"]`) | MIT | build/teste, não componente de produção intencional |

Dependências de build como PyInstaller 6.15.0, setuptools, altgraph, pefile, pywin32-ctypes e pyinstaller-hooks-contrib são distinguidas das dependências de runtime. O bootloader gerado por PyInstaller é redistribuído sob a exceção específica do projeto, que permite distribuir o bundle sob a licença da aplicação/dependências.

## PySide6 / Qt / preview

- versão: PySide6/Qt `6.9.1`;
- preview: `QMediaPlayer + QVideoWidget + QAudioOutput` / QtMultimedia;
- backend empacotado: plugins/DLLs Qt, incluindo backend multimídia;
- Qt for Python Community Edition: LGPLv3/GPLv3; licença comercial é alternativa somente quando efetivamente adquirida/usada;
- a build foi feita a partir dos pacotes públicos instalados via `pip`, e não há evidência de pacote comercial Qt;
- licença comercial Qt aplicável ao usuário/projeto: **NÃO DETERMINADO PELO CÓDIGO/ARTEFATO ANALISADO**.

O log da build prova inclusão/análise de módulos que a documentação oficial do Qt lista como GPLv3 para usuários open-source, incluindo `Qt Graphs`, `Qt HTTP Server`, `Qt Network Authorization` e `Qt Quick 3D`. O empacotamento atual usa `collect_all("PySide6")`, portanto inclui muito além do conjunto efetivamente necessário pela aplicação.

`QtWebEngineCore` também é empacotado pelo helper Globoplay. Qt WebEngine incorpora Chromium e sua distribuição exige conformidade tanto com a licença do Qt WebEngine quanto com as licenças de terceiros do Chromium.

**Conclusão objetiva:** o candidato atual não possui evidência suficiente para publicação sob um regime de licença definido. A correção esperada para um próximo passo é reduzir o empacotamento aos módulos realmente utilizados e/ou estabelecer expressamente o regime de licença aplicável, acrescentando os textos/avisos exigidos; isso muda o conteúdo do ZIP e exige novo candidato.

## FFmpeg / FFprobe

- versão observada: `n9.0.1-29-gad500d59cb-20260913`;
- origem preferencial da build: BtbN `ffmpeg-n9.0-latest-win64-gpl-9.0.zip`;
- configuração observada no run validado: inclui `--enable-gpl` e `--enable-version3`, além de bibliotecas GPL como x264/x265;
- licença da build distribuída: **GPLv3-or-later** conforme seleção de licença do FFmpeg para `gpl + version3`;
- obrigação de publicação não está satisfeita apenas pelo resumo atual: é necessário fornecer os textos/avisos e cumprir as obrigações de código-fonte/corresponding source aplicáveis à build redistribuída.

## yt-dlp

As duas variantes distribuídas são executáveis PyInstaller oficiais (`yt-dlp.exe`). O próprio projeto yt-dlp informa que, embora o código principal seja Unlicense, os executáveis PyInstaller incluem componentes GPLv3+ e o trabalho combinado é **GPLv3+**, com detalhes em `THIRD_PARTY_LICENSES.txt`.

O candidato atual não inclui prova suficiente desses textos/obrigações no nível exigido para publicação.

## Deno

- versão: `2.9.6`;
- licença principal: MIT;
- o copyright/permission notice precisa ser preservado para redistribuição;
- dependências internas do binário devem ser tratadas conforme os notices oficiais da distribuição correspondente no próximo candidato.

## PDF engine

- pypdf 6.18.0: BSD-3-Clause;
- pypdfium2 5.13.0: BSD-3-Clause/Apache-2.0;
- PDFium: BSD-style + licenças de dependências.

O upstream do pypdfium2 declara expressamente que a licença do PDFium e as licenças de suas dependências devem acompanhar distribuições binárias. O candidato atual não tem evidência suficiente de que esse conjunto completo esteja presente/adequadamente exposto para redistribuição.

## THIRD_PARTY_NOTICES

O arquivo atual já estava dentro do ZIP validado, mas é apenas um resumo. Alterá-lo ou adicionar textos integrais de licença que precisam acompanhar o usuário altera o conteúdo distribuído. Portanto o Passo 23 não modifica silenciosamente esse arquivo e não produz um ZIP diferente.

## Licenças incompatíveis/incertas

- licença comercial Qt: **NÃO DETERMINADO PELO CÓDIGO/ARTEFATO ANALISADO**;
- regime de publicação da própria aplicação compatível com módulos Qt GPL-only empacotados: não estabelecido no repositório;
- conjunto completo de textos/notices e oferta/código-fonte exigidos para FFmpeg GPLv3+, yt-dlp executável GPLv3+, Qt/Chromium e PDFium: não demonstrado no ZIP atual.

Não foi encontrada evidência para declarar uma incompatibilidade jurídica definitiva; foi encontrada evidência suficiente para declarar **compliance incompleto** e necessidade de novo candidato antes da publicação.

# PUB-002 — AUDITORIA DE SEGREDOS EM TODO O HISTÓRICO GIT

## Ferramenta e escopo

**PUB-002 — RESOLVIDO**

- ferramenta: Gitleaks `8.30.1`;
- checksum do scanner verificado antes da execução;
- comando principal: `gitleaks git --redact --report-format json --report-path ... .`;
- checkout: `fetch-depth: 0`;
- refs buscadas explicitamente: todas as branches remotas e tags;
- alcance registrado pelo gate: 168 commits alcançáveis, 4 branches remotas, 0 tags;
- Gitleaks informou 164 commits efetivamente percorridos em seu modo `git`;
- verificação complementar: marcadores de private key, nomes históricos suspeitos e blobs >= 5 MiB;
- ZIP validado também foi baixado pelo ID do artifact/run, teve SHA-256/tamanho confirmados e foi escaneado separadamente.

Run da auditoria: `34791248748`.

## Findings do histórico

Gitleaks: **2 findings**, regra `generic-api-key`, ambos em `scripts/pyi_runtime_portable_validation.py`, em dois commits históricos.

Classificação de ambos: **DADO DE TESTE / FALSO POSITIVO DE SEGREDO REAL**.

Contexto comprovado no próprio código histórico:

- variável `fake_secret`;
- comentários dizem explicitamente `somente dado fictício`;
- valores literais `SEGREDO-FICTICIO-PASSO17` e `SEGREDO-FICTICIO-PASSO18`;
- finalidade: provar que DPAPI não deixa o dado fictício em texto puro.

Nenhuma credencial real é inferida desses findings.

## Private keys e objetos históricos suspeitos

A verificação textual contou 1 ocorrência de padrão `BEGIN ... PRIVATE KEY`, mas essa ocorrência foi introduzida pelo próprio workflow de auditoria como padrão de busca, não por uma chave privada. Gitleaks não reportou private key.

- objetos históricos com nomes suspeitos (`.env`, credentials/secrets, DB/SQLite, logs, ZIP, PEM/key/P12/PFX): **0**;
- blobs históricos >= 5 MiB: **0**.

## Scan do ZIP validado

O ZIP escaneado é exatamente o aprovado:

- SHA-256 verificado: `259739899fe044157d350ab077d877ef8dd9e024cd33939266e026e8df3563f4`;
- tamanho verificado: `651329315` bytes.

Gitleaks encontrou 4 padrões `generic-api-key`:

- 3 em `_internal/PySide6/resources/qtwebengine_resources.pak`;
- 1 em `_internal/pypdfium2/internal/consts.py`.

Classificação: **FALSOS POSITIVOS DE RECURSOS/CONSTANTES DE TERCEIROS**. Não são arquivos de configuração do projeto, não aparecem como credenciais do Monitor e não correspondem a segredo fornecido pelo usuário.

Arquivos de estado pessoal evidente procurados no ZIP (`news.db`, `videos.db`, prefs, cookies, `.env`, logs, credentials/secrets): **0 correspondências**.

## Resultado consolidado PUB-002

- findings totais do histórico: 2;
- segredos reais no histórico: **0**;
- dados de teste: **2**;
- falsos positivos históricos adicionais: **0**;
- findings não determinados: **0**;
- private keys reais: **0**;
- necessidade de revogação/rotação: **NÃO**;
- necessidade de reescrita do histórico: **NÃO**;
- findings no ZIP: 4;
- segredos reais no ZIP: **0**;
- falsos positivos no ZIP: **4**;
- dados pessoais/estado pessoal evidente no ZIP: **0**.

**SEGREDOS REAIS ENCONTRADOS NO HISTÓRICO = 0**

**SEGREDOS REAIS NÃO TRATADOS = 0**

# Conclusão do Passo 23

- PUB-001: **BLOQUEADO**;
- PUB-002: **RESOLVIDO**;
- nova build necessária por compliance: **SIM**;
- portable técnico anterior: continua **VALIDADO**, mas não é o artefato apto à publicação pública;
- merge/tag/release/rebuild: não executados neste passo.

## Decisão

**NÃO PRONTO PARA MERGE/RELEASE**

Motivo: **NOVO PORTABLE NECESSÁRIO PARA INCLUIR/DELIMITAR O CONJUNTO DE COMPONENTES E COMPLIANCE DE LICENÇAS REDISTRIBUÍDAS.**
