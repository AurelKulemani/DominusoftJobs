

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0005_contactmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='resume_file',
            field=models.FileField(blank=True, null=True, upload_to='applications/'),
        ),
        migrations.AddField(
            model_name='cv',
            name='resume_file',
            field=models.FileField(blank=True, null=True, upload_to='resumes/'),
        ),
    ]