from coreapp.models import Report, Source
from coreapp.serializers import ReportSerializer, SourceSerializer
from rest_framework import permissions
from rest_framework import viewsets

class ReportViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    
    For more details on how accounts are activated please [see here][ref].

    [ref]: http://example.com/activating-accounts
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]


class SourceViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    serializer_class = SourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        report_id = self.kwargs['report_pk']
        return Source.objects.filter(report_id=report_id)