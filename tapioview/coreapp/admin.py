from django.contrib import admin

from .models import Report, Source

class SourceInline(admin.TabularInline):
    model = Source
    extra = 0

class ReportAdmin(admin.ModelAdmin):
    inlines = [SourceInline]

admin.site.register(Report, ReportAdmin)
admin.site.register(Source)