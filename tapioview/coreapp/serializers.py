from rest_framework import serializers
from coreapp.models import Report, Source


class SourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Source
        fields = ['id',
                  'description',
                  'value',
                  'emission_factor',
                  'total_emission',
                  'lifetime',
                  'acquisition_year',
                  'report']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Perform any necessary modification to the total_emission field value here
        year = self.context['request'].query_params.get('year')
        if year is not None:
            try:
                year = int(year)
                representation['total_emission'] = instance.year_emission(year)
            except ValueError:
                # Handle the case when the 'year' value is not a valid integer
                pass
        return representation
        

class ReportSerializer(serializers.ModelSerializer):
    sources = SourceSerializer(
        many=True,
        read_only=True,
    )

    total_emission = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ['id','name','total_emission','sources']
    

    def get_total_emission(self, obj):
        year = self.context['request'].query_params.get('year')
        total_emission = None
        if year is None:
            return None
        try:
            year = int(year)
            total_emission = sum(source.year_emission(year) 
                                for source in obj.sources.all() 
                                if source.total_emission is not None)
        except ValueError:
                # Handle the case when the 'year' value is not a valid integer
                pass
        return total_emission