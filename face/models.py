from os.path import splitext
from uuid import uuid4
from django.conf import settings
from django.core.files import File
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from imagekit.models import ProcessedImageField
from imagekit.processors import Thumbnail
from jsonfield import JSONField
from PIL import Image
import cognitive_face as CF


def upload_to(instance, filename):
    new_name = uuid4().hex + splitext(filename)[-1]
    return '{}/{}/{}'.format(instance.person.name.replace('/', '-'), new_name[:3], new_name[3:])


class PersonGroup(models.Model):
    name = models.CharField(max_length=128, db_index=True,
                            validators=[RegexValidator(r'^[a-z0-9]+$', '숫자/영소문자로만 입력해주세요.')])

    def __str__(self):
        return self.name

    def enroll(self):
        CF.person_group.create(self.name)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.enroll()


class Person(models.Model):
    group = models.ForeignKey(PersonGroup)
    name = models.CharField(max_length=128, db_index=True)
    person_id = models.UUIDField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = [
            ['group', 'name'],
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('person_detail', args=[self.pk])

    def enroll(self, commit=True):
        res = CF.person.create(self.group.name, self.name)
        self.person_id = res['personId']
        if commit:
            self.save()

    def save(self, *args, **kwargs):
        if not self.person_id:
            self.enroll(commit=False)
        super().save(*args, **kwargs)


class Photo(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    file = ProcessedImageField(upload_to=upload_to,
                               processors=[Thumbnail(512, 512, crop=False)],
                               format='JPEG',
                               options={'quality': 80})
    persisted_face_id = models.UUIDField(blank=True, null=True)
    props = JSONField(blank=True)  # 별도로 detection을 할 예정
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return 'Photo of {}'.format(self.person.name)

    @property
    def emotion(self):
        if self.props:
            return self.props[0]['faceAttributes']['emotion']

    def enroll(self, commit=True):
        try:
            res = CF.person.add_face(self.file, self.person.group.name, self.person.person_id)
            self.persisted_face_id = res['persistedFaceId']
        except CF.CognitiveFaceException:
            self.is_valid = False
        finally:
            self.file.seek(0)
        if commit:
            self.save()

    def detect(self, commit=True):
        attributes = 'age,gender,headPose,smile,facialHair,glasses,emotion,makeup,accessories,occlusion,blur,exposure,noise'
        self.props = CF.face.detect(self.file, face_id=True, landmarks=True, attributes=attributes)
        self.file.seek(0)
        if commit:
            self.save()

    def save(self, *args, **kwargs):
        if not self.persisted_face_id:
            self.enroll(commit=False)

        if not self.props:
            self.detect(commit=False)

        super().save(*args, **kwargs)

