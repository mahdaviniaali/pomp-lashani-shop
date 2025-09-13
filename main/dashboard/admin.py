from django.contrib import admin
from .models import DashboardCache, ReportLog


@admin.register(DashboardCache)
class DashboardCacheAdmin(admin.ModelAdmin):
    list_display = ('cache_key', 'created_at', 'updated_at', 'expires_at')
    list_filter = ('created_at', 'updated_at', 'expires_at')
    search_fields = ('cache_key',)
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ReportLog)
class ReportLogAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'generated_by', 'generated_at', 'file_path')
    list_filter = ('report_type', 'generated_at', 'generated_by')
    search_fields = ('report_type', 'generated_by__username', 'file_path')
    readonly_fields = ('generated_at',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False