"""
WSGI config for dirittoautore project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""


from solcx import compile_files, install_solc,set_solc_version
import os

from django.core.wsgi import get_wsgi_application
from web3 import Web3
from dirittoautore import var


from dirittodecent.apps import DirittodecentConfig


from dirittodecent.models import Testo
import hashlib
import threading
from dirittodecent import trust

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dirittoautore.settings')


### startup code

print('Deploy dei contratti')
set_solc_version('0.8.19')
w3 = Web3(Web3.HTTPProvider('HTTP://127.0.0.1:7545'))
w3.eth.default_account = w3.eth.accounts[0] 
print(w3.eth.default_account)
#per il deploy dei contratti si utilizza un portafoglio, in questo caso uso il primo portafoglio di gananche
DirittodecentConfig.contrattoTesto(w3)
DirittodecentConfig.ContrattoLicenza(w3)
var.web3 =w3



application = get_wsgi_application()
