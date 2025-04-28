from django.contrib import admin
from .models import Bill


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    """Admin configuration for the Bill model."""
    list_display = ('bill_name', 'user', 'amount', 'category', 'due_date', 'priority', 'auto_pay')
    list_filter = ('category', 'priority', 'auto_pay', 'due_date')
    search_fields = ('bill_name', 'user__username', 'category', 'service_provider')
    ordering = ('due_date',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'bill_name', 'amount', 'category', 'service_provider')
        }),
        ('Dates', {
            'fields': ('due_date', 'next_due_date')
        }),
        ('Options', {
            'fields': ('repeat_frequency', 'reminder', 'priority', 'auto_pay', 'is_paid', 'attach_photo', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'payment_date')
        }),
    )

# Customize the admin site headers
admin.site.site_header = "Bill Manager Admin"
admin.site.site_title = "Bill Manager Portal"
admin.site.index_title = "Welcome to the Bill Manager Administration"