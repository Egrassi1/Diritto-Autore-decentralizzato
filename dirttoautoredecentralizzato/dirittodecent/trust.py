from difflib import SequenceMatcher
import traceback
from dirittoautore.var import trustitems, semtrust
from dirittodecent.models import Testo

# thread che si occupa di gestire la comparazione dei testi
def trust():
   while True:
    try:
        semtrust.acquire()
        trust = True
        t = trustitems.pop()
        tfile = open(t.file.name, encoding="utf8")
        tdata = tfile.read()
        print("inizio comparazione: " + t.id)
        comparelist = Testo.objects.filter().exclude(id =t.id)
        for c in comparelist:
            cfile =open(c.file.name)
            cdata= cfile.read()
            rateo=  SequenceMatcher(None, tdata,cdata).ratio() * 100
            if (rateo >25):
                trust = False
        t.trust = trust
        t.save()
        print("fine comparazione: "+ t.id + " il trust è "+ str(trust))
    except: 
       print("si è verificato un errore nell'analisi del trust")
       traceback.print_exc()
        


