from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from vsm.collection import Collection
from .forms import UploadFileForm
# from somewhere import handle_uploaded_file

def home(request):

    # load collection
    col = Collection("/virs/collection/")
    tokens = col.loadCollection()

    context = {
        'section_title': 'VIRS - Visualization and Information Retrieval System',
        'tokens' : tokens,
    }

    # load template
    template = loader.get_template('vsm/index.html')

    return HttpResponse(template.render(context, request))

def upload(request):
    #Codigo que funciona quando poe localhost:8000/upload
    col = Collection("/virs/collection/")
    tokens = col.loadCollection()

    context = {
        'section_title': 'VIRS - Visualization and Information Retrieval System',
        'tokens' : tokens,
    }

    # load template
    template = loader.get_template('vsm/upload.html')

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


