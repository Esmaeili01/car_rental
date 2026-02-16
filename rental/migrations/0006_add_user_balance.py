from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0005_add_car_max_reservation_days'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name='user',
                    name='balance',
                    field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
                ),
            ],
        ),
    ]
