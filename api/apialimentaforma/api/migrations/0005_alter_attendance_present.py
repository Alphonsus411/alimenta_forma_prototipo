from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('api', '0004_alter_registration_options_alter_attendance_date_and_more')]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='present',
            field=models.BooleanField(default=False, verbose_name='Presente'),
        ),
    ]
