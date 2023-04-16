# modello di form che su index permette di caricare il file da depositare
from django import forms
class UploadFileForm(forms.Form):
    file = forms.FileField()

