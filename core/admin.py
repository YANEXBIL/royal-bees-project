from django.contrib import admin
from .models import NewsItem, Event # Add Event to the import

# ... (Keep your NewsItemAdmin class) ...

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_datetime', 'end_datetime', 'location', 'is_upcoming')
    list_filter = ('start_datetime', 'location')
    search_fields = ('title', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_datetime'
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'location')
        }),
        ('Date & Time Information', {
            'fields': ('start_datetime', 'end_datetime')
        }),
        ('Audit Information', {
            'classes': ('collapse',), # Make this section collapsible
            'fields': ('created_by',) # created_at and updated_at are auto
        }),
    )

    def get_queryset(self, request):
        # Optimize fetching created_by user
        return super().get_queryset(request).select_related('created_by')