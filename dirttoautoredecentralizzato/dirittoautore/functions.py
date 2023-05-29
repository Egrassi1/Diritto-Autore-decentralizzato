import os
import string
from dirittoautore.settings import STATIC_URL
from dirittodecent.models import Testo
import hashlib
import random
import dirittoautore.var as var
import threading
from dirittodecent.trust import trust




def handle_uploaded_file(f):  
    # viene calcolato analogamente al front-end l'hash del file appena caricato

        bytes = f.read() 
        hash = hashlib.md5(bytes).hexdigest()
        print(hash)
        
        # viene effettuato un doppio controllo sulla transazione
        #event_signature_hash = var.web3.keccak(text="Deposito(address,string,string,uint256)").hex()
        event_filter = var.contrattoTesto.events.Deposito.create_filter(fromBlock = 0, argument_filters = {"token_id": hash})
        event_logs = event_filter.get_all_entries()
        try:
            e = event_logs[0]
            print(event_logs[0]['args'])
            tx_hash = e['transactionHash']
            valori = event_logs[0]['args'] 
            #si da' per assunto che esista un solo evento in quanto l'id è univoco
            token_id = valori["token_id"]

            if(token_id == hash):         
                t = Testo(hash,f,None,valori['titolo'],str(valori['sender']),int(valori['data']))
                # se il thread non è stato inizializzato , viene costruito e avviato
                if var.truster == None:
                    var.truster = threading.Thread(target=trust)
                    var.truster.start()
                filename, ext = os.path.splitext(t.file.name)
                # se il testo  ha un formato valido , viene inserito nella coda per il controllo
                # altrimenti viene automaticamente segnalato come falso 
                if ext == ".txt":
                    t.save() 
                    var.trustitems.append(t)
                    var.semtrust.release() # signal sul semaforo del thread
                else: 
                        t.trust = False
                        t.save()
        except: print("transazione non riconosciuta")

# questa funzione controlla la corrispondenza tra il testo di una query effettuata dall'utente e i dati recuperati dalla blockchain
def match(query,data):
    Arquery = [char for char in query]
    Ardata =  [char for char in data]
    for i in range(0, len(Arquery)):
        if (len(Ardata) < i or Arquery[i] != Ardata[i]):
            return False
    return True

# genera il token casuale per il login
def gettoken():
    id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for i in range(16))
    return id


