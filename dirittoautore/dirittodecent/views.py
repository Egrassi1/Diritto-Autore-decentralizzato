import json
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from dirittoautore.functions import match,handle_uploaded_file,gettoken
from django.contrib.auth import login as Login, logout as Logout
from dirittoautore.form import UploadFileForm
from .models import Testo
import eth_account
import os
from datetime import datetime
from django.http import HttpResponse
import dirittoautore.var as var
from django.contrib.auth.models import User

import math



def index(request):
   """ Se l'utente è autenticato:
    - in caso di richiesta get viene caricato il template index.html
    - in caso di richiesta post viene prima gestito l'upload del file sul server
      e poi viene ricaricata la pagina perché è necessario rigenerare il token csrf
      Se l'utente non è autenticato viene caricato il template login.html
   """
   if (request.user == 'eugenio'):
       logout(request)

   if request.user.is_authenticated:  
      print(request.user)
      file = UploadFileForm()
      context = {"Testoaddress" : var.addressTesto,
                 "LicenzaAddress": var.addressLicenza,
                 "form": file }
      if request.method == 'GET' : 
         return render(request , 'index.html',context)
      else:
            form = UploadFileForm(request.POST,request.FILES)
            handle_uploaded_file(request.FILES['file'])  
            return render(request , 'index.html',context)
   else:
       return render(request,'login.html')
   

def script(request):

    return HttpResponse(var.addressTesto + ";"+ var.addressLicenza)

def search(request):
  
  """
  le richieste sono dstinte dal campo t ,  t == T significa che l'utente ricerca un testo , t == L una licenza
  testi e licenze vengono recuperati leggendo gli eventi emessi sulla blockchain
  """



  if request.method == 'GET' :
        query= request.GET.get('q', None)
        tipo = request.GET.get('t', None)
        pagina = request.GET.get('p', None)
        res = "" 
        resTit = ""
        resAut = ""
        if tipo == 'T':
          

           event_signature_hash = var.web3.keccak(text="Deposito(address,string,string,uint256)").hex() # viene calcolata la firma dell'evento
           event_filter = var.web3.eth.filter({'fromBlock': 0, 'address': var.addressTesto, 'topics': [event_signature_hash]})
          # si costruisce un event filter per l'evento specifico del relativo contratto e si leggono tutte le transazioni dal blocco 0
           event_logs = event_filter.get_all_entries()

           leng = len(event_logs)
           pages = round(leng/2)
           current = (int(pagina)-1)*2
        

           for i in range(current, current+2):
               if(i >= leng) : break

               e = event_logs[i]
               tx_hash = e['transactionHash']
               receipt = var.web3.eth.get_transaction_receipt(tx_hash)
               valori = var.contrattoTesto.events.Deposito().process_receipt(receipt) 
               #legge i log della transazione coerentemente con l'istanza del contratto
               valori = valori[0].args  #dictionary dei valori emessi dall'evento
               titolo =   valori["titolo"]
               id = valori["token_id"]
               autore = valori["sender"]
               data = datetime.utcfromtimestamp(valori["data"]).strftime('%Y-%m-%d %H:%M:%S')

               #per determinare il livello di trust bisogna interrogare il database mySQL
               trust = Testo.objects.get(id= id).trust
               if (trust): trust = "Testo Verificato"
               elif(not trust) : trust = "Testo Segnalato come non autentico "
               else : trust = "Testo in attesa di verifica"

               context = {"titolo" : titolo,
                 "id": id,
                 "autore":autore ,
                 "data":data,
                 "trust": trust}
               if(query == ""):
                 res =  render_to_string('cardTesto.html', context) +res
               else:
                  if(match(query,titolo)): resTit =  render_to_string('cardTesto.html', context) +resTit
                  elif(match(query,autore)): resAut = render_to_string('cardTesto.html', context) + resAut
           if(query == ""): return HttpResponse(str(pages)+"."+res)   
           # se il campo q è vuoto la ricerca è mirata a visualizzare tutti i risultanti 
           # non è necessario dividere per autore o titolo
           else:
            if(resTit != "") :resTit = "<p>per titolo</p>"+ resTit
            if(resAut!= ""): resAut = "<p>per autore</p>"+ resAut  
           return HttpResponse(str(pages)+"."+resTit+resAut)
      
        elif tipo == 'L':           
            tipolog =""
            propietario = ""
            autore = ""
            titolo = ""
            data = ""
            desc = ""
            id = ""
            event_signature_hash = var.web3.keccak(text="RilascioLicenza(bool,address,address,string,string,uint256,bytes20,uint256)").hex()
            event_filter = var.web3.eth.filter({'fromBlock': 0, 'address': var.addressLicenza, 'topics': [event_signature_hash]})
            
            event_logs = event_filter.get_all_entries()

            leng = len(event_logs)
            pages = round(leng/2)
            current = (int(pagina)-1)*2
        

            for i in range(current, current+2):
               if(i >= leng) : break

               e = event_logs[i]
               tx_hash = e['transactionHash']
               receipt = var.web3.eth.get_transaction_receipt(tx_hash)
               valori = var.contrattoLicenza.events.RilascioLicenza().process_receipt(receipt)
               valori = valori[0].args  

               proprietario = valori['proprietario']
               autore =valori['autore']
               titolo = valori['testo']
               data = datetime.utcfromtimestamp(valori["time"]).strftime('%Y-%m-%d %H:%M:%S')
               desc = valori['dati']
               id = valori["id"].hex()
               # il funzionamento è analogo a quello descritto per i testi.
               # In aggiunta viene controllato che l'utente da cui parte la richiesta 
               # sia il proprietario delle licenze.
               a = str(request.user)
               b= str(proprietario).upper()

               if (a == b):
                  if(valori['tipo']):
                        tipolog = "Licenza di Riproduzione"
                        desc = "Scadenza : " + datetime.utcfromtimestamp(desc).strftime('%Y-%m-%d %H:%M:%S')
                  else:
                      tipolog ="Licenza di Distribuzione"
                      desc = "Copie da Distribuire :" + str(desc)
                  context = {
                   "tipo": tipolog,
                   "proprietario": proprietario,
                   "autore": autore,
                   "titolo": titolo,
                   "time": data,
                   "data": desc,
                   "id": id,
                   "link": "http://127.0.0.1:8000/dirittocenet/download/?q="+id # viene aggiunto al template il link per il download del testo
               }
                  
                  if(query == ""):
                     res =  render_to_string('cardLicenza.html', context) +res
                  elif(match(query,titolo)): resTit =  render_to_string('cardLicenza.html', context) +resTit
                  elif(match(query,id)): resAut = render_to_string('cardLicenza.html', context) + resAut
            if(query == ""): return HttpResponse(str(pages)+"."+res)
            else:
              if(resTit != "") :resTit = "<p>per Titolo</p>"+ resTit
              if(resAut!= ""): resAut = "<p>per Id</p>"+ resAut  
              return HttpResponse(str(pages)+"."+resTit+resAut)
                 


      

def download(request):
    query= request.GET.get('q', None)
    #bisogna controllare che la licenza per cui è fatta la richeista di download appartenga all'utente autenticato 
    event_signature_hash = var.web3.keccak(text="RilascioLicenza(bool,address,address,string,string,uint256,bytes20,uint256)").hex()
    event_filter = var.web3.eth.filter({'fromBlock': 0, 'address': var.addressLicenza, 'topics': [event_signature_hash]})
    event_logs = event_filter.get_all_entries()
    print(event_logs)
    for e in event_logs:
        tx_hash = e['transactionHash']
        receipt = var.web3.eth.get_transaction_receipt(tx_hash)
        valori = var.contrattoLicenza.events.RilascioLicenza().process_receipt(receipt)
        valori = valori[0].args
        print(valori)
        id = valori['id'].hex()
        if(id == query):
            prop = valori['proprietario']

            print(prop)
            a = str(request.user)
            b = str(prop).upper()
        
            if (a == b):

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
    print(body)
    firma = body['firma']
    msg = body['msg']

    
    message = eth_account.messages.encode_defunct(bytes(msg, encoding='utf8'))
    # calcola l'encoding del messaggio nello standard EIP-191
    address =  eth_account.Account.recover_message(message,signature = firma)

    address = address.upper()

    if (var.auth[address.upper()] == msg) : 
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
    query = query.upper()
    var.auth [query] = tok
    print(query)
    print(var.auth[query])
    return HttpResponse(tok)

def logout(request):
    if request.user.is_authenticated:
        Logout(request)
        return redirect("index") # si viene reindirizzati alla pagina di login