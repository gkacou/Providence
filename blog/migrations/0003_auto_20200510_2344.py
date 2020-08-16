# Generated by Django 2.2.3 on 2020-05-10 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_donnees_initiales'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beneficiaire',
            name='sexe',
            field=models.CharField(choices=[('F', 'Féminin'), ('M', 'Masculin'), ('N', 'Non applicable')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='cas',
            name='sexe',
            field=models.CharField(choices=[('F', 'Féminin'), ('M', 'Masculin'), ('N', 'Non applicable')], max_length=1, null=True),
        ),
        migrations.AddIndex(
            model_name='beneficiaire',
            index=models.Index(fields=['nom'], name='benef_nom_idx'),
        ),
        migrations.AddIndex(
            model_name='beneficiaire',
            index=models.Index(fields=['prenoms'], name='benef_prenoms_idx'),
        ),
        migrations.AddIndex(
            model_name='communaute',
            index=models.Index(fields=['nom'], name='comm_nom_idx'),
        ),
        migrations.AddIndex(
            model_name='communaute',
            index=models.Index(fields=['nom_long'], name='comm_nom_long_idx'),
        ),
    ]