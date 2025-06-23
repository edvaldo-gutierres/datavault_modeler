from django.db import migrations, models

def forward_func(apps, schema_editor):
    Satellite = apps.get_model('modeler', 'Satellite')
    Hub = apps.get_model('modeler', 'Hub')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    # Obtém o ContentType para Hub usando o modelo histórico
    hub_ct = ContentType.objects.get(app_label='modeler', model='hub')
    
    # Para cada Satellite sem parent, associa ao primeiro Hub do projeto
    for satellite in Satellite.objects.filter(content_type__isnull=True):
        hub = Hub.objects.filter(project=satellite.project).first()
        if hub:
            satellite.content_type = hub_ct
            satellite.object_id = hub.id
            satellite.save()
        else:
            satellite.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('modeler', '0002_remove_satellite_hub_remove_satellite_link_and_more'),
    ]

    operations = [
        migrations.RunPython(forward_func),
        migrations.AlterField(
            model_name='satellite',
            name='content_type',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='satellite',
            name='object_id',
            field=models.PositiveIntegerField(),
        ),
    ] 