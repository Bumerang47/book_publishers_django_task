from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .serializers import RetrieveShopSerializer, ShopListSerializer
from .models import Shop


class ShopViewSet(viewsets.ViewSet):
    queryset = Shop.objects.all()

    def list(self, request):
        serializer = ShopListSerializer(self.queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        shop = get_object_or_404(self.queryset, pk=pk)
        serializer = RetrieveShopSerializer(shop)
        return Response(serializer.data)
