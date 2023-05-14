from django.db import models

class Report(models.Model):
    """
    The Report is the sum of all the emissions. It should be done once a year
    """
    name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name
    
    def year_emission(self, year: int) -> float|None:
        source_list = list(source.year_emission(year) 
                for source in self.sources.all() 
                if source.total_emission is not None)
        if len(source_list) == 0:
            return None
        return sum(source_list)

class ReductionStrategy(models.Model):
    """
    A ReductionStrategy is the set of all reduction modifications imagined for a given report
    """
    name = models.CharField(max_length=200, blank=True, null=True)
    report = models.ForeignKey(Report, related_name='reductionStrategies', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return  f'Report {self.report.id}: {self.name}'
    
    def year_delta_emission(self, year: int) -> float|None:
        """
        Delta = (Total GCG without strategy) - (Total GCG with strategy)
        Positive value -> diminution of GHG generation
        """
        emission_list = list(emission.year_delta_emission(year) 
                for emission in self.modifications.all() 
                if emission.year_delta_emission(year) is not None)
        total_delta = sum(emission_list)

        source_list = list(source.year_emission(year) 
                for source in self.sourcesStrategy.all() 
                if source.total_emission is not None)
        total_new_sources = sum(source_list)
    
        if len(emission_list)==0 and len(source_list)==0:
            return None
        
        return total_delta - total_new_sources
        


class Source(models.Model):
    """
    An Emission is every source that generates GreenHouse gases (GHG).
    It could be defined as value x emission_factor = total
    """
    report = models.ForeignKey(Report, related_name='sources', on_delete=models.CASCADE, blank=True, null=True)
    strategy = models.ForeignKey(ReductionStrategy, related_name='sourcesStrategy', on_delete=models.CASCADE, blank=True, null=True)
    description = models.CharField(max_length=250, blank=True, null=True)
    value = models.FloatField(blank=True, null=True)
    emission_factor = models.FloatField(blank=True, null=True)
    total_emission = models.FloatField(blank=True, null=True, help_text="Unit in kg")
    lifetime = models.PositiveIntegerField(blank=True, null=True)
    acquisition_year = models.PositiveSmallIntegerField(blank=True,null=True)

    def year_emission(self, year: int) -> float|None:
        if self.total_emission is None :
            return None # Model allow empty total_emission
        if self.acquisition_year is not None and self.acquisition_year > year : 
            return 0 # source doesn't exist at this time
        if (self.lifetime is not None 
            and self.acquisition_year is not None
            and self.acquisition_year + self.lifetime < year):
            return 0 # already amortized
        
        emission = self.total_emission
        if self.lifetime is not None:
            emission = emission / self.lifetime
        
        return emission
    
    def __str__(self):
        return self.description
    

class ReductionModification(models.Model):
    """
    A ReductionModification is a modification of a source.
    Can be a change of emission_factor with the emission_factor_change parameter or
    a ratio apply to value, the new value = source.value*value_ratio
    """
    strategy = models.ForeignKey(ReductionStrategy, related_name='modifications', 
                                 on_delete=models.CASCADE, blank=True, null=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, blank=True, null=True)
    description = models.CharField(max_length=250, blank=True, null=True)
    value_ratio = models.FloatField(blank=True, null=True)
    emission_factor_change = models.FloatField(blank=True, null=True)
    
    def __str__(self):
        return self.description
    
    def year_delta_emission(self, year: int) -> float|None:
        total_emission = self.source.year_emission(year)
        # Model allow empty total_emission and source can be inactive this year
        if total_emission is None or self.source.emission_factor is None or self.source.value is None :
            return None
        # Source can be inactive this year
        if total_emission == 0 :
            return 0.0
        
        emission_factor_modified = self.source.emission_factor
        value_modified = self.source.value

        if self.emission_factor_change is not None:
            emission_factor_modified = self.emission_factor_change 
        
        if self.value_ratio is not None:
            value_modified = value_modified * self.value_ratio
        
        emission_modified = emission_factor_modified * value_modified
        if self.source.lifetime is not None:
            emission_modified = emission_modified / self.source.lifetime
        
        return total_emission - emission_modified