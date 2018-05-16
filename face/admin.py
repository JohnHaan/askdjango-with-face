import time
import cognitive_face as CF
from django.contrib import admin
from .models import PersonGroup, Person, Photo
from .forms import PersonForm, PhotoForm


@admin.register(PersonGroup)
class PersonGroupAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ['name']
    actions = ['train']

    def train(self, request, queryset):
        for group in queryset:
            res = CF.person_group.train(group.name)
            while True:
                res = CF.person_group.get_status(group.name)
                if res['status'] != 'running':
                    break
                time.sleep(1)
        self.message_user(request, 'Train 완료')
    train.short_description = '학습시키기'


class PhotoInline(admin.StackedInline):
    model = Photo
    form = PhotoForm
    list_display = ['person', 'is_valid', 'persisted_face_id', 'file', 'props', 'updated_at']
    list_filter = ['person__name', 'is_valid', 'updated_at']


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    form = PersonForm
    list_display = ['group', 'name', 'person_id', 'updated_at']
    list_display_links = ['name']
    list_filter = ['group__name', 'updated_at']
    inlines = [PhotoInline]


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    form = PhotoForm
    list_display = ['person', 'is_valid', 'persisted_face_id', 'file', 'emotion', 'updated_at']
    list_filter = ['person__name', 'is_valid', 'updated_at']
    actions = ['enroll', 'detect']

    def enroll(self, request, queryset):
        for photo in queryset:
            photo.enroll()
        self.message_user(request, 'Enroll 완료')

    def detect(self, request, queryset):
        for photo in queryset:
            photo.detect()
        self.message_user(request, 'Detect 완료')

