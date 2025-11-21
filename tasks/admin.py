from django.contrib import admin
from .models import User, Task


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'created_at']
    search_fields = ['name', 'email']
    list_filter = ['created_at']
    ordering = ['-created_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'is_completed', 'created_at']
    search_fields = ['title', 'description', 'user__name']
    list_filter = ['is_completed', 'created_at', 'user']
    ordering = ['-created_at']
    raw_id_fields = ['user']