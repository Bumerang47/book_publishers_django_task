from django.contrib import admin
from django.urls import path
from publisher.views import PublisherViewSet
from shop.views import ShopViewSet
from rest_framework import routers
from django.conf.urls import url, include

router = routers.DefaultRouter()
router.register(r'publisher', PublisherViewSet)
router.register(r'shop', ShopViewSet)

urlpatterns = [

    url(r'^api/', include(router.urls)),
    path('admin/', admin.site.urls),
]
