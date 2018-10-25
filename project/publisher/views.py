from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .serializers import ListPublisherSerializer, RetrievePublisherSerializer
from .models import Publisher


class PublisherViewSet(viewsets.ViewSet):
    queryset = Publisher.objects.all()

    def list(self, request):
        serializer = ListPublisherSerializer(self.queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        publisher = get_object_or_404(self.queryset, pk=pk)
        serializer = RetrievePublisherSerializer(publisher)
        return Response(serializer.data)
