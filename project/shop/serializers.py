from django.db.models.functions import Coalesce
from django.db.models import Sum
from rest_framework import serializers
from .models import Shop
from publisher.serializers import BookSerializer
from publisher.models import Book


class BookInShopSerializer(BookSerializer):
    copies_sold_count = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ('id', 'title', 'copies_in_stock', 'copies_sold_count')

    def get_copies_sold_count(self, obj):
        return obj.stock_set.filter(
            shop=self.context.get('shop')
        ).aggregate(
            count=Coalesce(Sum('sale__count'), 0)
        ).get('count')


class RetrieveShopSerializer(serializers.ModelSerializer):
    books_in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = ('id', 'name', 'books_in_stock')

    @staticmethod
    def get_books_in_stock(obj):
        serializer = BookInShopSerializer(
            obj.books,
            many=True,
            read_only=True,
            context={'shop': obj.pk}
        )
        return serializer.data


class ShopListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        fields = ('id', 'name', 'url')
        model = Shop
