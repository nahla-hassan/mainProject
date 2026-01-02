from django.contrib import admin
from .models import Student, Teacher, UserRole,TimeTableEntry

models_to_register = [Student, Teacher, UserRole,TimeTableEntry]

for model in models_to_register:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass

