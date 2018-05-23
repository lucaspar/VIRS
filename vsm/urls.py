from django.urls import path

from . import views

urlpatterns = [
    path('',                    views.home,     name='home'),
    path('upload',              views.upload,   name='upload'),
    path('arquivo_invertido',   views.postings, name='postings'),
    path('modelo_vetorial',     views.vsm,      name='vsm'),
    path('pesquisa',            views.query,    name='query'),
    path('remover_colecao',     views.delete,   name='delete_collection'),
]
