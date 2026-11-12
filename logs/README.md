# Logs experimentais

Os logs preservam as execuções usadas na qualificação.

## `s009/`

- reprodução com o JAR distribuído;
- reprodução do fonte não modificado;
- execução trace-off;
- execução trace-on e `e4trace.txt`.

## `e4/controles_baseline/`

Execuções de S003, S005 e S010 com o JAR distribuído original.

As cópias de `pt-pos-tagger.model` e `pt-dep-parser.gz` foram deliberadamente excluídas. Seus hashes permanecem nos metadados.

Os logs brutos dos dois builds foram omitidos do pacote público porque registram caminhos absolutos do ambiente local. Os resultados e hashes dos builds permanecem documentados em `docs/build_fonte_baseline_e4.md` e `docs/validacao_instrumentacao_trace_off_e4.md`.
