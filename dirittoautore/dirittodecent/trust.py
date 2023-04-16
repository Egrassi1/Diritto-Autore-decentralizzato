from difflib import SequenceMatcher
from dirittoautore.var import trustitems, semtrust
from dirittodecent.models import Testo

# thread che si occupa di gestire la comparazione dei testi
def trust():
   while True:
    semtrust.acquire()
    trust = True
    t = trustitems.pop()
    tfile = open(t.file.name)
    tdata = tfile.read()
    print("inizio comparazione" + t.id)
    comparelist = Testo.objects.filter().exclude(id =t.id)
    for c in comparelist:
        cfile =open(c.file.name)
        cdata= cfile.read()
        rateo=  SequenceMatcher(None, tdata,cdata).ratio() * 100
        if (rateo >25):
            trust = False
    t.trust = trust
    t.save()
    print("fine comparazione di "+ t.id + "il trust è "+ trust)

        


