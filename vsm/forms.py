from django import forms
from .models import Collection

class CollectionUploadForm(forms.ModelForm):

    class Meta:
        model = Collection
        fields = ('title', 'description')
