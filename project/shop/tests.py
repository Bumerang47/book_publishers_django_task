from django.test import TestCase
from rest_framework.test import APIRequestFactory
from .views import ShopViewSet
from .models import Sale, Stock, Shop
from .exceptions import StockCountException


class PersonProfileTestClass(TestCase):
    fixtures = ['tests_data']

    def test_list_shop(self):
        factory = APIRequestFactory()
        wsgi = factory.get('/api/shop')
        list_view = ShopViewSet.as_view({'get': 'list'})
        response = list_view(wsgi)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Shop.objects.count())

    def test_sales_proceses(self):
        factory = APIRequestFactory()
        wsgi = factory.get('/api/publisher/1/')
        item_view = ShopViewSet.as_view({'get': 'retrieve'})
        response = item_view(wsgi, pk='1')
        self.assertEqual(response.status_code, 200)
        book_in_stack = 2

        begin_shop = response.data
        begin_book = response.data.get('books_in_stock')[book_in_stack]

        # create new sale
        stock = Stock.objects.get(shop__id=begin_shop.get('id'), book__id=begin_book.get('id'))
        amount_sale = 2
        sale = Sale(price=0.1, stock=stock,  count=amount_sale)

        # shortage exception
        self.assertRaises(StockCountException, sale.save)

        # incremented and updated stock request
        stock.count += amount_sale
        stock.save()
        response = item_view(wsgi, pk='1')
        behind_stock = response.data.get('books_in_stock')[book_in_stack].get('copies_in_stock')

        sale.save()
        response = item_view(wsgi, pk='1')

        self.assertEqual(
            response.data.get('books_in_stock')[book_in_stack].get('copies_sold_count') -
            begin_shop.get('books_in_stock')[book_in_stack].get('copies_sold_count'),
            amount_sale
        )

        self.assertEqual(
            behind_stock -
            begin_shop.get('books_in_stock')[book_in_stack].get('copies_in_stock'),
            amount_sale
        )
