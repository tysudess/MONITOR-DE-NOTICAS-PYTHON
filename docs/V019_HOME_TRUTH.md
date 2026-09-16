# v0.0.19 — Home imagem-verdade e sidebar global

Esta versão altera somente a camada visual da Home/shell.

- A referência visual 1672x941 fornecida pelo usuário é a fonte de verdade.
- O ativo visual é armazenado em 14 fragmentos Base64, remontado byte a byte e validado por tamanho e SHA-256 antes de ser exibido ou publicado.
- A sidebar é fixa em 225 px e mantém a mesma estrutura/estilo em todas as abas.
- As 15 rotas funcionais existentes permanecem registradas, inclusive Extrator de Notícias e Automação Planilhas.
- Controller, banco, coletores, matching, automações, proxy, credenciais, ferramentas e integrações não são substituídos.
- A release exige regressão, captura Windows 1672x941, build do portable e smoke do ZIP recém-gerado.
