# BD2425 - Database Project

## General Description
This repository contains the project developed for the **Databases** course in the **2024–2025 academic year**.  
The project is divided into two main parts:

1. **Part 1 (E1)**: Modeling and creation of the relational model.  
2. **Part 2 (E2)**: Implementation of a Flask-based application to interact with a PostgreSQL database.


## Repository Structure

- **entrega1/**  
  Contains the files related to the first part of the project, including the relational model and the assignment.  
  - `entrega-bd-01-02.pdf`: Document with the entity–relationship model, relational model, and relational algebra.

- **entrega2/**  
  Contains the files related to the second part of the project.  
  - `app/`: Flask application source code.  
    - `app.py`: Main application file.  
    - `docker-compose.yml`: Docker Compose configuration file.  
    - `Dockerfile`: Docker container configuration.  
    - `requirements.txt`: Project dependencies.  
  - `data/`: SQL scripts for database creation and manipulation.  
    - `aeroporto.csv`: Airports data.  
    - `aviao.csv`: Aircraft data.  
    - `assento.csv`: Seat data.  
    - `voo.csv`: Flight data.  
    - `bilhete.csv`: Ticket data.  
    - `venda.csv`: Sales data.  
    - `populate.sql`: Inserts data from the CSV files.  
    - `aviacao.sql`: Creates database tables.  
  - `E2-report.ipynb`: Jupyter Notebook report with queries and analysis.

- **README.md**  
  This file.

## Features

### API Endpoints

- `GET /` — Lists all airports.  
- `GET /voos/<partida>` — Lists flights departing from a specific airport.  
- `GET /voos/<partida>/<chegada>` — Lists flights between two airports.  
- `POST /compra/<voo>` — Registers the purchase of tickets for a given flight.  
- `POST /checkin/<bilhete>` — Registers check-in for purchased tickets without an assigned seat.


## Database Schema

The database includes the following main tables:

- **aeroporto** — Airport information.  
- **aviao** — Aircraft information.  
- **assento** — Seat information.  
- **voo** — Flight information.  
- **venda** — Ticket sale records.  
- **bilhete** — Issued ticket information.


## OLAP Queries

The project includes OLAP queries for data analysis, such as:

- Flight occupancy rate.  
- Most popular routes.  
- Sales statistics.


## Final Grade

- **E1**: 11.7 / 20.0  
- **E2**: 17.3 / 20.0  
- **Final Grade**: **14.5 / 20.0**


## Authors
Developed as part of the **Databases** course (BD2425) at **Instituto Superior Técnico**.  
