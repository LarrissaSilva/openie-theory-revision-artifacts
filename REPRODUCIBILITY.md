# Reprodutibilidade

## Níveis de reprodução

Este pacote diferencia três níveis:

1. reprodução das extrações do DptOIE;
2. reprodução da análise de Graph Rewriting;
3. reprodução da Theory Revision v4 e das matrizes de rastreabilidade.

## DptOIE

As execuções registradas utilizaram:

- Eclipse Temurin Java `1.8.0_504`;
- `CC=false`;
- `SC=false`;
- `appositive=0`;
- `pt-pos-tagger.model`, SHA-256 `3025001fb828b7bb73b7f7de6cf6e303126e23aa4f175c8e7f1ad69988a8635b`;
- `pt-dep-parser.gz`, SHA-256 `341e6b5bfc2288b8e7991ee746b2517b02dfb2ef7e540b3666f2b969bd4db30d`.

O `DptOIE.jar` distribuído possuía SHA-256 `5ff8246cc170537ce7ccb7e1640872564b1534f2ab6c0dbb00ea264468b36d52`.

O código, o JAR e os modelos devem ser obtidos de suas fontes originais. Os artefatos em `evidence/` preservam entradas, metadados, parses, saídas e traces, mas não incluem essas dependências.

## Notebooks

O experimento v4 foi executado com:

- Python `3.12.0`;
- NetworkX `3.5`;
- openpyxl `3.1.5`;
- nbclient `0.11.0`.

Instalação sugerida:

```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Execute os notebooks na ordem:

```text
research/graph_rewriting/experimento_v2_e4_impl_gold.ipynb
research/graph_rewriting/experimento_v3_e4_theory_revision.ipynb
research/graph_rewriting/experimento_v4_e4_theory_revision.ipynb
```

O v2 representa `R_impl` e `R_gold`; o v3 registra a experiência exploratória auditada; o v4 materializa regras imutáveis e operadores explícitos.

Os exportadores preservam referências aos commits metodológicos do repositório privado de pesquisa. As planilhas publicadas são os artefatos congelados usados na qualificação. A regeneração integral requer que os commits de referência estejam disponíveis ou que a verificação de história seja adaptada explicitamente, sem alterar os hashes congelados das entradas.

## Integridade

Os hashes dos arquivos publicados estão em `manifests/SHA256SUMS.txt`. A planilha e o notebook v4 também registram hashes congelados das entradas utilizadas na avaliação.

## Limite

Reproduzir o notebook v4 demonstra os resultados do modelo formal. Não equivale a executar uma versão revisada do DptOIE Java.
