from django import forms

class UploadFileForm(forms.Form):

    title = forms.CharField(max_length=50)
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))