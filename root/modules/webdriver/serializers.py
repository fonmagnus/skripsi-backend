from rest_framework import serializers
from .models import CrawlRequest


class CrawlRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrawlRequest
        fields = '__all__'
