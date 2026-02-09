from django.db import migrations

def create_categories(apps, schema_editor):
    Category = apps.get_model('jobs', 'Category')
    categories = [
        ('Programming', 'bx-code-alt'),
        ('Graphic design', 'bx-palette'),
        ('Digital Marketing & SEO', 'bx-line-chart'),
    ]
    for name, icon in categories:
        Category.objects.get_or_create(name=name, defaults={'icon': icon})

def remove_categories(apps, schema_editor):
    Category = apps.get_model('jobs', 'Category')
    names = ['Programming', 'Graphic design', 'Digital Marketing & SEO']
    Category.objects.filter(name__in=names).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0003_remove_experience_cv_alter_savedjob_unique_together_and_more'),
    ]

    operations = [
        migrations.RunPython(create_categories, remove_categories),
    ]