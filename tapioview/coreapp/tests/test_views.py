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
        self.source1 = Source.objects.create(report=self.report, description='Source 1', value=1, emission_factor=10)
        self.source2 = Source.objects.create(report=self.report, description='Source 2', value=1, emission_factor=10)

        # Setup permissions
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def tearDown(self):
        # Wipe the database after each test
        Source.objects.all().delete()
        Report.objects.all().delete()
        User.objects.all().delete()

    def test_get_reports(self):
        response = self.client.get(f'/reports/{self.report.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(f'/reports/{self.report.pk}/?year=2020')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check report
        self.assertEqual(response.data['name'], self.report.name)
        # ...

        # Check source
        self.assertEqual(len(response.data['sources']), 2)
        self.assertEqual(response.data['sources'][0]['id'], self.source1.pk)
        self.assertEqual(response.data['sources'][1]['id'], self.source2.pk)
        
        

class SourceViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Setup data
        self.report = Report.objects.create(name='Report 1')
        self.source1 = Source.objects.create(report=self.report, description='Source 1', value=1, emission_factor=10)
        self.source2 = Source.objects.create(report=self.report, description='Source 2', value=1, emission_factor=10)
        self.strategy = ReductionStrategy.objects.create(name='Strategy 1', report=self.report)
        self.source3 = Source.objects.create(strategy=self.strategy, description='Source 3', value=1, emission_factor=10)

        # Setup permissions
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def tearDown(self):
        # Wipe the database after each test
        ReductionModification.objects.all().delete()
        Source.objects.all().delete()
        ReductionStrategy.objects.all().delete()
        Report.objects.all().delete()
        User.objects.all().delete()
    

    def test_get_sources(self):
        response = self.client.get(f'/reports/{self.report.pk}/sources/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        response = self.client.get(f'/reports/{self.report.pk}/sources/{self.source1.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(f'/reports/{self.report.pk}/sources/{self.source2.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(f'/reports/{self.report.pk}/sources/{self.source2.pk}/?year=2020')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(f'/reports/{self.report.pk}/reductionStrategies/{self.strategy.pk}/sources/{self.source3.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(f'/reports/{self.report.pk}/reductionStrategies/{self.strategy.pk}/sources/{self.source3.pk}/?year=2020')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

class ReductionStrategyViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Setup data
        self.report = Report.objects.create(name='Report 1')
        self.source = Source.objects.create(report=self.report, description='Source 1', value=1, emission_factor=10)
        self.strategy = ReductionStrategy.objects.create(name='Strategy 1', report=self.report)
        self.modification = ReductionModification.objects.create(strategy=self.strategy,
                                                                 source=self.source,
                                                                 description='Modification 1',
                                                                 modification_start_year=2020)

        # Setup permissions
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def tearDown(self):
        # Wipe the database after each test
        ReductionModification.objects.all().delete()
        Source.objects.all().delete()
        ReductionStrategy.objects.all().delete()
        Report.objects.all().delete()
        User.objects.all().delete()
    

    def test_get_strategies(self):
        response = self.client.get(f'/reports/{self.report.pk}/reductionStrategies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(f'/reports/{self.report.pk}/reductionStrategies/{self.strategy.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(f'/reports/{self.report.pk}/reductionStrategies/{self.strategy.pk}/?year=2020')
        self.assertEqual(response.status_code, status.HTTP_200_OK)



class ReductionModificationViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Setup data
        self.report = Report.objects.create(name='Report 1')
        self.source = Source.objects.create(report=self.report, description='Source 1', value=1, emission_factor=10)
        self.strategy = ReductionStrategy.objects.create(name='Strategy 1', report=self.report)
        self.modification = ReductionModification.objects.create(strategy=self.strategy,
                                                                 source=self.source,
                                                                 description='Modification 1',
                                                                 modification_start_year=2020)

        # Setup permissions
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def tearDown(self):
        # Wipe the database after each test
        ReductionModification.objects.all().delete()
        Source.objects.all().delete()
        ReductionStrategy.objects.all().delete()
        Report.objects.all().delete()
        User.objects.all().delete()
    

    def test_get_modifications(self):
        response = self.client.get(f'/reports/{self.report.pk}/reductionStrategies/{self.strategy.pk}/modifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        response = self.client.get(f'/reports/{self.report.pk}/reductionStrategies/{self.strategy.pk}/modifications/{self.modification.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(f'/reports/{self.report.pk}/reductionStrategies/{self.strategy.pk}/modifications/{self.modification.pk}/?year=2020')
        self.assertEqual(response.status_code, status.HTTP_200_OK)