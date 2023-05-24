from django.db import models
from django.db.models import Q
from django.db.models.constraints import CheckConstraint
from django.core.exceptions import ValidationError

class Report(models.Model):
    """
    The Report is the sum of all the emissions. It should be done once a year
    """
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
    def year_emission(self, year: int) -> float:
        sources_sum = sum(source.year_emission(year) 
                          for source in self.sources.all())
        return sources_sum
    
    class Meta:
        ordering = ['id']

class ReductionStrategy(models.Model):
    """
    A ReductionStrategy is the set of all reduction modifications imagined for a given report
    """
    name = models.CharField(max_length=200)
    report = models.ForeignKey(Report, related_name='reductionStrategies', on_delete=models.CASCADE)

    def __str__(self):
        return  f'Report {self.report.id}: {self.name}'
    
    def year_delta_emission(self, year: int) -> float:
        """
        Delta = (Total GCG without strategy) - (Total GCG with strategy)
        Positive value -> diminution of GHG generation
        """
        # sum of the modifications
        total_delta = sum(source.year_delta_emission(year) 
                          for source in self.report.sources.all())

        # sum of the new sources
        total_new_sources = sum(source.year_emission(year) 
                                for source in self.sourcesStrategy.all())
        
        return total_delta - total_new_sources
    
    class Meta:
        ordering = ['id']
        


class Source(models.Model):
    """
    An Emission is every source that generates GreenHouse gases (GHG).
    It could be defined as value x emission_factor = total_emission
    """
    report = models.ForeignKey(Report, related_name='sources', on_delete=models.CASCADE, blank=True, null=True)
    strategy = models.ForeignKey(ReductionStrategy, related_name='sourcesStrategy', on_delete=models.CASCADE, blank=True, null=True)
    description = models.CharField(max_length=250, blank=True, null=True)
    value = models.FloatField()
    emission_factor = models.FloatField()
    lifetime = models.PositiveIntegerField(blank=True, null=True)
    acquisition_year = models.PositiveSmallIntegerField(blank=True,null=True)

    def total_emission(self) -> float:
        """
        Unit in kg
        """
        return self.emission_factor*self.value

    def year_emission(self, year: int) -> float:
        if self.acquisition_year and self.acquisition_year > year : 
            return 0 # source doesn't exist at this time
        if self.lifetime and self.acquisition_year + self.lifetime < year:
            return 0 # already amortized
        
        emission = self.total_emission()
        if self.lifetime:
            emission = emission / self.lifetime
        
        return emission
    
    def year_delta_emission(self, year: int) -> float:
        """
        Rules to calculate the delta:
        * the value changes are added together if it is during the lifetime of the change 
        * the emission factor = the last emission factor set
        * Positive value when modifications reduce emissions
        * Cannot have a positive value if the initial source is already amortized (it makes no sense to "improve" something that is already zero)
        """
        if self.acquisition_year and self.acquisition_year > year : 
            return 0 # source doesn't exist at this time
        
        cumul_value = self.value
        if self.lifetime and self.acquisition_year + self.lifetime < year:
            cumul_value = 0 # already amortized
        cumul_emission_factor = self.emission_factor
        
        for emission in self.sourceModifications.filter(modification_start_year__lte=year).order_by('order'):
            if emission.emission_factor_change:
                cumul_emission_factor = emission.emission_factor_change
            
            if self.lifetime and emission.modification_start_year + self.lifetime < year:
                break # already amortized         
            if emission.value_modification:
                cumul_value += emission.value_modification


        total_emission = self.year_emission(year)

        emission_modified = max(cumul_emission_factor * cumul_value,0)
        if self.lifetime:
            emission_modified = emission_modified / self.lifetime
        
        return total_emission - emission_modified

    
    def __str__(self):
        return self.description
    
    class Meta:
        ordering = ['id']
        constraints = [
            CheckConstraint(
                check=~(Q(report__isnull=True) & Q(strategy__isnull=True)),
                name='rep_or_strat_not_empty'
            ),
            CheckConstraint(
                check=Q(lifetime__isnull=True) | Q(acquisition_year__isnull=False),
                name='if_lifetime_not_empty_acquisition_year_not_empty'
            )
        ]
    

class ReductionModification(models.Model):
    """
    A ReductionModification is a modification of a source.
    Can be a change of emission_factor with the emission_factor_change parameter or
    a ratio apply to value, the new value = source.value*value_modification
    """
    strategy = models.ForeignKey(ReductionStrategy, related_name='modifications', 
                                 on_delete=models.CASCADE)
    source = models.ForeignKey(Source, related_name='sourceModifications', on_delete=models.CASCADE)
    description = models.CharField(max_length=250, blank=True, null=True)
    value_modification = models.FloatField(blank=True, null=True)
    emission_factor_change = models.FloatField(blank=True, null=True)
    order = models.PositiveSmallIntegerField()
    modification_start_year = models.PositiveSmallIntegerField()
    
    def __str__(self):
        return self.description
    
    def clean(self):
        super().clean()
        
        # Validate the date is greater than the already existing modifications with the same source and strategy
        last_modification = ReductionModification.objects.filter(
            source=self.source,
            strategy=self.strategy
        ).order_by('-order').first()

        if last_modification and self.modification_start_year < last_modification.modification_start_year:
            raise ValidationError(
                'modification_start_year must be greater than or equal to existing modification_start_year.'
            )
        
        # Validate the date is greater than his source acquisition_year
        if self.source.acquisition_year and self.modification_start_year < self.source.acquisition_year:
            raise ValidationError(
                'modification_start_year must be greater than or equal to source.acquisition_year'
            )
    
    def save(self, *args, **kwargs):
        self.clean()
        if not self.order:
            self.order = self.get_next_order()
        super().save(*args, **kwargs)

    def get_next_order(self):
        max_order = self.source.sourceModifications.filter(strategy_id=self.strategy_id).aggregate(models.Max('order'))['order__max']
        if max_order is None:
            return 0
        return max_order + 1
    class Meta:
        ordering = ['id']