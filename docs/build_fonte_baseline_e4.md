# Build baseline do código-fonte — E4

## Identificação

Este registro corresponde ao **“Build contemporâneo do código-fonte original do DptOIE usando Java 8 e Maven 3.9.16.”**

Não se trata de build histórico exato: a versão histórica do Maven não está registrada, o `pom.xml` não fixa todas as versões dos plugins e os plugins resolvidos atualmente podem diferir dos utilizados originalmente.

- Commit-base: `1a5ef708b1ed0a888aac63a7a4512af3cccad315`
- HEAD compilado: `5ba5a579f9399e5d29bfa718699dba416ea0188d`
- Branch: `experimento-proveniencia-e4`
- Java: Eclipse Temurin `1.8.0_504`
- Maven: `3.9.16`
- Repositório Maven isolado: `.local-tools/maven-repository/`
- Número de compilações: uma
- Exit code: `0`

## Comando

Executado a partir da raiz do repositório, com `JAVA_HOME` e `PATH` definidos somente no processo da compilação:

```text
.local-tools/maven/apache-maven-3.9.16/bin/mvn.cmd -Dmaven.repo.local=<workspace>/.local-tools/maven-repository clean package
```

## Artefatos principais

| Artefato | Tamanho | SHA-256 |
|---|---:|---|
| `target/ExtraiClausulas-1.0-SNAPSHOT.jar` | 57.276 bytes | `268c2de774654b3dc2a520a2d8989ed930c79a6f0215033eed5a1afd0b527fc8` |
| `target/ExtraiClausulas-1.0-SNAPSHOT-jar-with-dependencies.jar` | 24.434.768 bytes | `8cc9e723dd8a563bfaf82b8bb37ba9ee4223220366d18983503b4d2596615e5e` |

Para referência, o `DptOIE.jar` distribuído possui 8.607.253 bytes e SHA-256 `5ff8246cc170537ce7ccb7e1640872564b1534f2ab6c0dbb00ea264468b36d52`.

## Comparação estrutural com o JAR distribuído

- Os tamanhos e os hashes dos três JARs são diferentes.
- `extrai_clausulas/Main.class` e as principais classes do projeto estão presentes nos três JARs.
- O manifesto do `DptOIE.jar` distribuído declara `Main-Class: extrai_clausulas.Main`.
- O JAR contemporâneo com dependências declara `Main-Class: extrai_clausulas.Main`.
- O JAR contemporâneo fino contém `extrai_clausulas/Main.class`, mas não declara `Main-Class` no manifesto.

Essas observações são exclusivamente estruturais. **Ainda não há evidência de equivalência funcional entre o `DptOIE.jar` distribuído e o JAR compilado contemporaneamente.**

## Integridade do código-fonte

As comparações Git realizadas antes e depois do build não apresentaram diferenças em `src/` ou `pom.xml`, tanto entre o commit-base e o HEAD quanto no working tree. Portanto, o código-fonte e o arquivo de build permaneceram inalterados durante esta compilação.

O DptOIE compilado não foi executado nesta etapa.
