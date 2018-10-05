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
from cop.pageRank import PageRank
from .storage import handle_uploaded_files
from .forms import CollectionUploadForm
from .decorators import check_recaptcha
from .models import Collection

import os
import json
import time
import math
import urllib

SEL_COLLECTION_COOKIE = 'sel_collection'

# ----------------------------------------
#             AUXILIAR METHODS

# Handles POST request of collection selection by setting a session cookie
def handleCollectionPost(request):

    # get referer for redirect
    referer = request.META.get('HTTP_REFERER') if request.META.get('HTTP_REFERER') else '/'
    response = redirect(referer)

    # if POST, set a cookie
    if request.method == 'POST':
        current_collection = request.POST.get('collection_selector')
        response.set_cookie(SEL_COLLECTION_COOKIE, current_collection)

    return response

# Builds a collection's filesystem path from cookie
def buildCollectionPath(request):
    collection_path = None
    current_collection = request.COOKIES.get(SEL_COLLECTION_COOKIE, None)
    # check whether the object exists in database
    if current_collection and Collection.objects.get(pk=current_collection):
        collection_path = os.path.join(settings.COLLECTION_UPLOADS, current_collection)
    return collection_path

def standardResponse(request, context, template_path):
    rendered = render_to_string(template_path, context, request=request)
    response = HttpResponse(rendered)
    return response

# ----------------------------------------
#               VIEW METHODS

# collection deletion procedure
def delete(request):

    if request.method == 'POST':
        uuid = request.POST.get('collection_deletion')

        try:
            # get collection from DB
            col = Collection.objects.get(pk=uuid)
            if (col.read_only):
                messages.error(request, 'It is not possible to delete this collection')
                return redirect('home')

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
            messages.success(request, 'Collection deleted')

        # collection not in database
        except Collection.DoesNotExist:
            messages.error(request, 'Collection does not exist')

    return redirect('home')

# Home view
def home(request):

    context = {
        'title'                         : 'Visualization and Information Retrieval System',
        'GOOGLE_RECAPTCHA_PUBLIC_KEY'   : settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
        'collection_wheel'              : list(Collection.objects.all()),
        'sel_collection'                : request.COOKIES.get(SEL_COLLECTION_COOKIE,''),
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
            messages.success(request, 'New collection created')

            return redirect('home')

    # handle other requests or POST failure
    context = {
        'title': 'Upload Collection',
        'GOOGLE_RECAPTCHA_PUBLIC_KEY': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
    }

    # build response
    return standardResponse(request, context, 'vsm/upload.html')


# ----------------------------------------
# Shows a collection's Postings List
def postings(request):

    postings = []
    friendly_filenames = {}

    # load collection
    collection_path = buildCollectionPath(request)
    if collection_path:
        ii = InvertedIndex( collection_path )
        postings, friendly_filenames = ii.generatePostingsList()

    # pass computed data in context
    context = {
        'title'             : 'Inverted Index',
        'reference'         : 'https://en.wikipedia.org/wiki/Inverted_index',
        'collections'       : list(Collection.objects.all()),
        'sel_collection'    : request.COOKIES.get(SEL_COLLECTION_COOKIE, ''),
        'postings'          : postings,
        'friendly_filenames': friendly_filenames,
    }

    # build response
    return standardResponse(request, context, 'vsm/postings.html')

# ----------------------------------------
# Shows a collection's Vector Space Model
def vsm(request):

    vsm_table = {}
    headers = []
    vsm = None

    collection_path = buildCollectionPath(request)
    if collection_path:

        vsm = VectorSpaceModel( collection_path )
        vsm_table = vsm.generateVectorSpaceModel()

        # form table headers
        for term, value in vsm_table.items():
            for header, v in value.items():
                if header is 'tf' or header is 'tfidf':
                    th = '[F]' if header is 'tf' else '[TF×IDF]'
                    for c in range(0, len(v)):
                        ffn = vsm.friendly_filenames[vsm.file_list[c]]
                        headers.append(th.upper() + ' ' + ffn)
                else:
                    headers.append(header.upper())
            break

    # pass computed data in context
    context = {
        'title': 'Vector Space Model',
        'reference': 'https://en.wikipedia.org/wiki/Vector_space_model',
        'collections': list(Collection.objects.all()),
        'sel_collection': request.COOKIES.get(SEL_COLLECTION_COOKIE,''),
        'vsm': vsm_table,
        'headers': headers,
        'friendly_filenames': vsm.friendly_filenames if vsm else {},
    }

    # build response
    return standardResponse(request, context, 'vsm/vsm.html')


# ----------------------------------------
# Handles user searches over a collection
def query(request):

    query = ''
    outputs = {
        'ranking': [],
        'tfidfs': [],
        'terms': [],
        'docs': [],
        'ffn': {},
        'wq': [],
    }

    if request.method == 'POST':

        query = request.POST.get('query')
        collection_path = buildCollectionPath(request)

        # get collection path and process query
        if collection_path and query:
            vsm = VectorSpaceModel( collection_path )
            outputs = vsm.processQuery(query)

    context = {
        'title'     : 'Search',
        'reference' : 'https://en.wikipedia.org/wiki/Cosine_similarity',
        'GOOGLE_RECAPTCHA_PUBLIC_KEY': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
        'collections': list(Collection.objects.all()),
        'sel_collection': request.COOKIES.get(SEL_COLLECTION_COOKIE,''),
        'query'     : query,
        'ranking'   : outputs['ranking'],
        'tfidfs'    : outputs['tfidfs'],
        'terms'     : outputs['terms'],
        'docs'      : outputs['docs'],
        'ffn'       : outputs['ffn'],
        'wq'        : outputs['wq'],
    }

    # build response
    return standardResponse(request, context, 'vsm/query.html')

# ----------------------------------------
# Compute collection's PageRank
def pagerank(request):

    evolution = []
    friendly_filenames = {}

    # default PageRank parameters
    alpha = 0.1
    err_threshold = 0.01

    if request.method == 'POST':
        err_threshold   = float(request.POST.get('err_threshold'))
        alpha           = float(request.POST.get('alpha'))

    # load collection
    collection_path = buildCollectionPath(request)
    if collection_path:
        pr = PageRank( collection_path, err_threshold, alpha )
        evolution = pr.finalPageRank()
        friendly_filenames = pr.friendly_filenames

    # pass computed data in context
    context = {
        'title':                'PageRank',
        'reference':            'https://en.wikipedia.org/wiki/PageRank',
        'collections':          list(Collection.objects.all()),
        'sel_collection':       request.COOKIES.get(SEL_COLLECTION_COOKIE,''),
        'evolution':            evolution,
        'js_evolution':         json.dumps(evolution),
        'friendly_filenames':   friendly_filenames,
        'err_threshold':        err_threshold,
        'alpha':                alpha,
    }

    # build response
    return standardResponse(request, context, 'vsm/pagerank.html')

# ----------------------------------------
#            TEMPLATING METHODS

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def index(sequence, position):
    return sequence[position]

@register.filter
def roundAndAround(number):
    number = str(round(number, 3))
    # reverse the string before and after applying zfill()
    return number[::-1].zfill(5)[::-1]
