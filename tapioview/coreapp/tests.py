from django.contrib.auth.models import User
from django.test import TestCase

from .models import Report, Source
from rest_framework.test import APIClient
from rest_framework import status
# from django.test import tag
# from unittest import skip


class ReportViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Setup data
        self.report = Report.objects.create(name='Report 1')
        self.source1 = Source.objects.create(report=self.report, description='Source 1')
        self.source2 = Source.objects.create(report=self.report, description='Source 2')

        # Setup permissions
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def tearDown(self):
        # Wipe the database after each test
        Report.objects.all().delete()
        Source.objects.all().delete()
        User.objects.all().delete()

    def test_permissions(self):
        # Log out
        self.client.logout()
        # Test can't access without permissions
        response = self.client.get('/reports/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(f'/reports/{self.report.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_report_details(self):
        response = self.client.get(f'/reports/{self.report.pk}/')
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
        self.source1 = Source.objects.create(report=self.report, description='Source 1')
        self.source2 = Source.objects.create(report=self.report, description='Source 2')

        # Setup permissions
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def tearDown(self):
        # Wipe the database after each test
        Report.objects.all().delete()
        Source.objects.all().delete()
        User.objects.all().delete()

    def test_permissions(self):
        # Log out
        self.client.logout()
        # Test can't access without permissions
        response = self.client.get(f'/reports/{self.report.pk}/sources/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(f'/reports/{self.report.pk}/sources/{self.source1.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    

    def test_get_source_list(self):
        response = self.client.get(f'/reports/{self.report.pk}/sources/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        response = self.client.get(f'/reports/{self.report.pk}/sources/{self.source1.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(f'/reports/{self.report.pk}/sources/{self.source2.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)




class SourceModelTest(TestCase):

    def test_year_emission(self):
        # Setup data
        self.report = Report.objects.create(name='Report 1')
        source_test_cases = [
            [ # No total_emission
                Source.objects.create(report=self.report),
                2020, # expected year
                None #expected result for total_emission
            ],
            [ # Only total_emission
                Source.objects.create(report=self.report, 
                                      total_emission=8),
                2020,
                8
            ],
            [ # After acquisition_year
                Source.objects.create(report=self.report,
                                      total_emission=8,
                                      acquisition_year=2000),
                2020,
                8
            ],
            [ # Before acquisition_year
                Source.objects.create(report=self.report,
                                      total_emission=8,
                                      acquisition_year=2000),
                1999,
                0
            ],
            [ # Before lifetime
                Source.objects.create(report=self.report,
                                      total_emission=8,
                                      lifetime=5,
                                      acquisition_year=2000),
                1999,
                0
            ],
            [ # During lifetime
                Source.objects.create(report=self.report,
                                      total_emission=10,
                                      lifetime=5,
                                      acquisition_year=2000),
                2004,
                2
            ],
            [ # After lifetime
                Source.objects.create(report=self.report,
                                      total_emission=8,
                                      lifetime=5,
                                      acquisition_year=2000),
                2020,
                0
            ]
        ]

        for test_case in source_test_cases:
            self.assertEqual(test_case[0].year_emission(test_case[1]), test_case[2])

