from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template import loader
from django.conf import settings

from cop.invertedIndex import InvertedIndex
from .storage import handle_uploaded_files
from .forms import CollectionUploadForm
from .decorators import check_recaptcha
from .models import Collection

import json
import urllib

# Home view
def home(request):

    # load collection
    ii = InvertedIndex("/virs/collection/")
    tokens = ii.collectionPostingsList()
    context = {
        'title': 'Visualization and Information Retrieval System',
        'tokens' : tokens,
    }

    # load template
    template = loader.get_template('vsm/index.html')

    return HttpResponse(template.render(context, request))


# ----------------------------------------
# Handle user uploads (GET and POST)
@check_recaptcha
def upload(request):

    # handle POST request
    if request.method == 'POST':
        form = CollectionUploadForm(request.POST, request.FILES)
        file_list = request.FILES.getlist('files')

        # check form validation
        if form.is_valid() and request.recaptcha_is_valid:

            model = form.save(commit=False)
            model.corpus_size = len(file_list)

            # upload files
            handle_uploaded_files(file_list, dir_name=str(model.id))

            # save model to database
            model.save()
            messages.success(request, 'Nova coleção adicionada')

            return redirect('home')

    # handle other requests or POST failure
    context = {
        'title': 'Upload de Coleção',
        'GOOGLE_RECAPTCHA_PUBLIC_KEY': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
    }
    return render(request, 'vsm/upload.html', context)


# ----------------------------------------
# Shows a collection's Postings List
def postings(request):
    context = {
        'title': 'Arquivo Invertido',
    }
    return render(request, 'vsm/postings.html', context)


# ----------------------------------------
# Shows a collection's Vector Space Model
def vsm(request):
    context = {
        'title': 'Modelo Vetorial',
    }
    return render(request, 'vsm/vsm.html', context)


# ----------------------------------------
# Handles user searches over a collection
def query(request):
    context = {
        'title': 'Consulta',
    }
    return render(request, 'vsm/query.html', context)
