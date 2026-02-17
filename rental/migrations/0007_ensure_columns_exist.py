from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0006_add_user_balance'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "ALTER TABLE cars "
                "ADD COLUMN IF NOT EXISTS max_days INTEGER NOT NULL DEFAULT 7 "
                "CHECK (max_days >= 1);"
            ),
            reverse_sql="ALTER TABLE cars DROP COLUMN IF EXISTS max_days;",
        ),
        migrations.RunSQL(
            sql=(
                "ALTER TABLE users "
                "ADD COLUMN IF NOT EXISTS balance DECIMAL(12,2) NOT NULL DEFAULT 0;"
            ),
            reverse_sql="ALTER TABLE users DROP COLUMN IF EXISTS balance;",
        ),
    ]
