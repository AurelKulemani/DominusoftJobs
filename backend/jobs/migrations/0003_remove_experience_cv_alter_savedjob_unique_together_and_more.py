

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_application_savedjob'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='experience',
            name='cv',
        ),
        migrations.AlterUniqueTogether(
            name='savedjob',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='savedjob',
            name='job',
        ),
        migrations.RemoveField(
            model_name='savedjob',
            name='user',
        ),
        migrations.RemoveField(
            model_name='skill',
            name='cv',
        ),
        migrations.DeleteModel(
            name='Education',
        ),
        migrations.DeleteModel(
            name='Experience',
        ),
        migrations.DeleteModel(
            name='SavedJob',
        ),
        migrations.DeleteModel(
            name='Skill',
        ),
    ]