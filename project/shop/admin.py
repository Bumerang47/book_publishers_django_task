from django.contrib import admin
from .models import Shop, Sale, Stock


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('shop_name', 'book_title', 'count',)

    @staticmethod
    def shop_name(obj):
        return obj.shop.name

    @staticmethod
    def book_title(obj):
        return obj.book.title


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('stock_shop_name', 'stock_book_title', 'date_sale',)

    @staticmethod
    def stock_shop_name(obj):
        return obj.stock.shop.name

    @staticmethod
    def stock_book_title(obj):
        return obj.stock.book.title
