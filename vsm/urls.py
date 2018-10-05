from django.urls import path

from . import views

urlpatterns = [
    path('',                    views.home,                 name='home'),
    path('upload',              views.upload,               name='upload'),
    path('inverted_index',      views.postings,             name='postings'),
    path('vector_space_model',  views.vsm,                  name='vsm'),
    path('search',              views.query,                name='query'),
    path('pagerank',            views.pagerank,             name='pagerank'),
    path('delete_collection',   views.delete,               name='delete_collection'),
    path('select_collection',   views.handleCollectionPost, name='select_collection'),
]
