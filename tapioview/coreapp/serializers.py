from rest_framework import serializers
from coreapp.models import Report, Source


class SourceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Source
        fields = '__all__'
        # fields = ['id',
        #           'description', 
        #           'value', 
        #           'emission_factor',
        #           'total_emission',
        #           'lifetime',
        #           'acquisition_year']
        

class ReportSerializer(serializers.ModelSerializer):
    sources = SourceSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Report
        fields = ['id','name','sources']