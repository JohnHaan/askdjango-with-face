from django import forms
from .models import Person, Photo


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['group', 'name']


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['person', 'file']

