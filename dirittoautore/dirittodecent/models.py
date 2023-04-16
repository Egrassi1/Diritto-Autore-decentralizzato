from django.db import models
from dirittoautore.settings import STATIC_URL

# questa classe definisce l'oggetto testo che viene poi memorizzato nel database mySQL

class Testo(models.Model):
    id = models.CharField(max_length = 100, primary_key= True)
    file = models.FileField(upload_to = STATIC_URL +'uploads/')
    trust = models.BooleanField(blank=True, null=True)
   