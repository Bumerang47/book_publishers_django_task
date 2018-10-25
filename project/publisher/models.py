from django.db import models


class Publisher(models.Model):
    name = models.CharField('Publisher name', max_length=255)

    def __str__(self):
        return '%s (pk-%s)' % (self.name, self.pk)


class Book(models.Model):
    title = models.CharField('Title', max_length=255)
    publisher = models.ForeignKey('Publisher', on_delete=models.DO_NOTHING, related_name='books')

    def __str__(self):
        return '%s (pk-%s)' % (self.title, self.pk)
