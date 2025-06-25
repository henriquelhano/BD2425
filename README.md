# BD-2025 - Projeto de Bases de Dados

## Descrição Geral
Este repositório contém o projeto desenvolvido para a disciplina de Bases de Dados no ano letivo de 2025. O projeto é dividido em duas partes principais:

1. **Parte 1 (E1)**: Modelagem e criação do modelo relacional.
2. **Parte 2 (E2)**: Implementação de uma aplicação baseada em Flask para interagir com uma base de dados PostgreSQL.

## Estrutura do Repositório

- **entrega1/**: Contém o ficheiro relacionado com primeira parte do projeto, incluindo o modelo relacional e o enunciado.
  - `entrega-bd-02-02.pdf`: Documento com o modelo entidade-associação, relacional e álgebra relacional.

- **entrega2/**: Contém os arquivos da segunda parte do projeto.
  - `app/`: Código da aplicação Flask.
    - `app.py`: Código principal da aplicação.
    - `docker-compose.yml`: Configuração para execução com Docker.
    - `Dockerfile`: Configuração do container Docker.
    - `requirements.txt`: Dependências do projeto.
  - `data/`: Scripts SQL para criação e manipulação da base de dados.
    - `aeroporto.csv`: Ficheiro com os aeroportos.
    - `aviao.csv`: Ficheiro com os aviões.
    - `assento.csv`: Ficheiro com os assentos.
    - `voo.csv`: Ficheiro com os voos.
    - `bilhete.csv`: Ficheiro com os bilhetes.
    - `venda.csv`: Ficheiro com as vendas.
    - `populate.sql`: Inserção de dados provenientes dos ficheiros .csv.
  - `aviacao.sql`: Criação das tabelas.
  - `E2-report.ipynb`: Relatório em jupyter Notebook com as consultas.
- **README.md**: Este arquivo.


## Funcionalidades

### Endpoints da API
- `GET /`: Lista todos os aeroportos.
- `GET /voos/<partida>`: Lista voos a partir de um aeroporto específico.
- `GET /voos/<partida>/<chegada>`: Lista voos entre dois aeroportos.
- `POST /compra/<voo>`: Regista a compra de bilhetes para um voo.
- `POST /checkin/<bilhete>`: Regista a o checkin dos bilhetes comprados sem lugar atribuído


### Base de Dados
A base de dados contém as seguintes tabelas principais:
- `aeroporto`: Informações sobre aeroportos.
- `aviao`: Informações sobre aviões.
- `assento`: Assentos disponíveis nos aviões.
- `voo`: Informações sobre voos.
- `venda`: Registro de vendas de bilhetes.
- `bilhete`: Informações sobre bilhetes emitidos.

### Consultas OLAP
O projeto inclui consultas OLAP para análise de dados, como:
- Taxa de ocupação de voos.
- Rotas mais populares.
- Estatísticas de vendas.

