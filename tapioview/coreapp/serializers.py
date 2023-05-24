from rest_framework import serializers
from coreapp.models import Report, Source, ReductionStrategy, ReductionModification


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
        
    def to_representation(self, instance: Source):
        representation = super().to_representation(instance)
        # Perform any necessary modification to the total_emission field value here
        year_param:str|None = self.context['request'].query_params.get('year')
        if year_param:
            try:
                year = int(year_param)
                representation['total_emission'] = instance.year_emission(year)
            except ValueError:
                # Handle the case when the 'year' value is not a valid integer
                pass
        return representation
        

class ReductionModificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReductionModification
        fields = ['id',
                  'description',
                  'strategy',
                  'source',
                  'order',
                  'modification_start_year',
                  'value_modification',
                  'emission_factor_change']
        read_only_fields = ['order']

class ReductionStrategySerializer(serializers.ModelSerializer):
    sources = SourceSerializer(
        many=True,
        read_only=True,
    )
    modifications = ReductionModificationSerializer(
        many=True,
        read_only=True,
    )

    delta_total_emission = serializers.SerializerMethodField()

    class Meta:
        model = ReductionStrategy
        fields = ['id',
                  'report',
                  'name',
                  'delta_total_emission',
                  'sources',
                  'modifications']
    

    def get_delta_total_emission(self, obj: ReductionStrategy) -> float|None:
        year_param:str|None = self.context['request'].query_params.get('year')
        delta_total_emission:float|None = None
        if not year_param:
            return None # In the case where there is no year parameter, the calculation of the delta is meaningless
        try:
            year = int(year_param)
            delta_total_emission = obj.year_delta_emission(year)
        except ValueError:
            # Handle the case when the 'year' value is not a valid integer
            pass
        return delta_total_emission

class ReportSerializer(serializers.ModelSerializer):
    sources = SourceSerializer(
        many=True,
        read_only=True,
    )
    reductionStrategies = ReductionStrategySerializer(
        many=True,
        read_only=True,
    )

    total_emission = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ['id',
                  'name',
                  'total_emission',
                  'sources',
                  'reductionStrategies']
    

    def get_total_emission(self, obj: Report) -> float|None:
        year_param:str|None = self.context['request'].query_params.get('year')
        total_emission:float|None = None
        if not year_param:
            return None
        try:
            year = int(year_param)
            total_emission = obj.year_emission(year)
        except ValueError:
            # Handle the case when the 'year' value is not a valid integer
            pass
        return total_emission