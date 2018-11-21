from django.contrib import admin
from django.apps import apps



# Register your models here.



projects = apps.get_app_config('projects')

for model_name, model in projects.models.items():
	admin.site.register(model)


