# Baseline dos controles candidatos de E4

Este documento utiliza as seguintes qualificações:

- **FATO EXPERIMENTAL:** resultado diretamente sustentado pela planilha ou pelos artefatos preservados da execução.
- **EVIDÊNCIA SINTÁTICA:** informação presente no parse produzido pelo pipeline, sem equivaler automaticamente a uma análise linguística correta.
- **HIPÓTESE LINGUÍSTICA:** interpretação preliminar que ainda precisa ser validada com especialistas.
- **NÃO DETERMINADO:** informação que as evidências atuais não permitem estabelecer.

## 1. Objetivo e relação com a preparação de Theory Revision

O objetivo deste experimento foi estabelecer o comportamento baseline do DptOIE em três sentenças reais do OIEC-PT-GOLD que contêm preposições fora da REL produzida pelo sistema. Esses exemplos poderão ser usados posteriormente para verificar se uma revisão de E4 transfere indevidamente preposições de argumentos ou adjuntos para REL.

**FATO EXPERIMENTAL:** nenhuma regra foi revisada, nenhum operador de revisão foi aplicado e nenhuma representação de \(R'_{impl}\) foi criada. O experimento somente reproduziu o comportamento do JAR distribuído original.

Os exemplos são preparatórios para dois tipos de avaliação futura:

1. **controle de não aplicação:** verificar que uma revisão não aplique E4 quando a preposição não for regida pelo verbo da REL;
2. **controle geral de não regressão:** verificar que extrações baseline corretas ou equivalentes ao GOLD permaneçam preservadas.

**NÃO DETERMINADO:** os casos ainda não são controles linguísticos confirmados, pois falta estabelecer formalmente o valor de \(Rege(v,p)\) em cada construção.

## 2. Critérios de seleção de S005, S010 e S003

Os casos foram selecionados da aba `analise` de `research/experimento/semana5_experimento_OIEC_PT_GOLD (3)(1).xlsx`.

Critérios aplicados:

- a planilha classifica a extração correspondente como `E+` do próprio DptOIE;
- a extração contém uma ou mais preposições fora de REL;
- o GOLD preserva essas preposições no argumento;
- a construção é potencialmente útil para detectar sobreaplicação de E4;
- os exemplos pertencem a três sentenças linguisticamente independentes;
- S010-A51 e S010-A52 compartilham a mesma sentença e, por isso, foram reproduzidos em uma única execução.

Casos selecionados:

| Caso | Papel preliminar | Elemento de interesse |
|---|---|---|
| S005-A28 | construção com complemento/conteúdo ou finalidade | `dignidade para continuar...`; `protestar contra...` |
| S010-A51 | construção locativa | `na Universidade de Northampton` |
| S010-A52 | construção locativa e oração de finalidade | `na Universidade... para encontrar...` |
| S003-A20 | complemento de adjetivo em construção copular | `digno de atenção` |

**DECISÃO METODOLÓGICA:** a seleção não pressupõe que `case`, `mark` ou `nmod` provem regência verbal. Essas relações são apenas evidências do parse observado.

## 3. Ambiente experimental

### Repositório e runtime

- Branch: `modelagem-graph-rewriting-e4`.
- Commit: `67a62a72bfa16a98f0a6422bde670bab3a834459`.
- Java: Eclipse Temurin `1.8.0_504`.
- Parâmetros: `CC=false`, `SC=false`, `appositive=0`.
- Trace E4: desabilitado; foram encontradas zero linhas `[E4TRACE]`.

### JAR utilizado

**FATO EXPERIMENTAL:** foi usado o `DptOIE.jar` distribuído original:

| Artefato | Tamanho | SHA-256 |
|---|---:|---|
| `DptOIE.jar` | 8.607.253 bytes | `5ff8246cc170537ce7ccb7e1640872564b1534f2ab6c0dbb00ea264468b36d52` |

O JAR atual em `target/` foi identificado como o build instrumentado, com SHA-256 `3c4b9a72dafe03c41045367be437c638eabeb9e71a1bf2edab7ce329c826290d`, e não foi utilizado.

### Modelos

| Modelo | Tamanho | SHA-256 |
|---|---:|---|
| `pt-pos-tagger.model` | 7.663.538 bytes | `3025001fb828b7bb73b7f7de6cf6e303126e23aa4f175c8e7f1ad69988a8635b` |
| `pt-dep-parser.gz` | 106.097.068 bytes | `341e6b5bfc2288b8e7991ee746b2517b02dfb2ef7e540b3666f2b969bd4db30d` |

As cópias experimentais dos modelos permanecem em `pt-models/` dentro de cada diretório de execução e estão excluídas do Git. Os modelos não são incluídos no checkpoint documental.

## 4. Procedimento de reprodução

Para cada sentença:

1. o texto foi extraído exclusivamente da coluna `sentenca_original` da aba `analise`;
2. o texto foi registrado em um arquivo UTF-8 contendo uma única sentença;
3. foram criados diretórios isolados em `logs/e4/controles_baseline/`;
4. foram usadas cópias dos mesmos modelos validados no experimento S009;
5. o hash do JAR e dos modelos foi verificado antes da execução;
6. foi executado uma única vez o caminho `-sentencesIN`, com `CC=false`, `SC=false` e `appositive=0`;
7. foram preservados `stdout`, `stderr`, CSV e os três arquivos intermediários;
8. os hashes e o exit code foram registrados em `execution_metadata.json`;
9. nenhuma execução foi repetida.

| Sentença | Origem | Início UTC | Término UTC | Exit code |
|---|---|---|---|---:|
| S005 | A28, `sentenca_original` | `2026-10-28T01:18:15.019Z` | `2026-10-28T01:20:00.711Z` | 0 |
| S010 | A51/A52, `sentenca_original` | `2026-10-28T01:21:34.845Z` | `2026-10-28T01:23:07.515Z` | 0 |
| S003 | A20, `sentenca_original` | `2026-10-28T01:24:40.363Z` | `2026-10-28T01:26:15.438Z` | 0 |

O `stderr` das três execuções contém somente o aviso do SLF4J sobre a ausência de provider e a adoção do logger NOP. Não foi observado erro funcional.

## 5. Resultados das 15 extrações

**FATO EXPERIMENTAL:** as três execuções produziram 15 extrações. Após normalizar somente os espaços de preenchimento dos campos do CSV, todas coincidem, na mesma ordem, com as extrações do DptOIE registradas na planilha.

### S005 — quatro extrações

Sentença original:

> O mundo pode estar enfurecido e absurdo - no entanto pelo menos alguém tem dignidade para continuar a protestar contra esse fato.

| Ordinal | Linha da análise | Extração reproduzida | Classificação na planilha |
|---:|---|---|---|
| 1 | A26 | `(O mundo, pode estar, enfurecido - e absurdo en o entanto)` | E− |
| 2 | A27 | `(alguém, tem, dignidade)` | E+ |
| 3 | A28 | `(alguém, tem, dignidade para continuar a protestar contra esse fato)` | E+ |
| 4 | A29 | `(alguém, tem, dignidade por o menos)` | E+ |

A26 mantém a divergência E3 registrada na planilha. A29 envolve a expressão `por o menos` e pode interagir com E9; por isso, não é o primeiro controle recomendado para E4.

### S010 — seis extrações

Sentença original:

> Eu visitei os espetáculos universitários na Universidade de Northampton para encontrar novos talentos, diz ele.

| Ordinal | Linha da análise | Extração reproduzida | Classificação na planilha |
|---:|---|---|---|
| 1 | A50 | `(Eu, visitei, os espetáculos universitários)` | E+ |
| 2 | A51 | `(Eu, visitei, os espetáculos universitários en a Universidade de Northampton)` | E+ |
| 3 | A52 | `(Eu, visitei, os espetáculos universitários en a Universidade de Northampton para encontrar novos talentos)` | E+ |
| 4 | A53 | `(Eu, visitei, os espetáculos universitários en a Universidade de Northampton para encontrar novos talentos , diz)` | E− |
| 5 | A54 | `(Eu, visitei, os espetáculos universitários para encontrar novos talentos)` | E− |
| 6 | A55 | `(Eu, visitei, os espetáculos universitários , diz)` | E− |

A53–A55 reproduzem as divergências E3/S3 documentadas na planilha.

### S003 — cinco extrações

Sentença original:

> Um avanço rápido para 2016 e isso é cada vez mais digno de atenção.

| Ordinal | Linha da análise | Extração reproduzida | Classificação na planilha |
|---:|---|---|---|
| 1 | A16 | `(Um avanço, rápido, para 2016)` | E− |
| 2 | A17 | `(Um avanço, rápido, para 2016 e isso é cada vez mais digno de atenção)` | E− |
| 3 | A18 | `(Um avanço, rápido, e isso é cada vez mais digno de atenção)` | E− |
| 4 | A19 | `(isso, é cada vez, mais digno de atenção)` | E− |
| 5 | A20 | `(isso, é, cada vez mais digno de atenção)` | E+ |

A16–A18 mantêm a divergência E1. A19 mantém as divergências E9/E3 registradas. A20 é a extração candidata a controle.

### Integridade dos artefatos

Todos os arquivos listados nos três `execution_metadata.json` existem e possuem exatamente os tamanhos e hashes registrados. As entradas coincidem com a planilha, os modelos coincidem com os hashes validados e os CSVs reproduzem as linhas históricas na mesma ordem.

#### S005

| Arquivo | SHA-256 |
|---|---|
| `execution_metadata.json` | `1edef79e05132abcfa272e9d7f8aa91c727c2adaa9128c915f288eeccf4f1318` |
| `s005_sentences.txt` | `c37e36f51a45cb2e37a10ebece791be2d407abb6eebe456c78904feb3d30c5ad` |
| `stdout.txt` | `fbd67b6779a8ed6606becf15733e6894115cef6d5306271d32b3bf9b4954d9ba` |
| `stderr.txt` | `6717f012d12e354d2433bdc32bbc80f87b5ca364f0bb6b6f2be5504bc469d132` |
| `extractedFactsByDpOIE.csv` | `b7463406760fb182ea262cd02e037249e7732cc1252920f73e466df67e726b93` |
| `output/tokenized_sentences` | `b367c75e61bad3ff7db08e4607837b673907631013864b8db1907e6ea9a2acd2` |
| `output/imput_DP.txt` | `745fa03fe9ef00822403e3b9878b0b5562c57db95521eb042d6e13af4eb73d75` |
| `output/output_DP.conll` | `49335c1eb391b21f55b6c44a956bfbfcc15ae968e75eb511f364e8a16a20ec2d` |

#### S010

| Arquivo | SHA-256 |
|---|---|
| `execution_metadata.json` | `a1555d4061927cf6299d8ccfa58c47b727befd435f4e193a3e095e71e2dab068` |
| `s010_sentences.txt` | `1cb8ffe5a81ef84ed228bc9fbe649a72086b74b3faa4c5647120878cfa341845` |
| `stdout.txt` | `977986e946b7f29805a27487900bb44b8360b6a84b088277f4690907e4804883` |
| `stderr.txt` | `6717f012d12e354d2433bdc32bbc80f87b5ca364f0bb6b6f2be5504bc469d132` |
| `extractedFactsByDpOIE.csv` | `21f4e1f047e1d9fa4cc4ff05049201e93e2b944c6deab8fff9551069a35e3736` |
| `output/tokenized_sentences` | `7c1e88661775d297a26fac6158a2a9c5e664fd16768522cfd029faffd4a73619` |
| `output/imput_DP.txt` | `6c5e0f9ff89271c16b92f5f4601cf94a960a3ee939f62247078eb6f21788e1c8` |
| `output/output_DP.conll` | `c3aaab2679596c96ca24e51896134ef572d7f963946c0af5c16ae50c4f4e5cfe` |

#### S003

| Arquivo | SHA-256 |
|---|---|
| `execution_metadata.json` | `3ca7385186808026774b3e46183524d86ce8d0793fcec0b2250b3a72e7030273` |
| `s003_sentences.txt` | `faccd1e5fa47dda019f648aa8bcdd17434856631920aa73a058eeb3171f7aea7` |
| `stdout.txt` | `c32d78c44e54eb6efce0b329a07d0423ee70fa85420099837eaa738825aae1be` |
| `stderr.txt` | `6717f012d12e354d2433bdc32bbc80f87b5ca364f0bb6b6f2be5504bc469d132` |
| `extractedFactsByDpOIE.csv` | `2a9b038f21ee709d591480e9e026d530468ae6c8ab74e23164829debc5ad8851` |
| `output/tokenized_sentences` | `223041d2e5bc226f9c7a0b000712322943c37bf0f24141e2dd5ed1ee37931474` |
| `output/imput_DP.txt` | `f6f30f2f70f3b8ec23bb263d21a31272949d0c91bfd28f4ec88f5833c010732f` |
| `output/output_DP.conll` | `f12731b7b6dc71ffda49d837f947f8eb76119751a4062585c8e564e3d0cb624c` |

## 6. Comparação dos quatro candidatos com o GOLD

Na nomenclatura do código/CSV, o sujeito é chamado `ARG1` e o segundo argumento é chamado `ARG2`. Para manter a convenção científica desta pesquisa, a tabela abaixo usa `ARG0`, `REL` e `ARG1`.

| Caso | ARG0 baseline/GOLD | REL baseline/GOLD | ARG1 baseline | ARG1 GOLD | Resultado |
|---|---|---|---|---|---|
| S005-A28 | `alguém` / `alguém` | `tem` / `tem` | `dignidade para continuar a protestar contra esse fato` | igual | Correspondência textual exata dos três componentes |
| S010-A51 | `Eu` / `Eu` | `visitei` / `visitei` | `os espetáculos universitários en a Universidade de Northampton` | `os espetáculos universitários em a Universidade de Northampton` | Mesmas fronteiras; diferença superficial `en a`/`em a` |
| S010-A52 | `Eu` / `Eu` | `visitei` / `visitei` | `os espetáculos universitários en a Universidade de Northampton para encontrar novos talentos` | forma correspondente com `em a` | Mesmas fronteiras; diferença superficial `en a`/`em a` |
| S003-A20 | `isso` / `isso` | `é` / `é` | `cada vez mais digno de atenção` | igual | Correspondência textual exata dos três componentes |

**FATO EXPERIMENTAL:** nos quatro candidatos, as preposições de interesse permaneceram no argumento e não foram incorporadas a REL.

Esse fato, isoladamente, não demonstra que a extração seja linguisticamente um controle válido de E4. Também não demonstra que o DptOIE tenha tomado uma decisão baseada em regência verbal.

## 7. Correspondência textual e equivalência das fronteiras

Foram usadas três noções distintas:

1. **correspondência textual exata:** ARG0, REL e ARG1 possuem os mesmos textos no baseline e no GOLD, após remover somente espaços periféricos de serialização;
2. **equivalência das fronteiras:** os mesmos constituintes pertencem a ARG0, REL e ARG1, embora exista uma diferença superficial dentro de um componente;
3. **divergência funcional:** algum elemento muda de componente, falta, sobra ou altera a proposição extraída.

Aplicação aos candidatos:

- S005-A28: correspondência textual exata;
- S003-A20: correspondência textual exata;
- S010-A51/A52: equivalência das fronteiras, sem correspondência textual exata devido a `en a`/`em a`.

A forma `en` aparece no arquivo tokenizado e no parse, e não somente no CSV. Portanto, não é uma diferença causada exclusivamente pelo encoding ou pela serialização do CSV. O CSV foi produzido em Windows-1252; quando lido nessa codificação, os caracteres acentuados são preservados.

## 8. Evidências sintáticas e hipóteses linguísticas

### S005-A28

**EVIDÊNCIA SINTÁTICA:**

- `para`: `head=continuar`, `deprel=mark`;
- `continuar`: `head=tem`, `deprel=nmod`;
- `contra`: `head=fato`, `deprel=case`;
- `fato`: `head=protestar`, `deprel=nmod`.

**HIPÓTESE LINGUÍSTICA:** `para continuar a protestar...` expressa conteúdo ou finalidade na construção `ter dignidade`; `contra esse fato` está associado ao predicado encaixado `protestar`, e não à REL principal `tem`.

**NÃO DETERMINADO:** \(Rege(tem,para)\). A hipótese preliminar é que seja falso, mas isso ainda requer validação linguística.

### S010-A51/A52

**EVIDÊNCIA SINTÁTICA:**

- `en`: `head=Universidade`, `deprel=case`;
- `Universidade`: `head=visitei`, `deprel=nmod`;
- `para`: `head=encontrar`, `deprel=mark`;
- `encontrar`: `head=visitei`, `deprel=nmod`.

**HIPÓTESE LINGUÍSTICA:** `na Universidade de Northampton` funciona como localização do evento, e `para encontrar novos talentos` como oração de finalidade. Nenhuma das duas preposições seria regida por `visitar` no sentido exigido por E4.

**NÃO DETERMINADO:** \(Rege(visitei,em)\) e \(Rege(visitei,para)\). As hipóteses preliminares são negativas, mas precisam ser validadas.

### S003-A20

**EVIDÊNCIA SINTÁTICA:**

- o parser classificou `rápido` como `VERB` e raiz;
- `é` recebeu `deprel=cop`;
- `digno` recebeu `deprel=amod`;
- `de`: `head=atenção`, `deprel=case`;
- `atenção`: `head=digno`, `deprel=nmod`.

**HIPÓTESE LINGUÍSTICA:** `de atenção` completa o adjetivo `digno`, e não o verbo copular `ser`.

**NÃO DETERMINADO:** \(Rege(é,de)\). A hipótese preliminar é negativa. A análise global do parser para S003 contém decisões discutíveis, especialmente a classificação de `rápido`, e não deve ser adotada como análise linguística final.

## 9. Limitações

- Não há E+ E4 confirmado do próprio DptOIE no conjunto experimental atual.
- Os quatro exemplos continuam sendo candidatos; a condição linguística \(Rege(v,p)\) ainda não foi validada por especialistas.
- `case`, `mark` e `nmod` não são tratados como prova de regência verbal.
- S010-A51 e A52 pertencem à mesma sentença e não constituem evidências linguisticamente independentes.
- A diferença `en a`/`em a` impede classificar A51/A52 como correspondência textual exata, embora as fronteiras sejam equivalentes.
- S003 possui um parse global discutível, que limita o uso direto de suas dependências como fundamento linguístico.
- S005 contém um predicado encaixado (`protestar contra`), o que exige distinguir a regência do verbo principal da regência interna de outro predicado.
- O experimento comprova reprodução do baseline e preserva os dados necessários para uma comparação posterior; não valida uma revisão de E4.

## 10. Critérios para uso posterior na avaliação de não regressão

Antes de promover um candidato a controle de não aplicação, devem ser satisfeitos todos os critérios seguintes:

1. identificar inequivocamente o verbo correspondente à REL avaliada;
2. identificar a preposição e a expressão à qual ela pertence;
3. obter validação linguística explícita de que \(Rege(v,p)\) é falso para o verbo da REL;
4. distinguir preposição de argumento, adjunto ou predicado encaixado;
5. conservar a sentença, o GOLD e o output baseline registrados neste experimento;
6. definir a equivalência esperada: textual exata ou equivalência de fronteiras;
7. após uma futura revisão, executar sob o mesmo Java, modelos e parâmetros;
8. exigir que a preposição permaneça no componente esperado;
9. exigir que ARG0, REL e ARG1 não adquiram perdas, sobras ou mudanças de escopo;
10. comparar todas as extrações da sentença, e não apenas a extração candidata;
11. verificar que a quantidade de extrações não seja alterada indevidamente;
12. tratar separadamente divergências de E3, E9 e S3, sem atribuí-las a E4.

Papel futuro preliminar:

| Caso | Controle de não aplicação | Controle geral de não regressão | Estado atual |
|---|---|---|---|
| S005-A28 | candidato | sim | aguarda validação de `Rege(tem,para)` |
| S010-A51 | candidato | sim, por equivalência de fronteiras | aguarda validação do locativo |
| S010-A52 | candidato de estresse | sim, por equivalência de fronteiras | aguarda validação da finalidade |
| S003-A20 | candidato | sim | aguarda validação de `digno de` e revisão linguística do parse |

Uma avaliação de não regressão de E4 somente poderá ser considerada completa depois de combinar esses controles validados com E− independentes e com E+ E4 confirmados do próprio DptOIE.
