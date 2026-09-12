# Arquitetura da migração Python

## Fonte da verdade

A migração usa `tysudess/noticias-monitor`, Build SHA `df1701ba5427a04954093e8ebed63f26abb2b2b7`, **mais as transformações executadas por** `.github/workflows/release-v8-extractor-tab-portable.yml`. O destino é `tysudess/MONITOR-DE-NOTICAS-PYTHON`, branch `migration/python-foundation`.

A regra permanente é preservar o motor e o comportamento comprovados. Quando algo não é comprovado: **NÃO DETERMINADO PELO CÓDIGO ANALISADO**.

## Arquitetura atual após o Passo 10

```text
Application
└─ MainWindow (PySide6 QMainWindow)
   ├─ páginas do Monitor migradas no Passo 9
   ├─ Editor de PDF [placeholder]
   ├─ Extrator de Vídeos [ExtractorPage REAL]
   └─ Editor de Vídeo [placeholder]

ExtractorPage (PySide6)
   ├─ Download
   │  ├─ URL
   │  ├─ 5 presets de qualidade
   │  ├─ BAIXAR VÍDEO / CANCELAR / Abrir Vídeos
   │  ├─ progresso/status
   │  └─ QThread → ExtractorEngine
   ├─ Histórico
   │  └─ ExtractorPortableStateStore
   └─ Configurações
      ├─ GloboplaySessionStore (DPAPI CurrentUser)
      ├─ launcher do GloboplayLoginHelper.exe, quando empacotado
      └─ YtDlpUpdater

ExtractorEngine
   ├─ yt-dlp.exe (nightly no pacote da release)
   ├─ yt-dlp-stable.exe (Globoplay)
   ├─ ffmpeg.exe
   ├─ ffprobe.exe
   ├─ deno.exe
   ├─ YouTube normal
   ├─ YouTube Live: snapshot HLS congelado + fallback temporal limitado
   ├─ Globoplay: URL → globo:ID → HLS → HTML m3u8
   ├─ R7/Record: página → candidatos HTML
   └─ Genérico: yt-dlp → candidatos HTML/mídia direta

Windows
   ├─ HiddenProcessRunner: subprocessos ocultos + kill da árvore
   └─ DpapiTextStore: sessão Globoplay protegida
```

## Fronteira UI x motor

A UI não contém parsing de sites nem monta comandos de mídia. `ExtractorPage` coleta URL/qualidade, cria um worker em `QThread`, encaminha progresso e aciona cancelamento. A montagem de comandos, roteamento por fonte, retry, HLS, FFprobe, FFmpeg, cookies e erros pertence a `monitor_noticias.extractor`.

O cancelamento preserva dois níveis da release: a UI incrementa um token de operação para ignorar callbacks antigos e o engine encerra a árvore do processo ativo por `HiddenProcessRunner.destroy_tree()`.

## Motor real do Extrator

A release não usa um downloader Python inventado. O motor comprovado é uma composição de:

- `yt-dlp.exe`;
- `yt-dlp-stable.exe`;
- `ffmpeg.exe`;
- `ffprobe.exe`;
- `deno.exe`;
- fallbacks HTML próprios;
- snapshot HLS próprio para YouTube Live;
- cookies Globoplay protegidos por DPAPI;
- helper Chromium/PySide6 para login Globoplay;
- updater seguro de yt-dlp.

As versões exatas de yt-dlp e Deno são **NÃO DETERMINADO PELO CÓDIGO ANALISADO**, porque o workflow baixa `latest` no momento do build. O workflow tenta FFmpeg BtbN `ffmpeg-n9.0-latest-win64-gpl-9.0.zip` e usa Gyan `ffmpeg-release-essentials.zip` como fallback; qual fonte concreta venceu no artefato final é **NÃO DETERMINADO PELO CÓDIGO ANALISADO** sem inspecionar o binário/log do build.

## Qualidades

O contrato contém exatamente cinco presets:

| Label | Limite | Selector primário | Compat |
|---|---:|---|---|
| 360p | 360 | `bv*[height<=360][ext=mp4]+ba[ext=m4a]/b[height<=360][ext=mp4]/bv*[height<=360]+ba/b[height<=360]/b` | `b[height<=360][ext=mp4]/b[height<=360]/b` |
| 480p | 480 | `bv*[height<=480][ext=mp4]+ba[ext=m4a]/b[height<=480][ext=mp4]/bv*[height<=480]+ba/b[height<=480]/b` | `b[height<=480][ext=mp4]/b[height<=480]/b` |
| 720p HD | 720 | `bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[height<=720][ext=mp4]/bv*[height<=720]+ba/b[height<=720]/b` | `b[height<=720][ext=mp4]/b[height<=720]/b` |
| 1080p Full HD | 1080 | `bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080][ext=mp4]/bv*[height<=1080]+ba/b[height<=1080]/b` | `b[height<=1080][ext=mp4]/b[height<=1080]/b` |
| Melhor disponível | sem limite | `bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b` | `b[ext=mp4]/b` |

Índice padrão: `1` = `480p`.

## Comando yt-dlp base

O engine preserva:

`--no-playlist --newline --progress --windows-filenames --trim-filenames 180 --continue --retries 10 --fragment-retries 10 --retry-sleep http:linear=1::3 --retry-sleep fragment:linear=1::3 --socket-timeout 30 --ffmpeg-location <bin> -f <selector> --merge-output-format mp4 --remux-video mp4 -o "Videos/%(title).150B [%(id)s].%(ext)s" --print "after_move:FINAL_FILE:%(filepath)s"`.

Se Deno existe, adiciona `--js-runtimes deno:<path>`. Cookies/referer/proxy só são acrescentados quando o fluxo os fornece.

## Retry de compatibilidade

A segunda tentativa usa `quality.compat` somente quando o erro primário contém `403`, `forbidden`, `requested format`, `format is not available`, `qualidade escolhida não está disponível` ou `player response`. Erros de autenticação não disparam esse retry.

## YouTube normal e Live

O probe usa `--ignore-config --no-playlist --dump-single-json --skip-download --socket-timeout 30`. Após o patch da release, `post_live` **não** é live ativa; somente `is_live=true` ou `live_status=is_live` usa o fluxo de live.

### Snapshot HLS

O fluxo principal de live:

1. repete o probe com timeout 25 e `--ffmpeg-location`;
2. determina o ponto final no instante do clique;
3. escolhe variante HLS muxada com áudio+vídeo, preferindo não ultrapassar a altura desejada;
4. lê a playlist, resolve URLs relativas e valida a janela DVR;
5. acrescenta `#EXT-X-ENDLIST` para congelar a janela;
6. tenta FFmpeg `-c copy`;
7. se necessário, transcodifica para H.264/AAC (`libx264`, `veryfast`, CRF 20, `yuv420p`, AAC 160k, `+faststart`).

Fallback temporal yt-dlp: `--live-from-start --hls-use-mpegts --download-sections *00:00:00-HH:MM:SS --force-keyframes-at-cuts --concurrent-fragments 4`. Se o início não puder ser determinado com segurança, o download é interrompido para não acompanhar a transmissão indefinidamente.

## H.264 / FFprobe

Após YouTube normal/live, FFprobe consulta `v:0`/`codec_name`. `h264` e `avc1` são mantidos. Outros codecs passam pela conversão H.264/AAC da baseline. Falha na conversão preserva o arquivo original.

## Globoplay

Usa `yt-dlp-stable.exe` quando disponível. Ordem final:

1. URL original;
2. `globo:<id>` quando ID é detectado;
3. URL original com `--hls-use-mpegts --downloader m3u8:native`;
4. até 15 candidatos `.m3u8` extraídos do HTML.

Base Globoplay: `--force-ipv4 --ignore-config --no-mtime`. O runtime cookie vem de `data/extractor/globoplay.session.dpapi`, DPAPI CurrentUser, e é materializado temporariamente apenas durante a operação.

O login interno depende de `data/extractor/runtime/GloboplayLoginHelper.exe` (>20 MB), com `--output` e `--profile-dir`. O Passo 10 implementa o launcher, mas o helper binário pertence à montagem da release/portable e não é criado neste passo; por isso o login real permanece bloqueado até o passo de empacotamento.

## R7/Record

Base `--force-ipv4 --no-mtime`. Primeiro tenta a página; depois busca até 15 candidatos `.m3u8/.mp4/.m4v/.webm`. Um erro da página principal não é tratado como diagnóstico final de DRM antes de testar os candidatos.

## Genérico

URL direta `.m3u8/.mp4/.m4v/.webm/.mov` vai direto ao engine. Caso contrário, tenta yt-dlp e depois até 15 candidatos HTML. O parser normaliza `\u0026`, `\/` e `&amp;`, usa User-Agent/Referer comprovados e exclui URLs de tracking/analytics/pixel.

## Proxy do Extrator

O engine mantém parâmetro de proxy porque os fallbacks e comandos originais o suportam. Entretanto, a transformação final da release remove a UI própria de proxy e chama `engine.download(..., "")` e `GloboplayLoginWindow(..., "")`. Portanto o Passo 10 **não liga automaticamente o proxy geral do Monitor ao Extrator**. Fazer isso agora alteraria a release aprovada.

## Persistência

`data/extractor/settings.properties` guarda `qualityIndex`; `history.txt` guarda até 50 caminhos distintos, mais recente primeiro; `globoplay.session.dpapi` guarda cookies protegidos por DPAPI CurrentUser. A pasta de saída é `Videos/`.

## Atualizador yt-dlp

Baixa o stable oficial para `yt-dlp.update.tmp.exe`, exige >1 MB, valida `--version`, move a instalação anterior para `yt-dlp.backup.exe`, instala/substitui, valida novamente e só então apaga o backup. Em falha, tenta restaurar o anterior e preserva backup quando necessário. Timeouts: conexão 30 s, leitura 60 s, validação 30 s. User-Agent: `MonitorDeNoticias-Extractor/3.0.1`.

## Testes do Passo 10

Foram adicionados testes de:

- cinco presets e seletores;
- classificação das fontes e normalização R7;
- mídia direta e filtros HTML;
- estado portable/histórico;
- comando yt-dlp e progresso;
- retry restrito a falhas compatíveis;
- contrato FFprobe/H.264;
- cancelamento da árvore de processo;
- contrato visual do `ExtractorPage`;
- equivalência explícita de rotas e qualidade.

A matriz Windows/Ubuntu executa `compileall` e toda a regressão com Qt offscreen. O run do Passo 10 passou nos dois ambientes. Isso não substitui teste de download real com os cinco binários/helper da distribuição final.

## Pendências deliberadas após o Passo 10

- teste real de YouTube normal/live com binários da release;
- teste real de R7/Record e Globoplay;
- helper Globoplay empacotado;
- confirmação das versões concretas dos binários presentes no ZIP da release;
- portable final;
- Editor PDF completo;
- Editor de Vídeo completo.

Os demais componentes e pendências dos Passos 1–9 permanecem válidos e não foram alterados pelo Passo 10.
