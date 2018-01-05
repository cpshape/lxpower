from django.contrib import admin
from .models  import  Staff,Dptm,Sitdsc,CarBrand,CarProd,CarSeries,Dptstaff
from werkzeug.security import  generate_password_hash

class StaffAdmin(admin.ModelAdmin):
    list_display = ('staff_id','staff_name', 'staff_sex', 'staff_role','staff_cell','staff_user')
    fields = ('staff_name', 'staff_sex', 'staff_role','staff_cell', 'staff_user')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.staff_pwd = generate_password_hash('123456')
        obj.save()

class DptmAdmin(admin.ModelAdmin):
    list_display = ('dpt_id','dpt_name','dpt_up','dpt_short_name', 'dpt_is_yw',  'dpt_charge','dpt_site')
    fields = ('dpt_name','dpt_up',  'dpt_short_name','dpt_is_yw', 'dpt_charge','dpt_site')

class SitdscAdmin(admin.ModelAdmin):
    list_display = ('sit_name', 'sit_short', 'sit_attr','sit_owner', 'sit_start_date', 'sit_end_date','sit_size', 'sit_station','sit_park')
    fields = ('sit_name', 'sit_short', 'sit_attr','sit_owner', 'sit_start_date', 'sit_end_date','sit_size', 'sit_station','sit_park')

class CarBrandAdmin(admin.ModelAdmin):
    list_display = ('brand_id', 'brand_name')
    fields = ('brand_id', 'brand_name')

class CarProdAdmin(admin.ModelAdmin):
    list_display = ('brand', 'prod_id', 'prod_name')
    fields = ('brand', 'prod_id', 'prod_name')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "brand_id":
            kwargs["queryset"] = CarBrand.objects.all('brand_id')

        return super(CarProdAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

class CarSeriesAdmin(admin.ModelAdmin):
    list_display = ('brand', 'prod_id', 'series_id','series_name','series_price')
    fields = ('brand', 'prod_id', 'series_id','series_name','series_price')

class DptstaffAdmin(admin.ModelAdmin):
    list_display = ('dpt', 'staff')
    fields = ('dpt', 'staff')

admin.site.register(Staff,StaffAdmin)
admin.site.register(Dptm,DptmAdmin)
admin.site.register(Sitdsc,SitdscAdmin)
admin.site.register(CarBrand,CarBrandAdmin)
admin.site.register(CarProd,CarProdAdmin)
admin.site.register(CarSeries,CarSeriesAdmin)
admin.site.register(Dptstaff,DptstaffAdmin)