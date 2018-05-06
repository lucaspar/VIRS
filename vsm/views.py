from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render

def home(request):
    template = loader.get_template('vsm/index.html')
    context = {
        'section_title': 'VIRS - Visualization and Information Retrieval System'
    }
    return HttpResponse(template.render(context, request))
