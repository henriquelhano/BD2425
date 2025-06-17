#!/usr/bin/python3
import os
from datetime import datetime, timedelta
from logging.config import dictConfig
from psycopg.rows import namedtuple_row
from psycopg_pool import ConnectionPool
from flask import Flask, json, jsonify, request
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Lisbon") # Timezone for the application

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@postgres/postgres")

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s:%(lineno)s - %(funcName)20s(): %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

def time_now():
    """
    Gera o tempo atual com a timezone definida.
    """
    return datetime.now(TZ)

pool = ConnectionPool(
    conninfo=DATABASE_URL,
    kwargs={
        "autocommit": False, # Use transactions
        "row_factory": namedtuple_row,
    },
    min_size=4,
    max_size=10,
    open=True,
    # check=ConnectionPool.check_connection,
    name="postgres_pool",
    timeout=5,
)

app = Flask(__name__)
app.config.from_prefixed_env()
log = app.logger

@app.route('/', methods=['GET'])
def listarAeroportos():
    """	Lista todos os aeroportos (nome e cidade).""" 
    with pool.connection() as conn:
        with conn.cursor(row_factory=namedtuple_row) as cur:
                try:
                    aeroportos = cur.execute(
                        """
                        SELECT nome, cidade FROM aeroporto ORDER BY nome;
                        """,
                        {},
                    ).fetchall()
                    log.debug(f"Encontrados {cur.rowcount} aeroportos")
                    return jsonify(aeroportos), 200 # O 200 no protocolo HTTP indica que a requisição foi bem sucedida
                except Exception as e:
                    return jsonify({"error": str(e)}), 500 # O 500 no protocolo HTTP indica um erro interno do servidor
        

@app.route('/voos/<partida>', methods=['GET'])
def voos_partida(partida):
    """
    Retorna a lista todos os voos (número de série do avião, hora de partida e aeroporto de chegada) 
    que partem do aeroporto de <partida> até 12h após o momento da consulta.
    """
    """As mensagens de erro estão em inglês porque havia um problema de character encoding"""
    agora = time_now()
    fim = agora + timedelta(hours=12)
    with pool.connection() as conn:
        with conn.cursor(row_factory=namedtuple_row) as cur:
            try:
                # Busca o código do aeroporto pelo nome
                cur.execute(
                    "SELECT codigo FROM aeroporto WHERE nome = %(partida)s;",
                    {"partida": partida},
                )
                # Para evitar SQL Injection, usamos parâmetros nomeados
                aeroporto_ = cur.fetchone()

                if not aeroporto_:
                    return jsonify({"error": f"Airport with name {partida} not found"}), 404
                # O 404 no protocolo HTTP indica que o recurso solicitado não foi encontrado
                codigo_partida = aeroporto_.codigo

                # Agora busca os voos usando o código
                cur.execute(
                    """
                    SELECT no_serie, hora_partida, chegada FROM voo
                    WHERE partida = %s AND hora_partida BETWEEN %s AND %s;
                    """
                    ,
                    (codigo_partida, agora, fim),
                )
                # Para evitar SQL Injection, tratamos os parâmetros como valores literais
                voos = cur.fetchall()
                if not voos:
                    return jsonify({"error": f"No flights found for the airport {partida} in the next 12 hours"}), 404
                return jsonify(voos), 200
            except Exception as e:
                return jsonify({"erro": str(e)}), 500
            

@app.route('/voos/<partida>/<chegada>', methods=['GET'])
def voos_partida_chegada(partida, chegada):
    """Lista os próximos três voos (número de série do avião e hora de partida) 
    entre o aeroporto de <partida> e o aeroporto de <chegada> para os quais ainda há bilhetes disponíveis."""
    """As mensagens de erro estão em inglês porque havia um problema de character encoding"""
    agora = time_now()
    with pool.connection() as conn:
        with conn.cursor(row_factory=namedtuple_row) as cur:
            try:
                # Busca o código do aeroporto de partida
                cur.execute(
                    "SELECT codigo FROM aeroporto WHERE nome = %(partida)s;",
                    {"partida": partida},
                )
                aeroporto_ = cur.fetchone()
                if not aeroporto_:
                    return jsonify({"error": f"Departure Airport {partida} not found"}), 404

                # Busca o código do aeroporto de chegada
                cur.execute(
                    "SELECT codigo FROM aeroporto WHERE nome = %(chegada)s;",
                    {"chegada": chegada},
                )
                aeroporto_chegada = cur.fetchone()
                if not aeroporto_chegada:
                    return jsonify({"error": f"Arrival Airport {chegada} not found"}), 404
                
                #Define os códigos dos aeroportos
                codigo_partida = aeroporto_.codigo
                codigo_chegada = aeroporto_chegada.codigo

                # Busca os voos disponíveis
                cur.execute("""
                     SELECT v.no_serie, v.hora_partida
                     from voo v
                     WHERE v.partida = %s 
                        AND v.chegada = %s 
                        AND v.hora_partida > %s
                        AND EXISTS (
                           SELECT 1
                           FROM assento a
                           WHERE a.no_serie = v.no_serie
                              AND NOT EXISTS (
                                 SELECT 1 FROM bilhete b
                                 WHERE b.voo_id = v.id
                                    AND b.no_serie = a.no_serie
                                    AND b.lugar = a.lugar
                              )  
                        )
                     ORDER BY v.hora_partida ASC
                     LIMIT 3;    
                  """, (codigo_partida, codigo_chegada, agora))
                voos = cur.fetchall()
                
                if not voos:
                    return jsonify({"error": f"There is no flight between {partida} and {chegada} with available tickets"}), 404
                return jsonify(voos), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
   
@app.route('/compra/<voo>', methods=['POST'])
def fazer_compra(voo):
   """
   Regista a compra de bilhetes para um voo específico.
   Recebe no corpo da request um JSON com o NIF do cliente e uma lista de bilhetes.
   """
   data = request.get_json()
   nif_cliente = data.get("nif_cliente")
   bilhetes = data.get("bilhetes")

   if not (nif_cliente and bilhetes):
      return jsonify({"error": "NIF and Tickets are mandatory"}), 400
   
   with pool.connection() as conn:
      with conn.cursor() as cur:
         try:
            no_serie = cur.execute(
               """
               SELECT no_serie 
               FROM voo 
               WHERE id = %s
               """, 
               (voo,)
            ).fetchone()
            
            if not no_serie:
               return jsonify({"error": "Flight not found"}), 404
            no_serie = no_serie[0]

            now = time_now()
            codigo_reserva = cur.execute(
               """
               INSERT INTO venda (nif_cliente, hora)
               VALUES (%s, %s)
               RETURNING codigo_reserva;
               """, 
               (nif_cliente, now)
            ).fetchone()[0]

            return_bilhetes = []
            for b in bilhetes:

                prim_classe = b["classe"] == 1
                preco = 300 if prim_classe else 150
                cur.execute(
                  """
                  INSERT INTO bilhete (voo_id, codigo_reserva, nome_passageiro, preco, prim_classe, no_serie)
                  VALUES (%s, %s, %s, %s, %s, %s)
                  RETURNING id, preco;
                  """, 
                  (voo, codigo_reserva, b["nome"], preco, prim_classe, no_serie)
                )
                bilhete_id, preco = cur.fetchone()
                return_bilhetes.append({
                  "id": bilhete_id,
                  "nome": b["nome"],
                  "classe": b["classe"],
                  "preco": preco
                })
            
                conn.commit()
            
                return jsonify({"message": f"Purchase made for flight {voo}","codigo_reserva:": codigo_reserva, "nif_cliente": nif_cliente,"bilhetes": bilhetes}), 200
         
         except Exception as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 500


@app.route('/checkin/<bilhete>', methods=['POST'])
def check_in(bilhete):
   """
   Realiza o check-in de um bilhete, atribuindo um lugar disponível.
   Retorna o lugar atribuído ou um erro se não houver lugares disponíveis.
   """
   try:
      bilhete_id = int(bilhete)
   except ValueError:
      return jsonify({"error": "Invalid ticket ID, must be an integer"}), 400

   with pool.connection() as conn:
      with conn.cursor() as cur:
         try:
            bilhete_row = cur.execute(
               """
               SELECT b.id, b.voo_id, b.no_serie, b.prim_classe, b.lugar
               FROM bilhete b
               WHERE b.id = %s
               """,
               (bilhete_id,)
            ).fetchone()

            if bilhete_row is None:
               return jsonify({"error": "Ticket not found"}), 404

            if bilhete_row[4] is not None:
               return jsonify({"error": "Check-in already made"}), 409

            voo_id = bilhete_row[1]
            no_serie = bilhete_row[2]
            prim_classe = bilhete_row[3]

            if no_serie is None:
               # Tenta buscar o no_serie do voo e atualizar o bilhete
               no_serie_row = cur.execute(
                  "SELECT no_serie FROM voo WHERE id = %s", (voo_id,)
               ).fetchone()
               if not no_serie_row or not no_serie_row[0]:
                  return jsonify({"error": "Flight not found or without serial number"}), 404
               no_serie = no_serie_row[0]
               cur.execute(
                  "UPDATE bilhete SET no_serie = %s WHERE id = %s",
                  (no_serie, bilhete_id)
               )

            # Procurar um assento disponível da classe correspondente
            assento_livre = cur.execute(
               """
               SELECT a.lugar
               FROM assento a
               WHERE a.no_serie = %s
                  AND a.prim_classe = %s
                  AND NOT EXISTS (
                     SELECT 1 FROM bilhete b
                     WHERE b.no_serie = a.no_serie
                        AND b.lugar = a.lugar
                        AND b.voo_id = %s
                  )
               ORDER BY a.lugar ASC
               LIMIT 1
               """,
               (no_serie, prim_classe, voo_id)
            ).fetchone()

            if assento_livre is None:
               return jsonify({"error": "Não há lugares disponíveis para este bilhete"}), 409

            lugar_atribuido = assento_livre[0]

            # Atualizar o bilhete com o lugar atribuído
            cur.execute(
               """
               UPDATE bilhete
               SET lugar = %s
               WHERE id = %s
               """,
               (lugar_atribuido, bilhete_id)
            )

            conn.commit()
            return jsonify({"lugar_atribuido": lugar_atribuido}), 200

         except Exception as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 500

            
if __name__ == "__main__":
    app.run()