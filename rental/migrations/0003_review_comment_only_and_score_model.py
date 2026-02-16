from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0002_alter_review_score_nullable'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RemoveField(
                    model_name='review',
                    name='datetime',
                ),
                migrations.RemoveField(
                    model_name='review',
                    name='score',
                ),
                migrations.AlterField(
                    model_name='review',
                    name='comment',
                    field=models.TextField(),
                ),
                migrations.CreateModel(
                    name='Score',
                    fields=[
                        ('score_id', models.AutoField(primary_key=True, serialize=False)),
                        ('score', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                        ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='rental.car')),
                        ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='rental.user')),
                    ],
                    options={
                        'db_table': 'scores',
                    },
                ),
                migrations.AddConstraint(
                    model_name='score',
                    constraint=models.UniqueConstraint(fields=('car', 'user'), name='unique_car_user_score'),
                ),
            ],
        ),
    ]
