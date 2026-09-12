# Decisões de migração

## DEC-001
ID DA DECISÃO: DEC-001  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-001, MIG-081  
COMPONENTE: Runtime Python  
COMPORTAMENTO ORIGINAL: O build V8 aprovado usa Python 3.12 para empacotar o Editor PySide6.  
DECISÃO: Adotar Python 3.12.x na fundação.  
JUSTIFICATIVA: Preservar a linha de runtime já comprovada no build válido e evitar versão experimental ou posterior sem necessidade.  
EVIDÊNCIA NO KOTLIN: Workflow da release V8 / Build SHA `df1701ba5427a04954093e8ebed63f26abb2b2b7`.  
IMPACTO: `requires-python >=3.12,<3.13`.  
REVERSÍVEL: Sim, mediante nova evidência e testes.  
OBSERVAÇÕES: Nenhuma funcionalidade de negócio depende desta decisão neste passo.

## DEC-002
ID DA DECISÃO: DEC-002  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-068 a MIG-077, MIG-081  
COMPONENTE: Toolkit de UI  
COMPORTAMENTO ORIGINAL: O Editor de Vídeo aprovado já usa PySide6 6.9.1/QtMultimedia.  
DECISÃO: Usar PySide6 6.9.1 como toolkit principal da fundação.  
JUSTIFICATIVA: Não substituir motor/toolkit já validado no artefato aprovado.  
EVIDÊNCIA NO KOTLIN: Workflow/release V8 validam PySide6 6.9.1.  
IMPACTO: Janela mínima Qt e dependência fixada.  
REVERSÍVEL: Sim, somente com avaliação formal.  
OBSERVAÇÕES: Nenhuma tela completa foi migrada.

## DEC-003
ID DA DECISÃO: DEC-003  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-002, MIG-003  
COMPONENTE: Estrutura e caminhos  
COMPORTAMENTO ORIGINAL: O Portable resolve dados e binários relativamente à aplicação, não ao diretório atual do terminal.  
DECISÃO: Centralizar caminhos em `AppPaths` e nunca usar CWD como raiz.  
JUSTIFICATIVA: Preparar desenvolvimento e futuro frozen sem caminhos absolutos.  
EVIDÊNCIA NO KOTLIN: `PortablePaths` e `discoverAppDir` da baseline auditada.  
IMPACTO: Todos os módulos futuros deverão obter caminhos pela camada central.  
REVERSÍVEL: Sim.  
OBSERVAÇÕES: Regras completas de persistência ainda não foram migradas.

## DEC-004
ID DA DECISÃO: DEC-004  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-082  
COMPONENTE: FFmpeg/FFprobe e binários  
COMPORTAMENTO ORIGINAL: O Portable inclui binários específicos no diretório `bin`.  
DECISÃO: Neste passo criar somente resolução de `bin/ffmpeg.exe` e `bin/ffprobe.exe`; não baixar nem substituir executáveis.  
JUSTIFICATIVA: A versão/binário final deve ser determinada pelo passo de migração correspondente, sem download aleatório.  
EVIDÊNCIA NO KOTLIN: Workflow V8 monta os binários no Portable.  
IMPACTO: Dependência permanece pendente.  
REVERSÍVEL: Sim.  
OBSERVAÇÕES: Nenhum processamento de mídia foi implementado.

## DEC-005
ID DA DECISÃO: DEC-005  
DATA: 2026-09-12  
MIG RELACIONADO: MIG-001  
COMPONENTE: Git  
COMPORTAMENTO ORIGINAL: Repositório destino estava vazio, sem commit-base.  
DECISÃO: Criar bootstrap mínimo `.gitkeep` em `main` e realizar todo desenvolvimento da fundação em `migration/python-foundation`.  
JUSTIFICATIVA: Git/GitHub não permitem criar branch a partir de repositório sem commit.  
EVIDÊNCIA NO KOTLIN: Não aplicável; limitação do repositório destino observada antes da modificação.  
IMPACTO: `main` recebe somente commit técnico de inicialização; fundação permanece isolada.  
REVERSÍVEL: Sim.  
OBSERVAÇÕES: Nenhuma alteração foi feita no repositório Kotlin.
