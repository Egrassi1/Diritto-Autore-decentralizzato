from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),  # pagina prncipale
    path("script/", views.script, name = "script"),
    path("search/",views.search, name = "search"), # richieste per la ricerca di testi o licenze
    path("download/",views.download,name = "download"), # richieste per il download dei testi per qui si è acquistata la licenza
    path("login/",views.login,name = "login"), # richiesta per il loginn
    path("token/",views.token ,name = "token"), # richiesta per il token da firmare per il login
    path("logout/", views.logout, name = "logout"), # richiesta per il logout
    path("ban/",views.ban, name= "ban"),
    path("unban/",views.unban, name= "unban"),
    path("licenza/",views.licenza,name = "licenza"),
    path("test/",views.test,name = "test"),
    path("test2/",views.test2,name = "test2"),
    path("test3/",views.test3,name = "test3"),
    path("test4/",views.test4,name = "test4"),


]