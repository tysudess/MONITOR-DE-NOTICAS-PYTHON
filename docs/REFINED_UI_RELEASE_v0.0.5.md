# Release v0.0.5 — refinamento visual global

Validação pré-merge do refinamento visual das telas do Monitor de Notícias.

## Escopo

- somente camada de interface PySide6 e infraestrutura de validação/release;
- motor de notícias, vídeos, demandas, banco, matching, proxy, automação, PDF, extrator, FFmpeg e FFprobe preservados;
- tela Início mantida como referência visual principal;
- demais telas alinhadas à mesma identidade azul-marinho/ciano/dourado.

## Gate executado

- Windows GitHub Actions;
- compilação Python aprovada;
- suíte completa `pytest -q` aprovada;
- 10 telas capturadas em 1721 x 914 com backend Qt nativo do Windows;
- artefato visual do run 34890892267 gerado com sucesso.

## Telas cobertas

Início, Notícias, Vídeos, Demandas, Fontes, Histórico, Termos, Configurações, Editor de PDF e Extrator de Vídeos.

## Portable

A publicação v0.0.5 executa nova build portable a partir do commit publicado, reaproveitando somente os binários FFmpeg/FFprobe previamente auditados byte a byte e validando novamente o ZIP e o smoke do executável antes de criar a GitHub Release.
