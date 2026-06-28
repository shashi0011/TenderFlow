from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Category, Quote, RFP, RFPVendor, User, VendorProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
 
    pass


admin.site.register(Category)
admin.site.register(VendorProfile)
admin.site.register(RFP)
admin.site.register(RFPVendor)
admin.site.register(Quote)
