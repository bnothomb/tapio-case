from coreapp.models import Report, Source
from coreapp.serializers import ReportSerializer, SourceSerializer
from rest_framework import permissions
from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

@extend_schema(
    description='Computed value based on the year.',
    parameters=[
        OpenApiParameter(
            name='year',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='The year for the computation.',
            required=False
        )
    ]
)
class ReportViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    
    For more details on how accounts are activated please [see here][ref].

    [ref]: http://example.com/activating-accounts
    """
    queryset = Report.objects.all().order_by('id')
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(
    description='Computed value based on the year.',
    parameters=[
        OpenApiParameter(
            name='year',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='The year for the computation.',
            required=False
        )
    ]
)
class SourceViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    serializer_class = SourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        report_id = self.kwargs['report_id']
        return Source.objects.filter(report_id=report_id).order_by('id')