from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from cop.invertedIndex import InvertedIndex

# from somewhere import handle_uploaded_file
from .forms import UploadFileForm

def home(request):

    # load collection
    ii = InvertedIndex("/virs/collection/")
    tokens = ii.collectionPostingsList()
    context = {
        'section_title': 'VIRS - Visualization and Information Retrieval System',
        'tokens' : tokens,
    }

    # load template
    template = loader.get_template('index.html')

    return HttpResponse(template.render(context, request))

def upload(request):
    #Codigo que funciona quando poe localhost:8000/upload
    col = InvertedIndex("/virs/collection/")
    tokens = col.collectionPostingsList()

    context = {
        'section_title': 'VIRS - Visualization and Information Retrieval System',
        'tokens' : tokens,
    }

    # load template
    template = loader.get_template('upload.html')

    return HttpResponse(template.render(context, request))

    #Do exemplo
    # if request.method == 'POST':
    #     form = UploadFileForm(request.POST, request.FILES)
    #     if form.is_valid():
    #         handle_uploaded_file(request.FILES['file'])
    #         return HttpResponseRedirect('/success/url/')
    # else:
    #     form = UploadFileForm()
    # return render(request, 'upload.html', {'form': form})

    # template = loader.get_template('vsm/upload.html')
    # return HttpResponse(template.render(request))


