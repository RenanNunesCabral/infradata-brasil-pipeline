# infradata-brasil-pipeline

Pipeline de engenharia de dados para ingestão, transformação e disponibilização de dados de infraestrutura no Brasil.

## Estrutura do projeto

```
infradata-brasil-pipeline/
├── data/
│   ├── raw/          # Dados brutos, sem transformação
│   ├── bronze/       # Dados ingeridos e persistidos (schema mínimo)
│   ├── silver/       # Dados limpos e padronizados
│   └── gold/         # Dados agregados prontos para consumo
├── src/
│   ├── ingestion/    # Scripts e conectores de ingestão
│   ├── transformations/  # Regras de limpeza e transformação
│   └── utils/        # Funções auxiliares compartilhadas
├── dashboard/        # Visualizações e painéis
├── docs/             # Documentação do projeto
├── tests/            # Testes automatizados
├── requirements.txt
└── README.md
```

## Camadas de dados (medallion)

| Camada  | Descrição |
|---------|-----------|
| **raw** | Arquivos originais das fontes (CSV, JSON, etc.) |
| **bronze** | Dados ingeridos com metadados de ingestão |
| **silver** | Dados validados, deduplicados e tipados |
| **gold** | Métricas e datasets finais para análise |

## Configuração

1. Clone o repositório e entre na pasta do projeto:

   ```bash
   cd infradata-brasil-pipeline
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

## Execução

> Os scripts de ingestão e transformação estão adicionados em `src/`.

## Testes

```bash
pytest tests/
```

## Licença

A definir.

## Dicionário de indicadores

Os indicadores do SINISA são mantidos na camada Gold com seus códigos oficiais,
como `IAG0001`, `IAG0002` e `IAG0003`, para preservar rastreabilidade com a fonte original.

No dashboard, esses códigos são traduzidos para descrições amigáveis utilizando um dicionário de metadados localizado em `src/utils/sinisa_labels.py`.

Exemplo:

| Código | Descrição |
|---|---|
| IAG0001 | Atendimento da população total com rede de abastecimento de água |
| IAG0002 | Atendimento da população urbana com rede de abastecimento de água |
| IAG0003 | Atendimento da população rural com rede de abastecimento de água |