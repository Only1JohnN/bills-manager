from django.contrib import admin
from .models import Bill

# Register your models here.
admin.site.site_header = "Bill Manager Admin"
admin.site.site_title = "Bill Manager Portal"
admin.site.index_title = "Welcome to the Bill Manager Administration"
from .models import Bill

admin.site.register(Bill)
# admin.site.register(BillItem)
