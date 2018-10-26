from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from rest_framework import serializers
from .models import Publisher, Book
from shop.models import Shop, Sale


class ListPublisherSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        fields = ('id', 'name', 'url')
        model = Publisher


class BookSerializer(serializers.ModelSerializer):
    copies_in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ('id', 'title', 'copies_in_stock')

    def get_copies_in_stock(self, obj):
        return obj.stock_set.filter(shop=self.context.get('shop'))[0].count


class PublisherShopsSerializer(serializers.ModelSerializer):
    books_in_stock = serializers.SerializerMethodField()
    books_sold_count = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = ('id', 'name', 'books_sold_count', 'books_in_stock')

    def get_books_in_stock(self, obj):
        serializer = BookSerializer(
            obj.books.filter(
                stock__count__gt=0,
                stock__book__publisher=self.context.get('publisher_pk')
            ),
            many=True,
            read_only=True,
            context={'shop': obj.pk}
        )
        return serializer.data

    def get_books_sold_count(self, obj):
        return Sale.objects.filter(
            stock__book__publisher=self.context.get('publisher_pk'),
            stock__shop=obj.pk
        ).aggregate(count=Coalesce(Sum('count'), 0)).get('count')


class RetrievePublisherSerializer(serializers.ModelSerializer):
    shops = serializers.SerializerMethodField()

    class Meta:
        model = Publisher
        fields = ('shops',)

    @staticmethod
    def get_shops(obj):
        #  shops which selling now or already sold at least one book of that publisher
        shops = Shop.objects.filter(
            stock__in=Stock.objects.filter(
                Q(book__publisher=obj.pk) & (
                    Q(count__gt=0) | Q(sale__count__gt=0)
                )
            )
        ).annotate(
            sale_count=Sum(F('stock__sale__count'))
        ).order_by('-sale_count')

        serializer = PublisherShopsSerializer(shops, many=True, context={'publisher_pk': obj.pk})
        return serializer.data
