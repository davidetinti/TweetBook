# TweetBook

Andrea Ricciardelli, Davide Tinti, Matteo Feroli, Manuel Vannini, Stefano Sgarzi

# Guida all'utilizzo del server SSH e Git
Accedere al server con:
```bash
ssh unibo@128.116.169.110
Password: [pass]
cd sito/TweetBook
```

Il server è già configurato per l'utilizzo con Git nella cartella corrente:
```bash
git pull origin 'master'
git push origin 'master'
```

Per un utilizzo appropriato, evitare di utilizzare il comando push dal server.

A meno che capitino particolari imprevisti, il server Web remoto sarà sempre attivo.
Dopo aver effettuato un Pull, o aver cambiato dei file nel l'unico comando necessario per poter applicare gli aggiornamenti è:
```bash
./runserver.sh
```

Il sito web sarà disponibile all'indirizzo http://128.116.169.110/

# Guida alla compilazione su server locale
Per prima cosa, assicurarsi di avere un'istanza Git di questa repo in una cartella del proprio PC:
```bash
git init 
git remote add origin http://aminsep.disi.unibo.it/gitlab/Daveeeed/tweetbook.git
git fetch --all
git checkout 'master'
git pull origin 'master'
```

Quindi installare Docker: https://www.docker.com/get-started

Per avviare il server, nonché per ricaricarlo quando vengono effettuati cambiamenti al codice, avviare lo script
```bash
./runserver.sh
```
La prima volta impiegherà svariato tempo per tutte le installazioni necessarie. le volte sucessive dovrebbe prendere al massimo 6-7 secondi.

Il sito web sarà disponibile all'indirizzo http://localhost:8000/