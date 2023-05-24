from django.test import TestCase
from coreapp.models import Report, Source, ReductionStrategy, ReductionModification
# from django.test import tag

class ReportModelTest(TestCase):

    def test_year_emission_report(self):
        # No source
        report = Report.objects.create(name='Report 1')
        self.assertEqual(report.year_emission(2020),0)

        # One source
        Source.objects.create(report=report, value=1, emission_factor=10)
        self.assertEqual(report.year_emission(2020),10)

        # Two sources
        Source.objects.create(report=report, value=1, emission_factor=10)
        self.assertEqual(report.year_emission(2020),20)
        

class SourceModelTest(TestCase):

    def test_year_emission_source(self):
        # Setup data
        report = Report.objects.create(name='Report 1')
        source_test_cases = [
            [ # After acquisition_year
                Source.objects.create(report=report,
                                      value=1, 
                                      emission_factor=8,
                                      acquisition_year=2000),
                2020,
                8
            ],
            [ # Before acquisition_year
                Source.objects.create(report=report,
                                      value=1, 
                                      emission_factor=8,
                                      acquisition_year=2000),
                1999,
                0
            ],
            [ # Before lifetime
                Source.objects.create(report=report,
                                      value=1, 
                                      emission_factor=8,
                                      lifetime=5,
                                      acquisition_year=2000),
                1999,
                0
            ],
            [ # During lifetime
                Source.objects.create(report=report,
                                      value=1, 
                                      emission_factor=10,
                                      lifetime=5,
                                      acquisition_year=2000),
                2004,
                2
            ],
            [ # After lifetime
                Source.objects.create(report=report,
                                      value=1, 
                                      emission_factor=10,
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
        source1 = Source.objects.create(report=report, value=10, emission_factor=10)
        source2 = Source.objects.create(report=report, value=10, emission_factor=10)

        # Strategy without data
        strategy = ReductionStrategy.objects.create(report=report)
        self.assertEqual(strategy.year_delta_emission(2020),0)

        # One ReductionStrategy
        ReductionModification.objects.create(strategy=strategy, source=source1, emission_factor_change=5,modification_start_year=2020)
        self.assertEqual(strategy.year_delta_emission(2020),50)

        # Two ReductionStrategies
        ReductionModification.objects.create(strategy=strategy, source=source2, emission_factor_change=5,modification_start_year=2020)
        self.assertEqual(strategy.year_delta_emission(2020),100)

        # Two ReductionStrategies and one Source
        Source.objects.create(strategy=strategy, value=10, emission_factor=10)
        self.assertEqual(strategy.year_delta_emission(2020),0)


class ReductionModificationModelTest(TestCase):

    def test_year_delta_emission_modification(self):
        report = Report.objects.create(name='Report 1')
        strategy = ReductionStrategy.objects.create(report=report)

        # emission_factor_change
        source = Source.objects.create(report=report, value=10, emission_factor=10)
        ReductionModification.objects.create(strategy=strategy, 
                                            source=source, 
                                            emission_factor_change=5,
                                            modification_start_year=2020)
        self.assertEqual(source.year_delta_emission(2020),50)

        # value_modification
        source = Source.objects.create(report=report, value=10, emission_factor=10)
        ReductionModification.objects.create(strategy=strategy, source=source, value_modification=-5,modification_start_year=2020)
        self.assertEqual(source.year_delta_emission(2020),100-((10-5)*10))

        # value_modification and emission_factor_change
        source = Source.objects.create(report=report, value=10, emission_factor=10)
        ReductionModification.objects.create(strategy=strategy, 
                                            source=source, 
                                            value_modification=-5, 
                                            emission_factor_change=5,
                                            modification_start_year=2020)
        self.assertEqual(source.year_delta_emission(2020),100-((10-5)*5))

        # lifetime
        source = Source.objects.create(report=report,
                                      value=10, 
                                      emission_factor=10,
                                      lifetime=5,
                                      acquisition_year=2000)
        ReductionModification.objects.create(strategy=strategy, source=source, value_modification=-5,modification_start_year=2000)
        self.assertEqual(source.year_delta_emission(1999),0)
        self.assertEqual(source.year_delta_emission(2002),100/5-((10-5)*10/5))
        self.assertEqual(source.year_delta_emission(2020),0)

        # modification after source lifetime, negative value
        source = Source.objects.create(report=report,
                                      value=10, 
                                      emission_factor=10,
                                      lifetime=5,
                                      acquisition_year=2000)
        ReductionModification.objects.create(strategy=strategy, source=source, value_modification=-5,modification_start_year=2020)
        self.assertEqual(source.year_delta_emission(2019),0)
        self.assertEqual(source.year_delta_emission(2020),0)
        self.assertEqual(source.year_delta_emission(2030),0)

        # modification after source lifetime, increase value
        source = Source.objects.create(report=report,
                                      value=10, 
                                      emission_factor=10,
                                      lifetime=5,
                                      acquisition_year=2000)
        ReductionModification.objects.create(strategy=strategy, source=source, value_modification=5,modification_start_year=2020)
        self.assertEqual(source.year_delta_emission(2019),0)
        self.assertEqual(source.year_delta_emission(2020),0-(5)*10/5)
        self.assertEqual(source.year_delta_emission(2030),0)


    def test_multiple_modification_order(self):
        report = Report.objects.create(name='Report 1')
        strategy = ReductionStrategy.objects.create(report=report)

        # first modification
        source = Source.objects.create(report=report, value=10, emission_factor=10)
        modification = ReductionModification.objects.create(strategy=strategy, 
                                                            source=source, 
                                                            emission_factor_change=5,
                                                            modification_start_year=2020)
        self.assertEqual(modification.order,0)

        # second modification
        modification = ReductionModification.objects.create(strategy=strategy, source=source, value_modification=-5,modification_start_year=2020)
        self.assertEqual(modification.order,1)

        # other source
        source = Source.objects.create(report=report, value=10, emission_factor=10)
        modification = ReductionModification.objects.create(strategy=strategy, source=source, 
                                                            value_modification=0.2, 
                                                            emission_factor_change=5,
                                                            modification_start_year=2020)
        self.assertEqual(modification.order,0)

        # same source, other strategy
        strategy2 = ReductionStrategy.objects.create(report=report)
        modification = ReductionModification.objects.create(strategy=strategy2, source=source, 
                                                            value_modification=-5, 
                                                            emission_factor_change=5,
                                                            modification_start_year=2020)
        self.assertEqual(modification.order,0)

