from django.contrib import admin
from django import forms
from .models import Publisher, Book


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'pk')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'publisher', 'pk')


class PublisherForm(forms.ModelForm):

    class Meta:
        model = Publisher
        fields = ['name']


class BookForm(forms.ModelForm):

    class Meta:
        model = Book
        fields = ['title', 'publisher']
