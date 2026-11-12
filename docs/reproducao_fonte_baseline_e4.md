# Reprodução baseline do S009 com o JAR compilado

## Identificação da execução

Esta execução é identificada como **“Reprodução baseline do S009 com o JAR compilado a partir do código-fonte não modificado do DptOIE.”**

- Commit-base: `1a5ef708b1ed0a888aac63a7a4512af3cccad315`
- HEAD executado: `82977595a4908543948daf03fa436fec57cd8793`
- Checkpoint do build: `82977595a4908543948daf03fa436fec57cd8793`
- JAR: `target/ExtraiClausulas-1.0-SNAPSHOT-jar-with-dependencies.jar`
- SHA-256 do JAR: `8cc9e723dd8a563bfaf82b8bb37ba9ee4223220366d18983503b4d2596615e5e`
- Java: Eclipse Temurin `1.8.0_504`
- Número de execuções: uma
- Exit code: `0`

O código-fonte não foi alterado, não foi adicionado logging e não houve nova compilação nesta etapa.

## Modelos e parâmetros

| Modelo | SHA-256 |
|---|---|
| `pt-pos-tagger.model` | `3025001fb828b7bb73b7f7de6cf6e303126e23aa4f175c8e7f1ad69988a8635b` |
| `pt-dep-parser.gz` | `341e6b5bfc2288b8e7991ee746b2517b02dfb2ef7e540b3666f2b969bd4db30d` |

Parâmetros:

- `CC=false`
- `SC=false`
- `appositive=0`

## Resultado do caso S009

A reprodução com o JAR distribuído e a reprodução com o JAR compilado terminaram com exit code `0` e produziram **7 extrações** cada.

A extração piloto está presente exatamente nas duas execuções:

`(Catalano, voltou, para a área)`

## Parse crítico

O parse dos tokens críticos é idêntico nas duas execuções:

| ID | FORM | POS | HEAD | DEPREL |
|---:|---|---|---:|---|
| 1 | Catalano | PNOUN | 2 | nsubj |
| 2 | voltou | VERB | 0 | root |
| 3 | para | ADP | 5 | case |
| 4 | a | DET | 5 | det |
| 5 | área | NOUN | 2 | nmod |

O arquivo `output/output_DP.conll` é byte a byte idêntico nas duas reproduções, com SHA-256:

`e94d708cef67efaa363a7fdb9e646e4fa39bc3c379e871923bf3631e96e2967f`

## Comparação dos CSVs

Os CSVs não são binariamente iguais:

- JAR distribuído: `affcad984064af90332666117a04033a545688fd09b5f5466e7704bb614385e9`
- JAR compilado: `3925c116c3ad9f4dd7d08d459b3e59e534a3ba8944216d14566c8af52d0197b6`

A comparação linha a linha mostrou que todas as sete linhas de dados são textualmente idênticas. A diferença está restrita à representação de caracteres acentuados no cabeçalho do CSV do JAR compilado, que contém formas como `SENTENÃ‡A`. Os valores de ARG1, REL e ARG2 não diferem entre as duas reproduções.

## Classificação e limite

Classificação: **COMPORTAMENTO EQUIVALENTE PARA O CASO PILOTO**.

Essa classificação vale exclusivamente para S009 nas condições registradas. **Ela não demonstra equivalência funcional geral entre o `DptOIE.jar` distribuído e o JAR compilado a partir do código-fonte.**

Os arquivos em `src/` e o `pom.xml` permaneceram inalterados durante a reprodução.
