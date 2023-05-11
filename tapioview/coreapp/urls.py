from django.urls import path, include
from rest_framework.routers import DefaultRouter
from coreapp import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'reports', views.ReportViewSet,basename="report")
router.register(r'reports/(?P<report_pk>\d+)/sources', views.SourceViewSet, basename='source')


# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]