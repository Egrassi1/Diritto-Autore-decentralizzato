"""
WSGI config for dirittoautore project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

from solcx import compile_files, install_solc
import os

from django.core.wsgi import get_wsgi_application
from web3 import Web3
from dirittoautore import var

from dirittodecent.apps import DirittodecentConfig

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dirittoautore.settings')


### startup code

print('Deploy dei contratti')
install_solc('latest')
w3 = Web3(Web3.HTTPProvider('http://18.193.74.219:8545'))
w3.eth.default_account = w3.eth.accounts[0] 
#per il deploy dei contratti si utilizza un portafoglio, in questo caso uso il primo portafoglio di gananche
DirittodecentConfig.contrattoTesto(w3)
DirittodecentConfig.ContrattoLicenza(w3)
var.web3 =w3


application = get_wsgi_application()
