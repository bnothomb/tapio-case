from django.contrib.auth.models import User
from django.test import TestCase
from coreapp.models import Report, Source, ReductionStrategy, ReductionModification
from rest_framework.test import APIClient
from rest_framework import status
# from django.test import tag


class ReportViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Setup data
        self.report = Report.objects.create(name='Report 1')
        self.source1 = Source.objects.create(report=self.report, description='Source 1')
        self.source2 = Source.objects.create(report=self.report, description='Source 2')

    def tearDown(self):
        # Wipe the database after each test
        Report.objects.all().delete()
        Source.objects.all().delete()
        User.objects.all().delete()

    def test_permissions_report(self):
        # Test can't access without permissions
        response = self.client.get('/reports/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(f'/reports/{self.report.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        

class SourceViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Setup data
        self.report = Report.objects.create(name='Report 1')
        self.source1 = Source.objects.create(report=self.report, description='Source 1')
        self.source2 = Source.objects.create(report=self.report, description='Source 2')
        self.strategy = ReductionStrategy.objects.create(name='Strategy 1', report=self.report)
        self.source3 = Source.objects.create(strategy=self.strategy, description='Source 3')

    def tearDown(self):
        # Wipe the database after each test
        Source.objects.all().delete()
        ReductionStrategy.objects.all().delete()
        Report.objects.all().delete()
        User.objects.all().delete()

    def test_permissions_source(self):
        # Test can't access without permissions
        response = self.client.get(f'/reports/{self.report.pk}/sources/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(f'/reports/{self.report.pk}/sources/{self.source1.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(f'/reports/{self.report.pk}/reductionStrategies/{self.strategy.pk}/sources/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(f'/reports/{self.report.pk}/reductionStrategies/{self.strategy.pk}/sources/{self.source3.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        

class ReductionStrategyViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Setup data
        self.report = Report.objects.create(name='Report 1')
        self.source = Source.objects.create(report=self.report, description='Source 1')
        self.strategy = ReductionStrategy.objects.create(name='Strategy 1', report=self.report)
        self.modification = ReductionModification.objects.create(strategy=self.strategy,
                                                                 source=self.source,
                                                                 description='Modification 1')

    def tearDown(self):
        # Wipe the database after each test
        ReductionModification.objects.all().delete()
        Source.objects.all().delete()
        ReductionStrategy.objects.all().delete()
        Report.objects.all().delete()
        User.objects.all().delete()

    def test_permissions_strategy(self):
        # Test can't access without permissions
        response = self.client.get(f'/reports/{self.report.pk}/reductionStrategies/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(f'/reports/{self.report.pk}/reductionStrategies/{self.strategy.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ReductionModificationViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Setup data
        self.report = Report.objects.create(name='Report 1')
        self.source = Source.objects.create(report=self.report, description='Source 1')
        self.strategy = ReductionStrategy.objects.create(name='Strategy 1', report=self.report)
        self.modification = ReductionModification.objects.create(strategy=self.strategy,
                                                                 source=self.source,
                                                                 description='Modification 1')

    def tearDown(self):
        # Wipe the database after each test
        ReductionModification.objects.all().delete()
        Source.objects.all().delete()
        ReductionStrategy.objects.all().delete()
        Report.objects.all().delete()
        User.objects.all().delete()

    def test_permissions_modification(self):
        # Test can't access without permissions
        response = self.client.get(f'/reports/{self.report.pk}/reductionStrategies/{self.strategy.pk}/modifications/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(f'/reports/{self.report.pk}/reductionStrategies/{self.strategy.pk}/modifications/{self.modification.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


