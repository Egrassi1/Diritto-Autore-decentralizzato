from django.db import models
from dirittoautore.settings import STATIC_URL

from django.db.models import UniqueConstraint
from django.db.models.functions import Lower

# questa classe definisce l'oggetto testo che viene poi memorizzato nel database mySQL


class Bannedusers(models.Model):
    sender = models.CharField(max_length = 100)
    target= models.CharField(max_length = 100)
    class Meta:
        constraints = [
        UniqueConstraint(Lower('target'),Lower('sender').desc(), name='unique_ban')
        ]

class Testo(models.Model):
    id = models.CharField(max_length = 100, primary_key= True)
    file = models.FileField(upload_to = STATIC_URL +'uploads/')
    trust = models.BooleanField(blank=True, null=True)
    titolo = models.CharField(max_length=100)
    sender = models.CharField(max_length=100)
    data = models.PositiveIntegerField(default = 0)

class Licenza(models.Model):
     id =  models.CharField(max_length = 100, primary_key= True)
     proprietario = models.CharField(max_length = 100)
     tipo = models.BooleanField()
     autore = models.CharField(max_length = 100)
     titolo = models.CharField(max_length = 100)
     data = models.PositiveIntegerField(default = 0)
     time = models.PositiveIntegerField(default = 0)




