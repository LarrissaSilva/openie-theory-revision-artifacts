# Validação de não interferência da instrumentação E4 com trace desabilitado

## Identificação

- Commit instrumentado: `db6af3e90c9a99ad2a61f6f0327e89503aeb63cc`.
- Java: Eclipse Temurin `1.8.0_504`.
- Maven: `3.9.16`.
- JAR instrumentado: `target/ExtraiClausulas-1.0-SNAPSHOT-jar-with-dependencies.jar`.
- SHA-256 do JAR instrumentado: `3c4b9a72dafe03c41045367be437c638eabeb9e71a1bf2edab7ce329c826290d`.

O build do commit instrumentado foi realizado uma única vez. A reprodução do caso S009 também foi realizada uma única vez, com o trace desabilitado e sem a propriedade JVM `dptoie.e4trace`. O build e a execução terminaram com exit code `0`.

## Resultado observado

A execução produziu 7 extrações e incluiu exatamente a extração piloto:

`(Catalano, voltou, para a área)`

O conteúdo funcional do arquivo `extractedFactsByDpOIE.csv` foi byte a byte idêntico ao baseline, com SHA-256 comum `3925c116c3ad9f4dd7d08d459b3e59e534a3ba8944216d14566c8af52d0197b6`.

Os arquivos intermediários também foram byte a byte idênticos ao baseline:

| Arquivo | SHA-256 comum |
| --- | --- |
| `output/tokenized_sentences` | `29c87903ebd187d60cd684a62d7d0db0acdd8a2de439b3bb79c59145d3b2c73b` |
| `output/imput_DP.txt` | `b52abc037f84d53f7409b6c6fc38ac6ea08b0fbb028fd58766bcf1681d60425b` |
| `output/output_DP.conll` | `e94d708cef67efaa363a7fdb9e646e4fa39bc3c379e871923bf3631e96e2967f` |

O parse crítico permaneceu idêntico ao baseline:

| ID | FORM | POS | HEAD | DEPREL |
| ---: | --- | --- | ---: | --- |
| 1 | Catalano | PNOUN | 2 | nsubj |
| 2 | voltou | VERB | 0 | root |
| 3 | para | ADP | 5 | case |
| 4 | a | DET | 5 | det |
| 5 | área | NOUN | 2 | nmod |

Foram encontradas zero linhas com o prefixo `[E4TRACE]` em `stdout` e zero em `stderr`.

As diferenças binárias observadas nos arquivos capturados `stdout.txt` e `stderr.txt` foram atribuídas apenas ao mecanismo de captura e serialização do PowerShell: o `stdout` da execução trace-off foi capturado em UTF-16LE, com caracteres de substituição para texto acentuado do console, e o `stderr` incluiu texto de encapsulamento `NativeCommandError`. Essas diferenças não ocorreram no CSV nem nos arquivos intermediários produzidos pelo DptOIE.

## Classificação

`INSTRUMENTAÇÃO NÃO ALTEROU O COMPORTAMENTO OBSERVADO`

Esta conclusão é limitada ao caso S009 e às condições testadas. Ela não demonstra ausência de interferência para outras sentenças, parâmetros, modelos ou caminhos de execução do DptOIE.
