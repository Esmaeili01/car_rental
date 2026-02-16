from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0004_remove_score_unique_constraint'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name='car',
                    name='max_days',
                    field=models.PositiveIntegerField(default=7),
                ),
            ],
        ),
    ]
