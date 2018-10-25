from django.db import models
from publisher.models import Book
from .exceptions import StockCountException


class Shop(models.Model):
    name = models.CharField('Shop name', max_length=255)
    books = models.ManyToManyField(Book, through='Stock', related_name='shops')

    def __str__(self):
        return '%s (pk-%s)' % (self.name, self.pk)


class Stock(models.Model):
    class Meta:
        unique_together = ('shop', 'book')

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    count = models.PositiveIntegerField('Количество')

    def __str__(self):
        return '%s-%s, %s' % (self.shop.name, self.book.title, self.count)


class Sale(models.Model):
    price = models.DecimalField('Price', max_digits=7, decimal_places=2)
    date_sale = models.DateTimeField('Sale data', auto_now_add=True)
    count = models.IntegerField('Count')
    stock = models.ForeignKey(Stock, on_delete=models.DO_NOTHING)

    def save(self, *args, **kwargs):
        if self.pk is None:
            if self.stock.count == 0:
                raise StockCountException('The amount of stock is zero')

            self.stock.count -= self.count
            if self.stock.count < 0:
                raise StockCountException('There are not enough items in stock.')

            self.stock.save()
        super(Sale, self).save(*args, **kwargs)

    def __str__(self):
        return '%s-%s, %s (%s)' % (self.stock.shop.name, self.stock.book.title, self.price, self.date_sale)
