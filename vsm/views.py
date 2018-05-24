from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.template.defaulttags import register
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib import messages
from django.template import loader
from django.conf import settings

from cop.invertedIndex import InvertedIndex
from cop.vectorSpaceModel import VectorSpaceModel
from .storage import handle_uploaded_files
from .forms import CollectionUploadForm
from .decorators import check_recaptcha
from .models import Collection

import os
import json
import urllib

SEL_COLLECTION_COOKIE = 'sel_collection'

# ----------------------------------------
#             AUXILIAR METHODS

# Handles POST request of collection selection
def handleCollectionPost(request):
    current_collection = request.POST.get('collection_selector')
    response = redirect(request.path_info)
    response.set_cookie(SEL_COLLECTION_COOKIE, current_collection)
    return response

# Builds a collection's filesystem path from cookie
def buildCollectionPath(request):
    current_collection = request.COOKIES.get(SEL_COLLECTION_COOKIE, False)
    if current_collection:
        # TODO: validate collection uuid from cookie
        collection_path = os.path.join(settings.COLLECTION_UPLOADS, current_collection)
    else:
        collection_path = "/virs/collection/"       # default fallback
    return collection_path

def standardResponse(request, context, template_path):
    rendered = render_to_string(template_path, context, request=request)
    response = HttpResponse(rendered)
    return response

# ----------------------------------------
#               VIEW METHODS

def delete(request):

    if request.method == 'POST':
        uuid = request.POST.get('collection_deletion')
        print('TO BE REMOVED: ', uuid)

        try:
            # get collection from DB
            col = Collection.objects.get(pk=uuid)

            # make dir if does not exist
            if not os.path.exists( settings.DELETED_COLLECTIONS ):
                os.makedirs(settings.DELETED_COLLECTIONS)

            # get paths
            current_collection_path = os.path.join(settings.COLLECTION_UPLOADS, str(col.id))
            new_collection_path = os.path.join(settings.DELETED_COLLECTIONS, str(col.id))

            # move files
            os.rename(current_collection_path, new_collection_path)

            # delete from database
            col.delete()

            # message visitor
            messages.success(request, 'Coleção removida')

        # collection not in database
        except Collection.DoesNotExist:
            messages.error(request, 'Coleção inexistente')

    return redirect('home')

# Home view
def home(request):

    if request.method == 'POST':
        col = request.POST.get('collection_deletion')
        print('TO BE REMOVED: ', col)
        return redirect('home')

    context = {
        'title': 'Visualization and Information Retrieval System',
        'GOOGLE_RECAPTCHA_PUBLIC_KEY': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
        'collection_wheel': list(Collection.objects.all()),
        'sel_collection': request.COOKIES.get(SEL_COLLECTION_COOKIE,''),
    }

    return render(request, 'vsm/index.html', context)


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

    # build response
    return standardResponse(request, context, 'vsm/upload.html')


# ----------------------------------------
# Shows a collection's Postings List
def postings(request):

    # if POST request, set cookie and redirect to GET request
    if request.method == 'POST':
        return handleCollectionPost(request)

    # load collection
    ii = InvertedIndex( buildCollectionPath(request) )
    postings, friendly_filenames = ii.generatePostingsList()

    # pass computed data in context
    context = {
        'title': 'Arquivo Invertido',
        'collections': list(Collection.objects.all()),
        'sel_collection': request.COOKIES.get(SEL_COLLECTION_COOKIE,''),
        'postings': postings,
        'friendly_filenames': friendly_filenames,
    }

    # build response
    return standardResponse(request, context, 'vsm/postings.html')

# ----------------------------------------
# Shows a collection's Vector Space Model
def vsm(request):

    # if POST request, set cookie and redirect to GET request
    if request.method == 'POST':
        return handleCollectionPost(request)

    vsm = VectorSpaceModel( buildCollectionPath(request) )
    vsm_table = vsm.generateVectorSpaceModel()

    # form table headers
    headers = []
    for term, value in vsm_table.items():
        for header, v in value.items():
            if header is 'tf' or header is 'tfidf':
                for c in range(0, len(v)):
                    headers.append(header + ' ' + str(c))
            else:
                headers.append(header)
        break

    # pass computed data in context
    context = {
        'title': 'Modelo Vetorial',
        'collections': list(Collection.objects.all()),
        'sel_collection': request.COOKIES.get(SEL_COLLECTION_COOKIE,''),
        'vsm': vsm_table,
        'headers': headers,
        'friendly_filenames': vsm.friendly_filenames,
    }

    # build response
    return standardResponse(request, context, 'vsm/vsm.html')


# ----------------------------------------
# Handles user searches over a collection
def query(request):

    # if POST request, set cookie and redirect to GET request
    if request.method == 'POST':
        return handleCollectionPost(request)

    context = {
        'title': 'Consulta',
        'collections': list(Collection.objects.all()),
        'sel_collection': request.COOKIES.get(SEL_COLLECTION_COOKIE,''),
    }

    # build response
    return standardResponse(request, context, 'vsm/query.html')

# ----------------------------------------
#            TEMPLATING METHODS

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)