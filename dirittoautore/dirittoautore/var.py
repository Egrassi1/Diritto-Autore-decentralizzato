from web3 import Web3, AsyncWeb3
from threading import *  


auth = dict()   # dictionary per gestire le richieste di login degli utenti
trustitems = [] # stack di Testi per cui determinare il livello di ttrust
semtrust = Semaphore(0) # semaforo per gestire il thread che si occupa del trust , inizializzato a 0
truster = None # riferimento al thread , viene inizializzato al primo upload di un testo
web3 = None
addressTesto = "" 
addressLicenza = ""
contrattoLicenza = None
contrattoTesto = None



