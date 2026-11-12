# Reprodução controlada do caso S009 — E4

## 1. Identificação da execução

**FATO:** Esta execução é identificada metodologicamente como **“Reprodução com o DptOIE.jar distribuído e o modelo de dependências oficialmente disponibilizado atualmente pelo projeto.”**

- Branch: `experimento-proveniencia-e4`
- Commit-base do código original: `1a5ef708b1ed0a888aac63a7a4512af3cccad315`
- Checkpoint metodológico: `2035a7501777886bd66c011affed56f6c14c719c`
- Tipo: `reproduction_current_official_dependency_model`
- Início: `2026-10-16T02:58:15.237Z`
- Término: `2026-10-16T02:58:31.592Z`
- Exit code: `0`
- Número de execuções: **uma única execução**

Nenhum arquivo Java foi alterado, não foi adicionado logging e o sistema não foi recompilado para esta reprodução.

## 2. Ambiente e dependências

### DptOIE.jar

- Arquivo: `DptOIE.jar`, distribuído na raiz do repositório
- SHA-256: `5ff8246cc170537ce7ccb7e1640872564b1534f2ab6c0dbb00ea264468b36d52`

### Java

- Distribuição: Eclipse Temurin
- Versão: `1.8.0_504`
- Executável portátil: `.local-tools/java8/jdk8u504-b01/bin/java.exe`

### Modelos

| Modelo | Origem da cópia experimental | SHA-256 |
|---|---|---|
| `pt-pos-tagger.model` | `pt-models/pt-pos-tagger.model` do repositório | `3025001fb828b7bb73b7f7de6cf6e303126e23aa4f175c8e7f1ad69988a8635b` |
| `pt-dep-parser.gz` | Link oficial de modelos indicado pelo README | `341e6b5bfc2288b8e7991ee746b2517b02dfb2ef7e540b3666f2b969bd4db30d` |

Origem indicada pelo README para os modelos:

`https://drive.google.com/drive/folders/1U7p3o2dvWMN0xecocCcsHh7uPmaW1Zmh?usp=drive_link`

**Limitação de proveniência:** não está comprovado que o `pt-dep-parser.gz` atualmente disponibilizado seja exatamente o mesmo modelo utilizado na execução histórica que produziu S009. Portanto, esta execução não é denominada reprodução histórica exata.

## 3. Entrada e parâmetros

Sentença:

`Catalano voltou para a área depois de viver em Londres e em Glasgow, onde estudou design de jóias na Glasgow School of Art.`

Parâmetros:

- `CC=false`
- `SC=false`
- `appositive=0`

## 4. Resultado da reprodução

Resultado: **REPRODUZIDA EXATAMENTE**.

Extração piloto:

`(Catalano, voltou, para a área)`

No CSV, os campos da extração `1.0` foram registrados como:

- ARG1: `Catalano `
- REL: ` voltou`
- ARG2: `para a área `

## 5. Parse de dependências dos tokens críticos

| ID | FORM | POS | HEAD | DEPREL |
|---:|---|---|---:|---|
| 1 | Catalano | PNOUN | 2 | nsubj |
| 2 | voltou | VERB | 0 | root |
| 3 | para | ADP | 5 | case |
| 4 | a | DET | 5 | det |
| 5 | área | NOUN | 2 | nmod |

## 6. Artefatos e hashes

| Artefato | SHA-256 |
|---|---|
| `s009_sentences.txt` | `765ffcf53b5ef92e10ab5caa78096b81431b03cdebdef55fd8575e0201c5d5f0` |
| `execution_metadata.json` | `cd81c011793eff567e3223754a95d118aedf2361788bd75bca1f089d74c0b533` |
| `stdout.txt` | `e644e28fb3ddcb16558671bc32055cc09231d809942c888772f68e22a632821b` |
| `stderr.txt` | `aea41ac4acf971d1cee802a17191246f4cb63c2d3fc9ca834231c78d63f2661f` |
| `extractedFactsByDpOIE.csv` | `affcad984064af90332666117a04033a545688fd09b5f5466e7704bb614385e9` |
| `output/tokenized_sentences` | `29c87903ebd187d60cd684a62d7d0db0acdd8a2de439b3bb79c59145d3b2c73b` |
| `output/imput_DP.txt` | `b52abc037f84d53f7409b6c6fc38ac6ea08b0fbb028fd58766bcf1681d60425b` |
| `output/output_DP.conll` | `e94d708cef67efaa363a7fdb9e646e4fa39bc3c379e871923bf3631e96e2967f` |

## 7. Observação sobre codificação

O `stdout.txt` preservou caracteres acentuados como `U+FFFD` durante a captura do terminal. O arquivo `extractedFactsByDpOIE.csv` foi produzido em Windows-1252 e preserva os caracteres `área` e `jóias` quando lido com essa codificação. Os outputs produzidos não foram corrigidos nem modificados após a execução.

## 8. Limites desta evidência

Esta reprodução confirma factual e descritivamente o output e o parse registrados acima. **Ainda não foi determinada a causalidade do resultado, não foi atribuído o erro a D02 ou D03 e não foi derivada a representação de \(R_{impl}^{E4}\).** Essas determinações exigem evidências posteriores de execução instrumentada.
