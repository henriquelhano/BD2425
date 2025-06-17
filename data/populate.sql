--Os atibutos das tabelas no CSV devem ser os mesmos da tabela aviao em no aviacao.sql

-- Populates the aeroporto table
\copy aeroporto FROM 'aeroporto.csv' DELIMITER ',' CSV HEADER

-- Populates the aviao table
\copy aviao FROM 'aviao.csv' DELIMITER ',' CSV HEADER

-- Populates the assento table
\copy assento FROM 'assento.csv' DELIMITER ',' CSV HEADER

-- Populates the voo table
\copy voo FROM 'voo.csv' DELIMITER ',' CSV HEADER

-- Populates the venda table
\copy venda FROM 'venda.csv' DELIMITER ',' CSV HEADER;

-- Corrige a sequência após importação
SELECT setval('venda_codigo_reserva_seq', (SELECT MAX(codigo_reserva) FROM venda));


-- Populates the bilhete table
\copy bilhete FROM 'bilhete.csv' DELIMITER ',' CSV HEADER;

-- Corrige a sequência da tabela bilhete
SELECT setval('bilhete_id_seq', (SELECT MAX(id) FROM bilhete));
