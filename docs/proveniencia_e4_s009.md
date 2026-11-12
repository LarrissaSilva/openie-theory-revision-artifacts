# Proveniência observada da E4 no caso piloto S009

## Identificação da execução

- Commit da instrumentação utilizada: `db6af3e90c9a99ad2a61f6f0327e89503aeb63cc`.
- HEAD do repositório durante a execução: `3da8e3a19df753760c3a9eecb3ef9150e5f5edd3`.
- JAR: `target/ExtraiClausulas-1.0-SNAPSHOT-jar-with-dependencies.jar`.
- SHA-256 do JAR instrumentado: `3c4b9a72dafe03c41045367be437c638eabeb9e71a1bf2edab7ce329c826290d`.
- Trace habilitado exclusivamente por `-Ddptoie.e4trace=true`.
- Número de execuções: 1.
- Exit code: `0`.
- Eventos `[E4TRACE]`: 133, com sequência monotônica e contínua de `seq=1` a `seq=133`.
- Extração piloto observada: `(Catalano, voltou, para a área)`.

## Validação funcional

Todos os outputs funcionais da execução trace-on são byte a byte idênticos aos correspondentes da execução trace-off:

| Artefato | SHA-256 comum |
| --- | --- |
| `extractedFactsByDpOIE.csv` | `3925c116c3ad9f4dd7d08d459b3e59e534a3ba8944216d14566c8af52d0197b6` |
| `output/tokenized_sentences` | `29c87903ebd187d60cd684a62d7d0db0acdd8a2de439b3bb79c59145d3b2c73b` |
| `output/imput_DP.txt` | `b52abc037f84d53f7409b6c6fc38ac6ea08b0fbb028fd58766bcf1681d60425b` |
| `output/output_DP.conll` | `e94d708cef67efaa363a7fdb9e646e4fa39bc3c379e871923bf3631e96e2967f` |

As duas execuções terminaram com exit code `0`, produziram 7 extrações e contêm exatamente a extração piloto. Nenhuma diferença funcional foi observada nas condições testadas.

## Parse crítico observado

| ID | FORM | POS | HEAD | DEPREL |
| ---: | --- | --- | ---: | --- |
| 1 | Catalano | PNOUN | 2 | nsubj |
| 2 | voltou | VERB | 0 | root |
| 3 | para | ADP | 5 | case |
| 4 | a | DET | 5 | det |
| 5 | área | NOUN | 2 | nmod |

## Cadeia de proveniência observada

1. Em `seq=1`, `Catalano`, token 1, foi selecionado como sujeito por `Extracao1.buscaSujeito`, com `head=2`, `deprel=nsubj` e `moduleId=1`.
2. Em `seq=2`, `voltou`, token 2, foi inicializado como núcleo de REL por `Extracao1.buscaRelacao`, com `moduleId=1`.
3. Em `seq=13`, a reavaliação registrou `relationCoreBefore=2` e `relationCoreAfter=2`; portanto, o núcleo permaneceu no token 2.
4. Em `seq=14`, `REL_FINAL_AFTER_BUILD` registrou somente `tokenIds=[2]`, `tokenForms=["voltou"]`, `relationCoreId=2` e `moduleId=1`.
5. A travessia observada da construção de REL ocorreu entre `seq=3` e `seq=12`. Os eventos `REL_CANDIDATE_EXAMINED` registraram apenas os tokens 1, 5, 8 e 26. Não houve evento desse tipo para `para`, token 3; portanto, ele não foi visitado nessa travessia.
6. Em `seq=16`, `área`, token 5, foi examinada por `Extracao1.extraiClausulas` como filha do núcleo token 2, com `head=2` e `deprel=nmod`.
7. Em `seq=17`, `ARG_CONCAT_BEGIN` registrou o início da concatenação do argumento a partir de `área`, token 5.
8. Em `seq=18`, `para`, token 3, filho de `área`, foi examinado com `head=5`, `deprel=case` e `intervalAvailable=true`. Em `seq=19`, esse token acionou a operação registrada por `ARG_INTERVAL_TRIGGERED`, com `intervalStart=3` e `intervalEnd=5`.
9. A mesma operação de intervalo adicionou o token 3, `para`, em `seq=20`; o token 4, `a`, em `seq=21`; e o token 5, `área`, em `seq=22`.
10. Em `seq=24`, `ARG_CONCAT_END` registrou o argumento com `tokenIds=[3,4,5]` e `tokenForms=["para","a","área"]`. Em `seq=25`, `ARGUMENT_STARTED` preservou esse mesmo conteúdo, com `moduleId=1`.
11. Em `seq=26`, o argumento `[3,4,5]` foi adicionado como ARG2 por `SujeitoRelacaoArgumentos.addArg2`, com `argumentIdentity=827966648`, `moduleId=1` e texto interno `"para a área "`.
12. Em `seq=127`, `FINAL_EXTRACTION_BEFORE_CSV` registrou a extração ordinal 1 com sujeito `"Catalano "`, REL `" voltou"`, ARG2 `"para a área "` e `argumentIdentity=827966648`. A identidade é a mesma registrada no evento `ARG2_ADDED`, comprovando que o mesmo objeto de argumento apareceu na extração final `(Catalano, voltou, para a área)`.

## O QUE O TRACE NÃO DEMONSTRA

- Não demonstra uma regra geral para todo o DptOIE.
- Não demonstra que todo token com `deprel=case` seja enviado a ARG2.
- Não demonstra que `case` seja a condição operacional responsável pela inclusão do token.
- Não demonstra ainda uma representação generalizada de \(R_{impl}^{E4}\).
- Não demonstra correção ou revisão da regra.

## IMPLICAÇÃO PARA A MODELAGEM

O comportamento observado deverá ser representado posteriormente em Graph Rewriting no mesmo framework utilizado para \(R_{gold}^{E4}\). Essa representação deverá preservar a distinção entre:

- propriedades linguísticas observadas no parse: `nmod`, `case` e `det`;
- condições efetivamente utilizadas pelo código, que deverão ser sustentadas pelas avaliações e operações registradas no trace, sem serem substituídas antecipadamente pelos rótulos linguísticos;
- operações produzidas nesta execução: `REL=[2]`, intervalo `[3,5]` e `ARG2=[3,4,5]`.

Este documento registra somente o comportamento comprovado para a extração piloto do S009 nas condições desta execução instrumentada.
