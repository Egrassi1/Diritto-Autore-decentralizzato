import hashlib
import json
import math
import threading
import time
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from dirittoautore.functions import match,handle_uploaded_file,gettoken
from django.contrib.auth import login as Login, logout as Logout
from dirittoautore.form import UploadFileForm
from dirittodecent.trust import trust
from .models import Testo , Bannedusers, Licenza
import eth_account
import os
from datetime import datetime
from django.http import Http404, HttpResponse
import dirittoautore.var as var
from django.contrib.auth.models import User
import pytz


from django.core.files import File


url = "http://127.0.0.1:8000"

def index(request):
   """ Se l'utente è autenticato:
    - in caso di richiesta get viene caricato il template index.html
    - in caso di richiesta post viene prima gestito l'upload del file sul server
      e poi viene ricaricata la pagina perché è necessario rigenerare il token csrf
      Se l'utente non è autenticato viene caricato il template login.html
   """
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
  #starttime = time.time()
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
            l = Licenza(valori['id'].hex(), valori['proprietario'],valori['tipo'],valori['autore'],valori['testo'],valori['dati'], valori['time'])
            l.save()
        return HttpResponse("ok")

        


def download(request):
    query= request.GET.get('q', None)
    #bisogna controllare che la licenza per cui è fatta la richeista di download appartenga all'utente autenticato 
    event_signature_hash = var.web3.keccak(text="RilascioLicenza(bool,address,address,string,string,uint256,bytes20,uint256)").hex()
    event_filter = var.web3.eth.filter({'fromBlock': 0, 'address': var.addressLicenza, 'topics': [event_signature_hash]})
    event_logs = event_filter.get_all_entries()
  
    for e in event_logs:
        tx_hash = e['transactionHash']
        receipt = var.web3.eth.get_transaction_receipt(tx_hash)
        valori = var.contrattoLicenza.events.RilascioLicenza().process_receipt(receipt)
        valori = valori[0].args
        id = valori['id'].hex()
        if(id == query):
            prop = valori['proprietario']
            aut = valori['autore']
           
            a = str(request.user)
            b = str(prop)
            c = str(aut)
        
            if (a == b or a == c):

                testo = Testo.objects.get(id = valori['id_testo'])
                
                file_path = testo.file.name
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as fh:
                        response = HttpResponse(fh.read(), content_type="application/text-plain")
                        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                        return response
    return HttpResponse("Non hai accesso a questo contenuto")


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
    tok = gettoken()
    query = query
    var.auth [query] = tok
    return HttpResponse(tok)

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

