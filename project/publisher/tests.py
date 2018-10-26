from django.test import TestCase
from rest_framework.test import APIRequestFactory
from publisher.views import PublisherViewSet
from shop.models import Sale, Stock


class PersonProfileTestClass(TestCase):
    fixtures = ['tests_data']

    def test_list_publisher(self):
        factory = APIRequestFactory()
        wsgi = factory.get('/api/publisher')
        list_view = PublisherViewSet.as_view({'get': 'list'})
        response = list_view(wsgi)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_publisher(self):
        factory = APIRequestFactory()
        wsgi = factory.get('/api/publisher/1/')
        item_view = PublisherViewSet.as_view({'get': 'retrieve'})
        response = item_view(wsgi, pk='1')
        self.assertEqual(response.status_code, 200)
        shop_order = 0
        count_books_from_fixtures = 2

        # test of ordering
        first_shop = response.data.get('shops')[shop_order]

        shop_list = list(response.data.get('shops'))
        shop_list.sort(key=lambda s: s.get('books_sold_count'), reverse=True)
        self.assertEqual(shop_list[shop_order].get('id'), first_shop.get('id'))
        self.assertEqual(
            len(shop_list[shop_order].get('books_in_stock')),
            count_books_from_fixtures
        )

        # availability of books sold
        wsgi = factory.get('/api/publisher/2/')

        response = item_view(wsgi, pk='2')
        shop = response.data.get('shops')[shop_order]
        book = shop.get('books_in_stock')[shop_order]

        # create new sale
        stock = Stock.objects.get(shop__id=shop.get('id'), book__id=book.get('id'))
        sale = Sale(price=0.1, stock=stock,  count=book.get('copies_in_stock'))
        sale.save()

        response = item_view(wsgi, pk='2')
        self.assertLess(
            shop.get('books_sold_count'),
            response.data.get('shops')[shop_order].get('books_sold_count')
        )

        # empty stock and positive sold count
        self.assertEqual(response.data.get('shops')[shop_order].get('books_in_stock'), [])

    def test_stock_and_sold(self):
        factory = APIRequestFactory()
        wsgi = factory.get('/api/publisher/1/')
        item_view = PublisherViewSet.as_view({'get': 'retrieve'})
        response = item_view(wsgi, pk='1')

        shop_order = 1
        book_order = 0

        stock = Stock.objects.get(
            shop_id=response.data.get('shops')[shop_order].get('id'),
            book_id=response.data.get('shops')[shop_order].get('books_in_stock')[book_order].get('id')
        )
        stock.count = 0
        self.assertTrue(stock.sale_set.exists())
        stock.save()
        response = item_view(wsgi, pk='1')
        response_shop = response.data.get('shops')[shop_order]
        self.assertEqual(response_shop.get('id'), stock.shop.pk)
        self.assertFalse(response_shop.get('books_in_stock'))
        self.assertEqual(len(response_shop.get('books_in_stock')), stock.count)

        stock.count = 1
        stock.sale_set.all().delete()
        shop_order = 2  # shop change order of response because haven't sold
        stock.save()
        response = item_view(wsgi, pk='1')
        response_shop = response.data.get('shops')[shop_order]
        self.assertEqual(response_shop.get('id'), stock.shop.pk)
        self.assertGreater(len(response_shop.get('books_in_stock')), 0)
        self.assertEqual(len(response_shop.get('books_in_stock')), stock.count)

        stock.count = 0
        stock.save()
        response = item_view(wsgi, pk='1')
        self.assertFalse(
            [shop for shop in response.data.get('shops') if shop.get('id') == stock.shop.pk]
        )
