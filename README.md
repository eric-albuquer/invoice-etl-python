# Invoice ETL Python

Automação para processar **Invoices** (faturas) do setor financeiro, extraindo dados de PDFs, armazenando localmente em `database.json` e disponibilizando análises de forma eficiente.  

Baseado no dataset público **[Company Documents Dataset](https://www.kaggle.com/datasets/ayoubcherguelaine/company-documents-dataset)**.

---

## ⚡ Features

- **Ingestão de PDFs**: Extrai `Order ID`, `Date`, `Customer ID` e tabela de itens (`Produto`, `Quantidade`, `Preço Unitário`).
- **Armazenamento**: Salva dados em `database.json` com verificação de duplicidade (mesmo `Order ID` não é salvo duas vezes).
- **Validação**: Utiliza **Pydantic** para garantir integridade dos dados.
- **Analytics**: Consultas via **Pandas**:
  - Média do valor total das faturas.
  - Produto mais comprado.
  - Total gasto por produto.
  - Listagem de produtos com nome e preço unitário.
- **Dashboard Gráfico**: Utiliza **matplotlib.pyplot** (biblioteca nativa amplamente utilizada para gráficos em Python) para exibir análises de forma intuitiva, como::
  - Top 10 produtos por total gasto.
  - Distribuição de preços unitários.
  - Top clientes por faturamento.
  - Número de faturas por mês.
- **Processamento Paralelo**: Pode processar múltiplos PDFs simultaneamente usando **multiprocessing** para acelerar a ingestão.
- **Registro de Log (Logging)**: Todas as execuções do pipeline são registradas em `ingestion.log`, incluindo:
  - Início e fim da execução
  - Processamento de arquivos com sucesso e erros
  - Tempo total de execução
  - PID dos processos para ingestão paralela

---

## 🗂 Estrutura do Projeto

```text
invoice-etl-python/
│
├─ main.py # Script principal, suporta ingestão sequencial ou paralela + analytics
├─ invoices/ # Pasta onde os PDFs devem estar
├─ ingestion.log # Armazena os registros de erro e execução
├─ database.json # Criado automaticamente após ingestão
└─ invoice_etl/
    ├─ download_dataset.py # Baixa os PDFs do Kaggle caso a pasta "invoices" não exista
    ├─ extractor.py # Extração de dados dos PDFs
    ├─ repository.py # Armazena as invoices em JSON, com validação Pydantic
    ├─ analytics.py # Consulta e análise dos dados
    ├─ dashboard.py # Visualização gráfica das análises
    ├─ models.py # Modelos Pydantic: Invoice e Item
```

---

## ⚙️ Requisitos

Antes de rodar o projeto, certifique-se de que:
- Python está instalado (testado com 3.12.0 e 3.12.1, pode funcionar em outras versões 3.10+).
- No Windows, a execução de scripts está habilitada (PowerShell ExecutionPolicy configurado para permitir scripts).

## ⚙️ Instalação

1. Clone o repositório:

```bash
git clone https://github.com/eric-albuquer/invoice-etl-python.git
cd invoice-etl-python

python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

pip install -r requirements.txt

python main.py
```

O script irá detectar se a pasta invoices/ existe. Caso não, o download_dataset.py será executado automaticamente.

## 🚀 Uso

### 1. Ingestão Sequencial + Analytics (padrão)
Este modo processa todos os PDFs sequencialmente e gera as análises no console.

```bash
python main.py
```

### 2. Ingestão Paralela + Analytics
Este modo utiliza múltiplos processos para acelerar a ingestão de PDFs grandes.

```bash
python main.py --parallel
```

### 3. Dashboard Gráfico
Para visualizar o dashboard com gráficos das análises, use a flag --dashboard junto da execução:

```bash
python main.py --dashboard
```

Você pode combinar flags, por exemplo:

```bash
python main.py --parallel --dashboard
```

Isso processa os PDFs em paralelo e, ao final, exibe o dashboard gráfico.

## ✅ Regras Importantes

- Não comitar `database.json` no repositório.
- Bibliotecas obrigatórias: `pydantic`, `pandas`, `pdfplumber` ou `pypdf`.
- Adicionalmente, usei `matplotlib.pyplot` apenas para visualização de dados no dashboard.
- Sistema evita duplicidade de `Order ID`.
- Código estruturado em **OO**, separando responsabilidades de ingestão e análise.

## 💡 Observações

- PDFs seguem padrão do dataset público; qualquer PDF do dataset pode ser usado para testes.
- Validação de dados via Pydantic garante integridade antes de salvar.
- A ingestão paralela é útil para grandes volumes de PDFs, reduzindo significativamente o tempo de processamento.

## 🌟 Próximos passos

- Criar dashboard visual interativo com Plotly/Dash para análises em tempo real.
- Adicionar suporte a mais formatos de arquivo (CSV, XLSX).


![Python](https://img.shields.io/badge/python-3.13-blue)
![License](https://img.shields.io/badge/license-MIT-green)