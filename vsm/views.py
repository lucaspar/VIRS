from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from cop.invertedIndex import InvertedIndex

def home(request):

    # load collection
    ii = InvertedIndex("/virs/collection/")
    tokens = ii.collectionPostingsList()
    context = {
        'section_title': 'VIRS - Visualization and Information Retrieval System',
        'tokens' : tokens,
    }

    # load template
    template = loader.get_template('vsm/index.html')

    return HttpResponse(template.render(context, request))
