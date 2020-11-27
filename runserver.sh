#!/bin/bash
# Elimino l'istanza precedente per consentire il coretto ricaricamento
docker-compose down
echo "Server chiuso. Riavvio in corso."
# Ricreo il contenitore
docker-compose build
echo "Server costruito."
# Avvio il server
docker-compose up &
sleep 5
echo "Server avviato."
# Riprendo il processo in background
docker-compose restart
echo "Server in funzione in background."
# Apro una connessione websocket per fare streaming dei tweet (sulla porta 5000)
./TweetBook/streamsearch.py 5000