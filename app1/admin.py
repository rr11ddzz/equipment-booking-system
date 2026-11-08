from django.contrib import admin
from .models import DeviceType,CPU,GPU,RAM,Equipment,CustomUser,Booking,InventoryCount

# Register your models here.
admin.site.register(DeviceType)
admin.site.register(CPU)
admin.site.register(GPU)
admin.site.register(RAM)
admin.site.register(Equipment)
admin.site.register(CustomUser)
admin.site.register(Booking)
admin.site.register(InventoryCount)