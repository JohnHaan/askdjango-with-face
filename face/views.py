from django.contrib import messages
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from .models import PersonGroup, Person, Photo
from .utils import photo_identify


def index(request):
    group = get_object_or_404(PersonGroup, pk=1)  # FIXME: pk=1인 그룹에 한해서 조회
    person_qs = Person.objects.annotate(photo_count=Count('photo')).filter(photo_count__gt=0)
    identified = []

    if request.method == 'POST':
        photo_file = request.FILES.get('photo')
        face_dict = photo_identify(group, photo_file, max_candidates_return=3)
        for face_id, result_per_face in face_dict.items():
            for result_per_person in result_per_face['candidates']:
                try:
                    person = Person.objects.get(person_id=result_per_person['personId'])
                    identified.append({
                        'name': person.name,
                        'photo_url': resolve_url('person_photo', person.pk),
                        'confidence': '{:.1f}%'.format(result_per_person['confidence'] * 100),
                    })
                except Person.DoesNotExist:
                    pass

        if not identified:
            messages.error(request, '매칭된 아이돌이 없네요. :(.')

    return render(request, 'face/index.html', {
        'person_list': person_qs,
        'identified': identified,
    })


def person_photo(request, pk):
    photo = Photo.objects.filter(person__pk=pk).order_by('?').first()
    if not photo:
        raise Http404
    return redirect(photo.file.url)

