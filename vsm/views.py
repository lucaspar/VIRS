from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
import vsm.collection as collection

def home(request):
    template = loader.get_template('vsm/index.html')
    context = {
        'section_title': 'VIRS - Visualization and Information Retrieval System',
        'aux' : collection.getAllTokensFrom("/virs/collection/")
    }
    return HttpResponse(template.render(context, request))
