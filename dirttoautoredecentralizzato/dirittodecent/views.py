import hashlib
import json
import math
import threading
import time
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from dirittoautore.functions import handle_uploaded_file,gettoken
from django.contrib.auth import login as Login, logout as Logout
from dirittoautore.form import UploadFileForm
from dirittodecent.trust import trust
from .models import Testo , Bannedusers, Licenza
import eth_account
import os
from datetime import datetime
from django.http import  HttpResponse
import dirittoautore.var as var
from django.contrib.auth.models import User
import pytz
from dirittoautore.settings import BASE_DIR

from django.core.files import File


from django.core.files.uploadedfile import SimpleUploadedFile


url = "https://16.16.124.198/"

def index(request):
   """ Se l'utente è autenticato:
    - in caso di richiesta get viene caricato il template index.html
    - in caso di richiesta post viene prima gestito l'upload del file sul server
      e poi viene ricaricata la pagina perché è necessario rigenerare il token csrf
      Se l'utente non è autenticato viene caricato il template login.html
   """
   starttime = time.time()
   if (request.user.is_superuser):
       Logout(request)
       return render(request,'login.html')
   if request.user.is_authenticated:  
      file = UploadFileForm()
      context = {"Testoaddress" : var.addressTesto,
                 "LicenzaAddress": var.addressLicenza,
                 "form": file }
      if request.method == 'GET' : 
         return render(request , 'index.html',context)
      else:
            form = UploadFileForm(request.POST,request.FILES)
            handle_uploaded_file(request.FILES['file'])  
            print('tempo DEPOSITO:'+str(time.time()-starttime))
            return redirect(url+"/dirittodecent/")
   else:
       return render(request,'login.html')
   

def script(request):

    return HttpResponse(var.addressTesto + ";"+ var.addressLicenza)

def search(request):
  
  """
  le richieste sono dstinte dal campo t ,  t == T significa che l'utente ricerca un testo , t == L una licenza
  testi e licenze vengono recuperati leggendo gli eventi emessi sulla blockchain
  """
  starttime = time.time()
  if request.method == 'GET' :
        
        timezone = request.COOKIES.get("timezone")
        try : timezone= pytz.timezone(timezone) 
        except: timezone= None

        query= request.GET.get('q', None)
        tipo = request.GET.get('t', None)
        pagina = request.GET.get('p', None)
        res = "" 
        if tipo == 'T':
            if (query== ""):
               qs =  Testo.objects.all()
            else:
                q1= Testo.objects.filter(titolo__startswith = query)
                q2= Testo.objects.filter(sender__startswith = query)
                qs = q2.union(q1)
                   
            leng = len(qs)
            pages = leng/4
            if  math.floor(pages) < (pages) : pages = pages +1
            pages = int(pages)
            current = (int(pagina)-1)*4
            for i in range(current, current+4):
                    if(i >= leng) : break
                    t = qs[i]
                    data = datetime.fromtimestamp(t.data,timezone).strftime('%Y-%m-%d %H:%M:%S')
                    try:
                                    if t.trust is None : trust = "Testo in attesa di verifica"
                                    elif (t.trust): trust = "Testo Verificato"
                                    else : trust = "Testo Segnalato come non autentico "
                    except: trust = "Testo Segnalato come non autentico "
                    context = {"titolo" : t.titolo,
                                    "id": t.id,
                                    "autore":t.sender ,
                                    "data":data,
                                    "trust": trust}
                    res =  render_to_string('cardTesto.html', context) +res
            print('tempo trascorso:'+str(time.time()-starttime))
            return HttpResponse(str(pages)+"."+res)
        
        elif tipo == 'L':
            if (query== ""):
               qs =  Licenza.objects.filter(proprietario= str(request.user))
            else:
                q1= Licenza.objects.filter(proprietario = str(request.user),titolo__startswith = query)
                q2= Licenza.objects.filter(proprietario = str(request.user),autore__startswith = query)
                qs = q1.union(q2)
            leng = len(qs)
            pages = leng/4
            if  math.floor(pages) < (pages) : pages = pages +1
            pages = int(pages)
            current = (int(pagina)-1)*4
            for i in range(current, current+4):
                if(i >= leng) : break
                t = qs[i]
                if(t.tipo):
                            tipolog = "Licenza di Riproduzione"
                            desc = "Scadenza : " + datetime.utcfromtimestamp(t.data).strftime('%Y-%m-%d %H:%M:%S')
                else:
                            tipolog ="Licenza di Distribuzione"
                            desc = "Copie da Distribuire :" + str(t.data)
                context = {
                                "tipo": tipolog,
                                "proprietario": t.proprietario,
                                "autore": t.autore,
                                "titolo": t.titolo,
                                "time": datetime.fromtimestamp(t.time,timezone).strftime('%Y-%m-%d %H:%M:%S'),
                                "data": desc,
                                "id": t.id,
                                "link": url+'/dirittodecent/download/?q='+t.id # viene aggiunto al template il link per il download del testo
                                }
                res =  render_to_string('cardLicenza.html', context) +res
            return HttpResponse(str(pages)+"."+res)
        elif tipo == 'mT':
             if (query== ""):
               qs =  Testo.objects.filter(sender = str(request.user))
             else:
                q1= Testo.objects.filter(sender = "request.user",titolo__startswith = query)
                q2= Testo.objects.filter(sender = "request.user",sender__startswith = query)
                qs = q2.union(q1)
                   
             leng = len(qs)
             pages = leng/4
             if  math.floor(pages) < (pages) : pages = pages +1
             pages = int(pages)
             current = (int(pagina)-1)*4
             for i in range(current, current+4):
                    if(i >= leng) : break
                    t = qs[i]
                    data = datetime.fromtimestamp(t.data,timezone).strftime('%Y-%m-%d %H:%M:%S')

                    try:
                                    
                                    if t.trust is None : trust = "Testo in attesa di verifica"
                                    elif (t.trust): trust = "Testo Verificato"
                                    else : trust = "Testo Segnalato come non autentico "
                    except: trust = "Testo Segnalato come non autentico "
                    context = {"titolo" : t.titolo,
                                    "id": t.id,
                                    "autore":t.sender ,
                                    "data":data,
                                    "trust": trust}
                    res =  render_to_string('cardTesto.html', context) +res
             return HttpResponse(str(pages)+"."+res)
        elif tipo == 'mL':
             if (query== ""):
               qs =  Licenza.objects.filter(autore = str(request.user))
             else:
                q1= Licenza.objects.filter(autore = str(request.user),titolo__startswith = query)
                q2= Licenza.objects.filter(autore = str(request.user),autore__startswith = query)
                qs = q1.union(q2)
             leng = len(qs)
             pages = leng/4
             if  math.floor(pages) < (pages) : pages = pages +1
             pages = int(pages)
             current = (int(pagina)-1)*4
             for i in range(current, current+4):
                if(i >= leng) : break
                t = qs[i]
                if(t.tipo):
                            tipolog = "Licenza di Riproduzione"
                            desc = "Scadenza : " + datetime.utcfromtimestamp(t.data).strftime('%Y-%m-%d %H:%M:%S')
                else:
                            tipolog ="Licenza di Distribuzione"
                            desc = "Copie da Distribuire :" + str(t.data)
                context = {
                                "tipo": tipolog,
                                "proprietario": t.proprietario,
                                "autore": t.autore,
                                "titolo": t.titolo,
                                "time": datetime.fromtimestamp(t.time,timezone).strftime('%Y-%m-%d %H:%M:%S'),
                                "data": desc,
                                "id": t.id,
                                "link": url+'/dirittodecent/download/?q='+t.id # viene aggiunto al template il link per il download del testo
                                }
                res =  render_to_string('cardLicenza.html', context) +res
             return HttpResponse(str(pages)+"."+res)

        elif tipo == 'u':    
             b =  Bannedusers.objects.filter(sender = request.user, target__icontains = query)
             leng = len(b)
             pages = leng/4
             if  math.floor(pages) < (pages) : pages = pages +1
             pages = int(pages)
             current = (int(pagina)-1)*4
             for i in range(current, current+5):
                 if(i >= leng) : break
                 utente = b[i]
                 context= {
                     "id": utente.id,
                     "utente": utente.target}
                
                 res = render_to_string('utente.html',context) +res
             return HttpResponse(str(pages)+"."+res)

def licenza(request):
    if (request.method == "POST"):
        body = json.loads(request.body)
        tx = body['tx']
        trans = var.web3.eth.get_transaction_receipt(tx) #autentica la transazione
        if trans is not None:
            valori = var.contrattoLicenza.events.RilascioLicenza().process_receipt(trans)
            valori = valori[0].args
            l = Licenza(valori['id'].hex(), valori['proprietario'],valori['tipo'],valori['autore'],valori['testo'],valori['id_testo'],valori['dati'], valori['time'])
            l.save()
        return HttpResponse("Licenza Registrata")

        
def download(request):
    try:
        query= request.GET.get('q', None)
        l = Licenza.objects.get(id=query)    
        print(l)
        if(l is not None and(str(l.proprietario)== str(request.user) or str(l.autore) == str(request.user)) ):
                testo = Testo.objects.get(id = l.id_testo) 
                file_path = testo.file.name
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as fh:
                        response = HttpResponse(fh.read(), content_type="application/text-plain")
                        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
                        return response
        return HttpResponse("Non hai accesso a questo contenuto")
                
    except: return HttpResponse("Non hai accesso a questo contenuto")

def login(request):
    
    body = json.loads(request.body)
    firma = body['firma']
    msg = body['msg']

    
    message = eth_account.messages.encode_defunct(bytes(msg, encoding='utf8'))
    # calcola l'encoding del messaggio nello standard EIP-191
    address =  eth_account.Account.recover_message(message,signature = firma)

    address = address
 
    if (var.auth[address] == msg) : 
      # verifica se per l'utente che ha firmato era stato depositato nel dictionary un nonce corrispondende a quello ricevuto dalla richiesta
      var.auth[address] = None # il token è consumato
      
      if User.objects.filter(username=address).exists():
          user =   User.objects.get(username=address)
          Login(request, user)
          return HttpResponse("loggato")
      else:
          user = User.objects.create_user(username = address) # se l'utente non esiste se ne crea uno  nuovo sul database
          user.save()
          Login(request,user)
          return HttpResponse("registrato")
      
    var.auth[address] = None
    return HttpResponse("Error")


def token(request): #viene gestita la richiesta del token
    query= request.GET.get('q', None)
    if (query is not None):
        tok = gettoken()
        query = query
        var.auth [query] = tok
        return HttpResponse(tok)
    else: return HttpResponse("invalid request")

def logout(request):
    if request.user.is_authenticated:
        Logout(request)
        # si viene reindirizzati alla pagina di login
    return redirect("index")

def ban(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            Wbreceipt = body['tr']
            event_filter = var.contrattoTesto.events.banevent.create_filter(fromBlock = 0, address = var.addressTesto ,argument_filters = {"sender":body['sender'], "target": body['target'] })
            event_logs = event_filter.get_all_entries()
            for e in event_logs:
                tx_hash = e['transactionHash']
                if(Wbreceipt == tx_hash.hex()):
                    b = Bannedusers(sender = body['sender'],target = body['target'])
                    b.save()
                    break
            return HttpResponse("success")
        except:  return HttpResponse("server error")


def unban(request):
    if request.method == "POST":
         try:
            body = json.loads(request.body)
            Wbreceipt = body['tr']            
            event_filter = var.contrattoTesto.events.unbanevent.create_filter(fromBlock = 0, address = var.addressTesto ,argument_filters = {"sender":body['sender'], "target": body['target'] })
            event_logs = event_filter.get_all_entries()
            for e in event_logs:
                    tx_hash = e['transactionHash']
                    if(Wbreceipt == tx_hash.hex()):
                        b =  Bannedusers.objects.filter(id= body['id'])
                        b.delete()
                        break
            return HttpResponse("success")  
         except:  return HttpResponse("server error")




def test(request):
    directory = BASE_DIR.joinpath('dataset/')
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        f = open(file_path,encoding='utf-8')
        djf= File(f)
        strbytes = f.read() 
        hash = hashlib.md5(strbytes.encode()).hexdigest()
        trans = var.contrattoTesto.functions.mint(filename,hash).build_transaction({
        'from': var.web3.eth.accounts[0],
        'to': var.addressTesto,
        'value': 200000000000000000
        })
        var.web3.eth.send_transaction(trans)
        event_filter = var.contrattoTesto.events.Deposito.create_filter(fromBlock = 0, argument_filters = {"token_id": hash})
        event_logs = event_filter.get_all_entries()
        e = event_logs[0]
        tx_hash = e['transactionHash']
        receipt = var.web3.eth.get_transaction_receipt(tx_hash)
        valori = var.contrattoTesto.events.Deposito().process_receipt(receipt) 
        valori = valori[0].args 
        token_id = valori["token_id"]
        

        sfile = SimpleUploadedFile(filename,bytes(strbytes, encoding='utf-8'))

        t = Testo(hash,sfile,None,valori['titolo'],str(valori['sender']),int(valori['data']))
        print(valori['titolo'])
        print(str(valori['sender']))
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
        print("Deposito eseguito")

        trans = var.contrattoLicenza.functions.mintLicenzaDistribuzione(hash,"",50).build_transaction({
        'from': var.web3.eth.accounts[1],
        'to': var.addressLicenza,
        'value': 50000000
        })
        tx =  var.web3.eth.send_transaction(trans)
        print(tx.hex())
        trans = var.web3.eth.get_transaction_receipt(tx) 
        print(trans)
        #autentica la transazione
        if trans is not None:
            valori = var.contrattoLicenza.events.RilascioLicenza().process_receipt(trans)
           # print(valori)
            valori = valori[0].args
            l = Licenza(valori['id'].hex(), valori['proprietario'],valori['tipo'],valori['autore'],valori['testo'],valori['id_testo'],valori['dati'], valori['time'])
            l.save()
    return HttpResponse("tutto ok")
