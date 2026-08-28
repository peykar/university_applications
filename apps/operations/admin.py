from django.contrib import admin

from .models import CommunicationLog, CommunicationLogRevision, Todo, TodoComment

admin.site.register(Todo)
admin.site.register(TodoComment)
admin.site.register(CommunicationLog)
admin.site.register(CommunicationLogRevision)
