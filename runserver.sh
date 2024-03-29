#!/bin/bash
# Elimino l'istanza precedente per consentire il coretto ricaricamento
docker-compose down
echo "Server chiuso. Riavvio in corso."
# Ricreo il contenitore
docker-compose build
echo "Server costruito."
# Avvio il server
docker-compose up &
sleep 45
echo "Server avviato."
# Riprendo il processo in background
docker-compose restart
echo "Server in funzione in background."
