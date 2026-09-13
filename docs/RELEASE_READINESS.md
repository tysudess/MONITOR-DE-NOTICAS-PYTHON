# RELEASE READINESS — PASSO 22

## Estado oficial

**PORTABLE WINDOWS: VALIDADO**

O candidato técnico aprovado é exatamente o artefato produzido a partir de `0f9ec957b3e9f3fdf9b02f5dbe9bb0836310d60d` no run `34776048157`. Nenhum commit mais recente deve ser apresentado como origem desse ZIP.

- repositório: `tysudess/MONITOR-DE-NOTICAS-PYTHON`
- branch do artefato: `migration/python-foundation`
- workflow: `Passo 17 - Windows Portable`
- commit do artefato: `0f9ec957b3e9f3fdf9b02f5dbe9bb0836310d60d`
- ZIP: `MONITOR-DE-NOTICIAS-PYTHON-portable-windows-x64.zip`
- tamanho ZIP: `651329315` bytes
- tamanho descompactado: `1262862742` bytes
- SHA-256: `259739899fe044157d350ab077d877ef8dd9e024cd33939266e026e8df3563f4`
- plataforma validada: Microsoft Windows Server 2025 / NT 10.0.26100 / AMD64
- arquitetura do pacote: Windows x64

## Gate técnico final

- BUILD = PASS
- ZIP = PASS
- HASH = PASS
- SEGUNDO RUNNER = PASS
- REEXTRAÇÃO = PASS
- PRIMEIRO SMOKE = PASS
- REABERTURA = PASS
- MOVIMENTAÇÃO = PASS
- PATH COM ESPAÇOS = PASS
- PATH COM ACENTOS = PASS
- SEGUNDO SMOKE = PASS
- SHUTDOWN = PASS
- PROCESSOS ÓRFÃOS = PASS (`0`)
- TEMPORÁRIOS = PASS
- LOGS = PASS
- SEGREDOS NO ARTEFATO = PASS (`SEGREDOS_REAIS_ENCONTRADOS=0`)
- DADOS PESSOAIS NO ZIP = PASS (`DADOS_PESSOAIS_NO_ZIP=0`)

A suíte que acompanhou o candidato aprovado terminou em `149 passed`, sem falhas.

## PORT-001 a PORT-005

Todos os bloqueadores PORT conhecidos foram resolvidos e preservados historicamente em `docs/MIGRACAO_PASSO_21.md`.

## MIGs de portable

O ciclo externo completo fornece evidência objetiva para promover:
- `MIG-002` — raiz portable/frozen;
- `MIG-079` — entrada Desktop original;
- `MIG-080` — transformações/workflow de build;
- `MIG-081` — empacotamento PyInstaller do editor/aplicação final;
- `MIG-082` — cinco binários portáteis;
- `MIG-083` — `BUILD-SHA` e hash do ZIP.

Estado consolidado: 116 MIGs; 77 APROVADOS; 37 EM TESTE; 2 PENDENTES (`MIG-061`, `MIG-114`); 0 BLOQUEADOS.

## Separação entre artefato e documentação

`docs/**` não entra no ZIP e também não está nos paths que disparam a workflow portable. Portanto mudanças documentais posteriores devem permanecer em commit separado e NÃO alteram o candidato `0f9ec957b3e9f3fdf9b02f5dbe9bb0836310d60d`.

## Bloqueadores para publicação pública

O portable está tecnicamente validado, porém este Passo 22 não prova dois requisitos de governança para uma publicação pública:

1. **Licenças de terceiros:** `portable/THIRD_PARTY_NOTICES.txt` inventaria as dependências, mas o build copia esse resumo junto aos binários e não há evidência suficiente, neste passo, de que todos os textos/avisos/código-fonte ou ofertas de código-fonte exigidos pelas licenças aplicáveis de componentes nativos/copyleft estejam completos. Conformidade jurídica integral: **NÃO DETERMINADO PELO CÓDIGO ANALISADO.**
2. **Histórico Git completo:** a árvore atual e o artefato não exibem segredos ou estado pessoal, mas não foi executado um scanner dedicado sobre todos os blobs históricos já removidos. A afirmação “nenhum commit histórico jamais conteve segredo” é **NÃO DETERMINADO PELO CÓDIGO ANALISADO.**

Esses pontos não invalidam o ZIP técnico aprovado e não autorizam rebuild silencioso. Devem ser resolvidos antes de publicação pública.

## Fonte histórica Kotlin

Fonte funcional de referência: `df1701ba5427a04954093e8ebed63f26abb2b2b7` + transformações comprovadas do workflow V8. A branch observada do repositório original continua em `e7b5d8eaac68bce6a9785e4da5b8ca5f83c34d2e` e não foi alterada pelo Passo 22.

## Decisão

**PORTABLE WINDOWS: VALIDADO**

**PUBLICAÇÃO PÚBLICA: BLOQUEADA ATÉ FECHAR LICENÇAS E AUDITORIA HISTÓRICA DE SEGREDOS.**
