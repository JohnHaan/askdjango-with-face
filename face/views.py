from django.db.models import Count
from django.http import Http404
from django.shortcuts import redirect, render
from .models import Person, Photo


def index(request):
    person_qs = Person.objects.annotate(photo_count=Count('photo')).filter(photo_count__gt=0)

    return render(request, 'face/index.html', {
        'person_list': person_qs,
    })


def person_photo(request, pk):
    photo = Photo.objects.filter(person__pk=pk).order_by('?').first()
    if not photo:
        raise Http404
    return redirect(photo.file.url)

