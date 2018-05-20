from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import loader

from cop.invertedIndex import InvertedIndex
from .storage import handle_uploaded_files
from .forms import UploadFileForm

# Home view
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

# Upload view (GET and POST)
def upload(request):

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_files(request.FILES.getlist('files'))
            return redirect('home')
    else:
        form = UploadFileForm()

    return render(request, 'upload.html', {'form': form})
