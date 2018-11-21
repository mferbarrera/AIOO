# Generated by Django 2.1.2 on 2018-10-23 04:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_auto_20181017_1007'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectevent',
            name='owner',
        ),
        migrations.AlterField(
            model_name='project',
            name='background',
            field=models.TextField(blank=True, default='#Antecedentes', max_length=5000, null=True, verbose_name='Antecedentes'),
        ),
        migrations.AlterField(
            model_name='project',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.Country', verbose_name='Pais'),
        ),
        migrations.AlterField(
            model_name='project',
            name='justify',
            field=models.TextField(default='#Justificación', max_length=5000, verbose_name='Justificación'),
        ),
        migrations.AlterField(
            model_name='project',
            name='label',
            field=models.CharField(choices=[('Normal', 'Normal'), ('Multimedia', 'Multimedia'), ('IP+Fotónico', 'IP+Fotónico')], default='Normal', max_length=100, verbose_name='Etiqueta'),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Titulo'),
        ),
        migrations.AlterField(
            model_name='project',
            name='objective',
            field=models.TextField(default='#Objetivo', max_length=5000, verbose_name='Objetivo'),
        ),
        migrations.AlterField(
            model_name='project',
            name='owner',
            field=models.ManyToManyField(to='projects.UserProfile', verbose_name='Tripulación'),
        ),
        migrations.AlterField(
            model_name='project',
            name='pds',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.ProjectDeliverableSchema', verbose_name='Entregables'),
        ),
        migrations.AlterField(
            model_name='project',
            name='priority',
            field=models.IntegerField(default=100, verbose_name='Prioridad'),
        ),
        migrations.AlterField(
            model_name='project',
            name='ptype',
            field=models.CharField(choices=[('AC', 'Acceso'), ('AM', 'AMX'), ('AP', 'Aplicaciones'), ('CO', 'Core'), ('DI', 'Distribución'), ('LB', 'Laboratorio'), ('VI', 'Video')], max_length=2, verbose_name='Tipo de proyecto'),
        ),
        migrations.AlterField(
            model_name='project',
            name='reference',
            field=models.CharField(blank=True, max_length=200, verbose_name='Referencia'),
        ),
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(choices=[('DP', 'Diseño'), ('QP', 'Cotización'), ('QA', 'SAP-Compras'), ('IP', 'Implementación'), ('CP', 'Capitalizado'), ('PR', 'Rechazado')], default='DP', max_length=2, verbose_name='Estatus'),
        ),
        migrations.AlterField(
            model_name='project',
            name='totallocations',
            field=models.IntegerField(default=0, verbose_name='Total de sitios'),
        ),
        migrations.AlterField(
            model_name='project',
            name='year',
            field=models.IntegerField(choices=[(2019, '2019'), (2018, '2018')], verbose_name='Año de ejecución'),
        ),
    ]
