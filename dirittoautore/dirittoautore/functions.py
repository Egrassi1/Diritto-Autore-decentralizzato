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
    t = Testo(hash,f,None)

    # se il thread non è stato inizializzato , viene costruito e avviato
    if var.truster == None:
        var.truster = threading.Thread(target=trust)
        var.truster.start()
    filename, ext = os.path.splitext(t.file.name)
    print(ext)
     # se il testo  ha un formato valido , viene inserito nella coda per il controllo
     # altrimenti viene automaticamente segnalato come falso 
    if ext == ".txt":
       t.save() 
       var.trustitems.append(t)
       var.semtrust.release() # signal sul semaforo del thread
    else: 
        t.trust = False
        t.save()

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


