# InfraData Brasil Pipeline

Pipeline de engenharia de dados para ingestão, tratamento, padronização e disponibilização de dados públicos de infraestrutura no Brasil.

O projeto utiliza dados do **SINISA** e do **IBGE** para construir uma arquitetura em camadas no padrão **Medallion Architecture**:

```text
Raw → Bronze → Silver → Gold → Dashboard
```

O objetivo é transformar arquivos públicos, muitas vezes pouco padronizados, em uma base analítica organizada e pronta para consumo em dashboards, análises e futuras integrações com ferramentas como DuckDB, dbt, Airflow e Databricks.

---

## Objetivo do projeto

Este projeto foi desenvolvido como um estudo prático de **Engenharia de Dados**, com foco em:

- ingestão de dados públicos;
- tratamento de arquivos Excel complexos;
- padronização de colunas;
- persistência em formato Parquet;
- separação em camadas Raw, Bronze, Silver e Gold;
- integração entre bases usando código IBGE;
- criação de dashboard analítico em Streamlit;
- documentação de pipeline de dados para portfólio.

---

## Fontes de dados

### SINISA

Utilizado para indicadores de abastecimento de água dos municípios brasileiros.

A planilha do SINISA possui cabeçalhos institucionais antes da tabela real. Por isso, o pipeline possui uma lógica para identificar automaticamente a linha correta de cabeçalho, onde aparecem colunas como:

```text
cod_IBGE, Município, UF, CAD0002, IAG0001, IAG0002...
```

### IBGE

Utilizado para obter a base territorial oficial dos municípios, estados e regiões.

A integração entre SINISA e IBGE é feita por meio do código do município:

```text
codigo_ibge
```

---

## Arquitetura do projeto

```text
infradata-brasil-pipeline/
│
├── data/
│   ├── raw/             # Arquivos originais das fontes
│   ├── bronze/          # Dados ingeridos e convertidos para Parquet
│   ├── silver/          # Dados limpos, padronizados e tratados
│   └── gold/            # Dados analíticos prontos para consumo
│
├── src/
│   ├── ingestion/       # Scripts de ingestão
│   ├── transformations/ # Transformações entre camadas
│   └── utils/           # Funções auxiliares
│
├── dashboard/           # Dashboard em Streamlit
├── docs/                # Documentação e imagens
├── tests/               # Testes automatizados
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## Camadas de dados

| Camada | Descrição |
|---|---|
| Raw | Arquivos originais baixados das fontes públicas, sem transformação |
| Bronze | Dados ingeridos e salvos em Parquet, com metadados de ingestão |
| Silver | Dados limpos, padronizados, deduplicados e preparados para análise |
| Gold | Base analítica final, integrada e pronta para dashboard |

---

## Pipeline desenvolvido

O fluxo atual do projeto é:

```text
1. Baixar/armazenar planilha do SINISA em data/raw/sinisa
2. Ingerir dados do IBGE
3. Ingerir dados do SINISA
4. Salvar dados brutos em Parquet na camada Bronze
5. Transformar Bronze em Silver
6. Criar tabela Gold integrando SINISA + IBGE
7. Disponibilizar os dados em dashboard Streamlit
```

---

## Tabela Gold

A principal tabela analítica gerada atualmente é:

```text
data/gold/infra_municipios_agua.parquet
```

Ela combina dados territoriais do IBGE com indicadores de abastecimento de água do SINISA.

Essa tabela permite analisar:

- atendimento total de água por município;
- atendimento urbano;
- atendimento rural;
- indicadores por UF;
- prestadores de serviço;
- natureza jurídica dos prestadores;
- distribuição dos indicadores por município.

---

## Dashboard

O projeto possui um dashboard em Streamlit localizado em:

```text
dashboard/app.py
```

O dashboard permite:

- filtrar dados por UF;
- selecionar indicadores do SINISA;
- visualizar métricas gerais;
- consultar ranking de municípios;
- comparar médias por UF;
- analisar natureza jurídica dos prestadores;
- baixar a base filtrada em CSV.

### Exemplo de visualização

Adicione aqui um print do dashboard:

```markdown
![Dashboard - Visão Geral](docs/images/dashboard_visao_geral.png)
```

---

## Dicionário de indicadores

Os indicadores do SINISA são mantidos na camada Gold com seus códigos oficiais, como:

```text
IAG0001
IAG0002
IAG0003
```

Essa decisão preserva a rastreabilidade com a fonte original.

No dashboard, esses códigos são traduzidos para descrições amigáveis utilizando o arquivo:

```text
src/utils/sinisa_labels.py
```

Exemplo:

| Código | Descrição |
|---|---|
| IAG0001 | Atendimento da população total com rede de abastecimento de água |
| IAG0002 | Atendimento da população urbana com rede de abastecimento de água |
| IAG0003 | Atendimento da população rural com rede de abastecimento de água |

---

## Tecnologias utilizadas

- Python
- Pandas
- PyArrow
- Parquet
- Streamlit
- Git/GitHub
- Arquitetura Medallion
- Dados públicos do SINISA e IBGE

---

## Como executar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/RenanNunesCabral/infradata-brasil-pipeline.git
cd infradata-brasil-pipeline
```

### 2. Criar ambiente virtual

```bash
python -m venv .venv
```

### 3. Ativar ambiente virtual

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 4. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## Como rodar o pipeline

### 1. Ingestão do IBGE

```bash
python -m src.ingestion.ibge_localidades
```

### 2. Ingestão do SINISA

Antes de rodar este passo, coloque a planilha do SINISA na pasta:

```text
data/raw/sinisa/
```

Depois execute:

```bash
python -m src.ingestion.sinisa
```

### 3. Transformação Bronze para Silver

```bash
python -m src.transformations.bronze_to_silver
```

### 4. Criação da camada Gold

```bash
python -m src.transformations.build_gold
```

### 5. Executar o dashboard

```bash
python -m streamlit run dashboard/app.py
```

---

## Testes

Para executar os testes automatizados:

```bash
pytest tests/
```

---

## Aprendizados do projeto

Durante o desenvolvimento deste projeto, foram trabalhados conceitos importantes de engenharia de dados:

- leitura de arquivos públicos não padronizados;
- detecção automática de cabeçalho real em planilhas Excel;
- padronização de nomes de colunas;
- tratamento de tipos mistos para gravação em Parquet;
- organização de dados em camadas;
- integração entre fontes usando chave oficial;
- criação de base Gold para consumo analítico;
- construção de dashboard com dados tratados.

---

## Próximas evoluções

Algumas melhorias planejadas:

- adicionar dados da ANEEL;
- adicionar dados do PNCP;
- incluir DuckDB para consultas SQL;
- criar testes de qualidade de dados;
- adicionar Docker;
- adicionar dbt para modelagem analítica;
- adicionar Airflow para orquestração;
- publicar o dashboard online;
- criar documentação com diagrama de arquitetura.

---

## Status do projeto

MVP funcional concluído.

O projeto já possui ingestão, transformação, camada Gold e dashboard inicial.

---

## Autor

Renan Nunes Cabral

Projeto desenvolvido para portfólio em Engenharia de Dados, Dados Públicos e Automação.
