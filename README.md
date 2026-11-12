# OpenIE Theory Revision Artifacts

Artefatos da qualificação de doutorado sobre revisão formal e rastreável de regras linguísticas em Extração de Informação Aberta para o português.

Este repositório documenta o estudo piloto da regra E4 no DptOIE, incluindo reprodução controlada, proveniência operacional, representação em Graph Rewriting e avaliação exploratória de regras candidatas produzidas por operadores explícitos de Theory Revision.

## Resultado central

No caso piloto S009-A41, o DptOIE produziu:

```text
(Catalano, voltou, para a área)
```

O GOLD registra:

```text
(Catalano, voltou para, a área)
```

A proveniência observada mostrou que `para` não foi visitado durante a construção de REL e entrou no argumento por uma operação de intervalo. No modelo formal, a divergência central é:

```text
R_impl observado: ARG1(e,p)
R_gold esperado:  REL(e,p)
```

## Escopo

O material sustenta uma prova de conceito formal e rastreável para E4/S009. Ele não demonstra uma revisão generalizada do DptOIE.

Limitações principais:

- os quatro outputs E− pertencem à mesma sentença S009;
- os quatro controles não são E+ específicos de E4;
- C2 recebe uma classificação provisória de `Rege(v,p)`;
- não existe ainda um reconhecedor independente de regência;
- onze outputs baseline permanecem não modelados;
- a revisão não foi implementada no DptOIE Java.

## Estrutura

```text
docs/                 protocolos, relatórios e dossiê da qualificação
research/             planilhas, formalização, notebooks e exportadores
logs/                 evidências de execução sem modelos ou binários
manifests/            hashes SHA-256 dos artefatos
```

Consulte [docs/README.md](docs/README.md) para localizar os arquivos correspondentes a cada uma das seis etapas metodológicas. A estrutura `research/` e `logs/` foi preservada porque os notebooks e exportadores usam esses caminhos relativos.

## Reprodutibilidade

As instruções e os limites de reprodução estão em [REPRODUCIBILITY.md](REPRODUCIBILITY.md). O repositório não contém o código, o JAR, os modelos linguísticos nem o ambiente Java do DptOIE. Os logs brutos de compilação também não são redistribuídos, pois registravam caminhos absolutos do ambiente local; os relatórios preservam comandos, versões, resultados e hashes dos builds.

O repositório original do extrator é:

- [FORMAS/DptOIE](https://github.com/FORMAS/DptOIE)

## Como citar

Use os metadados de [CITATION.cff](CITATION.cff). Uma versão arquivada com DOI poderá ser criada após a revisão do material da qualificação.

## Proveniência deste pacote

- repositório de pesquisa: `LarrissaSilva/DptOIE-doctoral-research`;
- branch de origem: `modelagem-graph-rewriting-e4`;
- commit consolidado do v4: `7f3fef2`;
- commit-base do DptOIE: `1a5ef708b1ed0a888aac63a7a4512af3cccad315`;
- data de preparação deste pacote: 2026-11-11.

## Direitos e materiais de terceiros

Leia [LICENSE-NOTICE.md](LICENSE-NOTICE.md) e [NOTICE.md](NOTICE.md) antes de reutilizar o conteúdo.
