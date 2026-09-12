# Arquitetura inicial

## Escopo do Passo 3

Esta arquitetura contém apenas a fundação. Os módulos de negócio são placeholders e não implementam comportamento do Kotlin.

## Fluxo de entrada

`run.py` → `monitor_noticias.app.application.Application` → `QApplication` → `monitor_noticias.ui.main_window.MainWindow`.

## Módulos

- `app`: bootstrap, resolução central de caminhos, logging, configuração vazia e exceções globais.
- `ui`: janela mínima PySide6. **Placeholder funcional de UI**, não reprodução das telas Kotlin.
- `models`: **placeholder**.
- `database`: **placeholder**; nenhum schema ou migration foi criado.
- `repositories`: **placeholder**.
- `collectors/news`: **placeholder**.
- `collectors/video`: **placeholder**.
- `matching`: **placeholder**.
- `automation`: **placeholder**.
- `networking`: **placeholder**.
- `windows`: **placeholder**.
- `video`: **placeholder**.
- `pdf`: **placeholder**.
- `extraction`: **placeholder**.
- `utils`: **placeholder**.
- `resources`: recursos distribuíveis futuros.
- `bin`: binários portáteis aprovados futuramente. O projeto não baixa executáveis automaticamente.
- `data`: dados runtime; nenhum banco real é criado.
- `logs`: logs runtime.
- `temp`: temporários runtime.
- `tests/unit`: infraestrutura determinística.
- `tests/integration`: integração de fundação.
- `tests/equivalence`: paridade futura Kotlin × Python por MIG.

## Caminhos

`AppPaths` centraliza a raiz e deriva `resources`, `data`, `bin`, `logs`, `temp`, `ffmpeg.exe` e `ffprobe.exe`. Em desenvolvimento a raiz é derivada da localização do módulo; em execução frozen, do diretório do executável. O diretório atual do terminal não é fonte da verdade.

## Dependências atuais

Apenas PySide6 e pytest foram adicionados. Bibliotecas de scraping, PDF, download, banco extras e integrações Windows não foram antecipadas.
