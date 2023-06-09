# Generated by Django 4.2.1 on 2023-05-24 06:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0004_alter_source_strategy'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reductionmodification',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='reductionstrategy',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='report',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='source',
            options={'ordering': ['id']},
        ),
        migrations.RemoveField(
            model_name='source',
            name='total_emission',
        ),
        migrations.AddField(
            model_name='reductionmodification',
            name='order',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='reductionmodification',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sourceModifications', to='coreapp.source'),
        ),
        migrations.AlterField(
            model_name='reductionmodification',
            name='strategy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modifications', to='coreapp.reductionstrategy'),
        ),
        migrations.AlterField(
            model_name='reductionstrategy',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='reductionstrategy',
            name='report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reductionStrategies', to='coreapp.report'),
        ),
        migrations.AlterField(
            model_name='report',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='source',
            name='emission_factor',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='source',
            name='value',
            field=models.FloatField(),
        ),
        migrations.AddConstraint(
            model_name='source',
            constraint=models.CheckConstraint(check=models.Q(('report__isnull', True), ('strategy__isnull', True), _negated=True), name='rep_or_strat_not_empty'),
        ),
        migrations.AddConstraint(
            model_name='source',
            constraint=models.CheckConstraint(check=models.Q(('lifetime__isnull', True), ('acquisition_year__isnull', False), _connector='OR'), name='if_lifetime_not_empty_acquisition_year_not_empty'),
        ),
    ]
