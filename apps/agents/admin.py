from django.contrib import admin
from .models import Agent, AgentDocument

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("company_name", "email", "cell", "landline", "parent", "is_active")
    search_fields = ("company_name", "email", "cell", "landline", "users__username", "users__email")

@admin.register(AgentDocument)
class AgentDocumentAdmin(admin.ModelAdmin):
    list_display = ("name", "agent", "created_at")
    search_fields = ("name", "description", "agent__company_name")
