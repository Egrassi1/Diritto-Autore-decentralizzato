from asyncore import loop
from django.apps import AppConfig
import os
from web3 import Web3
from solcx import compile_files, install_solc
import dirittoautore.var as var

import threading
import time


#all'avvio del server viene effettuato il deploy dei contratti

class DirittodecentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dirittodecent'

    def contrattoTesto(w3):
       
         contract_testo = compile_files(['testo.sol'],output_values=["abi", "bin"])
         id_testo, interface_testo = contract_testo.popitem()
         bytecode = interface_testo['bin'] 
         abi = interface_testo['abi'] 
         w3.eth.default_account = w3.eth.accounts[0]
         var.contrattoTesto = w3.eth.contract(abi=abi, bytecode=bytecode)
         #il costruttore viene inizializzato con un costo in WEI per il deposito dei testi
         tx_hash = var.contrattoTesto.constructor(200000000000000000).transact()  
         tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
         addressTesto = tx_receipt.contractAddress
         print(addressTesto)
         var.addressTesto = str(addressTesto)   
         #l'indirizzo del contratto viene salvato nel modulo var, verra poi passato ai template
    
    def ContrattoLicenza(w3):
        contract_licenza = compile_files(['licenza.sol'],output_values=["abi", "bin"])
        id_licenza ,interface_licenza = contract_licenza.popitem()
        id_licenza ,interface_licenza = contract_licenza.popitem()
        bytecode = interface_licenza['bin'] 
        abi = interface_licenza['abi'] 
        var.contrattoLicenza = w3.eth.contract(abi=abi, bytecode=bytecode)
         #il costruttore viene inizializzato con un costo base in WEI per le licenze (questo salirà proporzionalmente alle copie o alla scadenza)
        tx_hash = var.contrattoLicenza.constructor(var.addressTesto,1000000,1000000).transact()
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(tx_receipt.contractAddress)
        var.addressLicenza = str(tx_receipt.contractAddress)


         
    def ready(self):
        if os.environ.get('RUN_MAIN'):
            '''''
            print('Deploy dei contratti')
            install_solc('latest')
            w3 = Web3(Web3.HTTPProvider('http://18.193.74.219:8545'))
            w3.eth.default_account = w3.eth.accounts[0] 
             #per il deploy dei contratti si utilizza un portafoglio, in questo caso uso il primo portafoglio di gananche
            DirittodecentConfig.contrattoTesto(w3)
            DirittodecentConfig.ContrattoLicenza(w3)
            var.web3 =w3
            '''''
            # viene salvato un riferimento al provider web3
            

