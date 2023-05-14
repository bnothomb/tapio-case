from django.contrib import admin

from .models import Report, Source, ReductionStrategy, ReductionModification

class SourceInline(admin.TabularInline):
    model = Source
    extra = 0

class ReductionStrategyInline(admin.TabularInline):
    model = ReductionStrategy
    extra = 0

class ReductionModificationInline(admin.TabularInline):
    model = ReductionModification
    extra = 0

class ReportAdmin(admin.ModelAdmin):
    inlines = [SourceInline, ReductionStrategyInline]

class ReductionStrategyAdmin(admin.ModelAdmin):
    inlines = [SourceInline, ReductionModificationInline]

admin.site.register(Report, ReportAdmin)
admin.site.register(Source)
admin.site.register(ReductionStrategy, ReductionStrategyAdmin)
admin.site.register(ReductionModification)