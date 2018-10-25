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

        # test of ordering
        first_shop = response.data.get('shops')[0]

        shop_list = list(response.data.get('shops'))
        shop_list.sort(key=lambda s: s.get('books_sold_count'), reverse=True)
        self.assertEqual(shop_list[0].get('id'), first_shop.get('id'))
        self.assertEqual(len(shop_list[0].get('books_in_stock')), 2)

        # availability of books sold
        wsgi = factory.get('/api/publisher/2/')

        response = item_view(wsgi, pk='2')
        shop = response.data.get('shops')[0]
        book = shop.get('books_in_stock')[0]

        # create new sale
        stock = Stock.objects.get(shop__id=shop.get('id'), book__id=book.get('id'))
        sale = Sale(price=0.1, stock=stock,  count=book.get('copies_in_stock'))
        sale.save()

        response = item_view(wsgi, pk='2')
        self.assertLess(
            shop.get('books_sold_count'),
            response.data.get('shops')[0].get('books_sold_count')
        )
        self.assertEqual(response.data.get('shops')[0].get('books_in_stock'), [])
