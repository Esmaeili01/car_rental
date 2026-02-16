from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0003_review_comment_only_and_score_model'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RemoveConstraint(
                    model_name='score',
                    name='unique_car_user_score',
                ),
            ],
        ),
    ]
