# Progetto SDCC - Tipologia B2
Progetto per il corso di Sistemi Distribuiti e Cloud Computing, laurea magistrale in Ingegneria Informatica dell' Università di Roma Tor Vergata

Per poter utilizzare l'applicazione, sviluppata in un contesto UNIX (più precisamente MacOS) è necessario aver installato sul proprio pc:
- python3
- Docker
- AWS CLI
- libreia boto3 python
- ulteriori librerie specificate nella relazione

## Installazione
Per installare l'applicazione è consigliabile eseguire il clone di questa repository all'interno di una cartella di lavoro locale

## Configurazione e avvio
E' possibile configurare, all'interno del file config.json (nella directory GUI), le porte locali da utilizzare.
E' inoltre necessario modificare le credenziali AWS all'interno del file config.json e all'interno del file aws/credentials. Tuttavia, per fare ciò è necessario avere un laboratorio "Learner Lab" AWS attivo e recuperare i relativi token e chiavi di sicurezza, validi per 4 ore.

Per avviare l'applicazione, è necessario prima far partire lo script 'Start_server.sh'
Successivamente, si può avviare lo script 'Start_Gui.sh'

## Spegnimento
Per chiudere l'applicazione, si puo semplicemente chiudere la finestra GUI: in questo modo verranno rimossi anche i container utilizzati.
Per chiudere il server, è possibile eseguire lo script 'Shutdown_server.sh'.
