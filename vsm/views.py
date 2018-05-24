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
from cop.similarity import Similarity
from .storage import handle_uploaded_files
from .forms import CollectionUploadForm
from .decorators import check_recaptcha
from .models import Collection

import os
import json
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

# collection deletion procedure
def delete(request):

    if request.method == 'POST':
        uuid = request.POST.get('collection_deletion')

        try:
            # get collection from DB
            col = Collection.objects.get(pk=uuid)
            if (col.read_only):
                messages.error(request, 'Não é possível remover esta coleção')
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
            messages.success(request, 'Coleção removida')

        # collection not in database
        except Collection.DoesNotExist:
            messages.error(request, 'Coleção inexistente')

    return redirect('home')

# Home view
def home(request):

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

    # load collection
    ii = InvertedIndex( buildCollectionPath(request) )
    postings, friendly_filenames = ii.generatePostingsList()

    # pass computed data in context
    context = {
        'title': 'Arquivo Invertido',
        'reference': 'https://pt.wikipedia.org/wiki/Listas_invertidas',
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

    vsm = VectorSpaceModel( buildCollectionPath(request) )
    vsm_table = vsm.generateVectorSpaceModel()

    # form table headers
    headers = []
    for term, value in vsm_table.items():
        for header, v in value.items():
            if header is 'tf' or header is 'tfidf':
                for c in range(0, len(v)):
                    ffn = vsm.friendly_filenames[vsm.file_list[c]]
                    headers.append(header.upper() + '-' + ffn)
            else:
                headers.append(header.upper())
        break

    # pass computed data in context
    context = {
        'title': 'Modelo Vetorial',
        'reference': 'https://pt.wikipedia.org/wiki/Modelo_vetorial_em_sistemas_de_recupera%C3%A7%C3%A3o_da_informa%C3%A7%C3%A3o',
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

    ranking = []
    docs = []
    tfidfs = []
    wq = []
    col_terms = []
    ffn = {}

    if request.method == 'POST':

        # save query for processing
        query = request.POST.get('query')
        file = open("query/query.txt","w")
        file.write(str(query))
        file.close()

        # process query
        query_ii_obj = InvertedIndex("/virs/query/")
        query_ii = query_ii_obj.generatePostingsList()

        # process selected collection
        vsm = VectorSpaceModel( buildCollectionPath(request) )
        vsm_table = vsm.generateVectorSpaceModel()

        ffn = vsm.friendly_filenames                # save friendly filenames relation
        docs = vsm.file_list                        # documents list
        wq = [0] * len(vsm_table)                   # query terms weights (TFIDFs)
        tfidfs = [[] for i in range(len(docs))]     # documents terms weights (TFIDFs)

        col_terms = ['' for i in range(len(vsm_table))]

        # calculate query weights
        max_freq = 0
        query_terms = query_ii[0]
        for t in query_terms:
            max_freq = max(max_freq, query_terms[t][0][1])

        for dn, doc in enumerate(docs):
            for tn, t in enumerate(vsm_table):

                col_terms[tn] = t

                # calculate term's tfidf in query
                freq = query_terms[t][0][1] if t in query_terms else 0
                if freq > 0 and t in vsm_table:
                    print('idf:', vsm_table[t]['idf'])
                    wq[tn] = ( 0.5 + ( 0.5 * freq / max_freq ) ) * vsm_table[t]['idf']
                else:
                    wq[tn] = 0

                # append to tfidfs
                tfidfs[dn].append(vsm_table[t]['tfidf'][dn])
                # if t in query_vsm:
                #     print(query_vsm[t])
                #     wq[tn] = query_vsm[t]['tfidf'][0]

        sim = Similarity()
        ranking = sim.calculate_rank(docs, tfidfs, wq)

    context = {
        'title': 'Consulta',
        'reference': 'https://en.wikipedia.org/wiki/Cosine_similarity',
        'GOOGLE_RECAPTCHA_PUBLIC_KEY': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
        'collections': list(Collection.objects.all()),
        'sel_collection': request.COOKIES.get(SEL_COLLECTION_COOKIE,''),
        'ranking': ranking,
        'terms': col_terms,
        'tfidfs': tfidfs,
        'query': query,
        'docs': docs,
        'ffn': ffn,
        'wq': wq,
    }

    # build response
    return standardResponse(request, context, 'vsm/query.html')

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
