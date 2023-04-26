# modello di form che su index permette di caricare il file da depositare
from django import forms
import os


class UploadFileForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'accept':'.txt', 'id': 'filefield'}))



