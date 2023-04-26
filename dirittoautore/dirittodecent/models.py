from django.db import models
from dirittoautore.settings import STATIC_URL

from django.db.models import UniqueConstraint

# questa classe definisce l'oggetto testo che viene poi memorizzato nel database mySQL


class Bannedusers(models.Model):
    sender = models.CharField(max_length = 100)
    target= models.CharField(max_length = 100)
    UniqueConstraint(fields=['target', 'sender'], name='unique_ban')

class Testo(models.Model):
    id = models.CharField(max_length = 100, primary_key= True)
    file = models.FileField(upload_to = STATIC_URL +'uploads/')
    trust = models.BooleanField(blank=True, null=True)



