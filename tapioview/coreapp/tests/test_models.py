from django.test import TestCase
from coreapp.models import Report, Source, ReductionStrategy, ReductionModification
# from django.test import tag

class ReportModelTest(TestCase):

    def test_year_emission_report(self):
        # No source
        report = Report.objects.create(name='Report 1')
        self.assertIsNone(report.year_emission(2020))

        # One source without value
        Source.objects.create(report=report)
        self.assertIsNone(report.year_emission(2020))

        # Two sources
        Source.objects.create(report=report, 
                                      total_emission=10)
        self.assertEqual(report.year_emission(2020),10)

        # Two sources with value
        Source.objects.create(report=report, 
                                      total_emission=10)
        self.assertEqual(report.year_emission(2020),20)
        

class SourceModelTest(TestCase):

    def test_year_emission_source(self):
        # Setup data
        report = Report.objects.create(name='Report 1')
        source_test_cases = [
            [ # No total_emission
                Source.objects.create(report=report),
                2020, # expected year
                None #expected result for total_emission
            ],
            [ # Only total_emission
                Source.objects.create(report=report, 
                                      total_emission=8),
                2020,
                8
            ],
            [ # After acquisition_year
                Source.objects.create(report=report,
                                      total_emission=8,
                                      acquisition_year=2000),
                2020,
                8
            ],
            [ # Before acquisition_year
                Source.objects.create(report=report,
                                      total_emission=8,
                                      acquisition_year=2000),
                1999,
                0
            ],
            [ # Before lifetime
                Source.objects.create(report=report,
                                      total_emission=8,
                                      lifetime=5,
                                      acquisition_year=2000),
                1999,
                0
            ],
            [ # During lifetime
                Source.objects.create(report=report,
                                      total_emission=10,
                                      lifetime=5,
                                      acquisition_year=2000),
                2004,
                2
            ],
            [ # After lifetime
                Source.objects.create(report=report,
                                      total_emission=8,
                                      lifetime=5,
                                      acquisition_year=2000),
                2020,
                0
            ]
        ]

        for test_case in source_test_cases:
            self.assertEqual(test_case[0].year_emission(test_case[1]), test_case[2])


class ReductionStrategyModelTest(TestCase):

    def test_year_delta_emission_strategy(self):
        report = Report.objects.create(name='Report 1')
        source1 = Source.objects.create(report=report, value=10, emission_factor=10,total_emission=100)
        source2 = Source.objects.create(report=report, value=10, emission_factor=10,total_emission=100)

        # Strategy without data
        strategy = ReductionStrategy.objects.create(report=report)
        self.assertIsNone(strategy.year_delta_emission(2020))

        # One ReductionStrategy
        ReductionModification.objects.create(strategy=strategy, source=source1, emission_factor_change=5)
        self.assertEqual(strategy.year_delta_emission(2020),50)

        # Two ReductionStrategies
        ReductionModification.objects.create(strategy=strategy, source=source2, emission_factor_change=5)
        self.assertEqual(strategy.year_delta_emission(2020),100)

        # Two ReductionStrategies and one Source
        Source.objects.create(strategy=strategy, value=10, emission_factor=10,total_emission=100)
        self.assertEqual(strategy.year_delta_emission(2020),0)


class ReductionModificationModelTest(TestCase):

    def test_year_delta_emission_modification(self):
        report = Report.objects.create(name='Report 1')
        strategy = ReductionStrategy.objects.create(report=report)

        # Source without enougth data
        source = Source.objects.create(report=report, value=10, emission_factor=10)
        modification = ReductionModification.objects.create(strategy=strategy, source=source, emission_factor_change=5)
        self.assertIsNone(modification.year_delta_emission(2020))

        source = Source.objects.create(report=report, value=10,total_emission=100)
        modification = ReductionModification.objects.create(strategy=strategy, source=source, emission_factor_change=5)
        self.assertIsNone(modification.year_delta_emission(2020))

        # emission_factor_change
        source = Source.objects.create(report=report, value=10, emission_factor=10,total_emission=100)
        modification = ReductionModification.objects.create(strategy=strategy, source=source, emission_factor_change=5)
        self.assertEqual(modification.year_delta_emission(2020),50)

        # value_ratio
        source = Source.objects.create(report=report, value=10, emission_factor=10,total_emission=100)
        modification = ReductionModification.objects.create(strategy=strategy, source=source, value_ratio=0.2)
        self.assertEqual(modification.year_delta_emission(2020),100-(10*0.2*10))

        # value_ratio and emission_factor_change
        source = Source.objects.create(report=report, value=10, emission_factor=10,total_emission=100)
        modification = ReductionModification.objects.create(strategy=strategy, source=source, 
                                                            value_ratio=0.2, 
                                                            emission_factor_change=5)
        self.assertEqual(modification.year_delta_emission(2020),100-(10*0.2*5))

        # lifetime
        source = Source.objects.create(report=report,
                                      value=10, 
                                      emission_factor=10,
                                      total_emission=100,
                                      lifetime=5,
                                      acquisition_year=2000)
        modification = ReductionModification.objects.create(strategy=strategy, source=source, value_ratio=0.2)
        self.assertEqual(modification.year_delta_emission(1999),0)
        self.assertEqual(modification.year_delta_emission(2002),100/5-(10*0.2*10/5))
        self.assertEqual(modification.year_delta_emission(2020),0)

