# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Dptm(models.Model):
    dpt_id = models.PositiveSmallIntegerField(primary_key=True,verbose_name='部门编号')
    dpt_up = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True, verbose_name='上级部门')
    CATEGORY_CHOICES = (
        ('0', '否'),
        ('1', '是'),
    )
    dpt_is_yw = models.CharField(max_length=1, blank=True, null=True,verbose_name='是否业务部门',choices = CATEGORY_CHOICES)
    dpt_name = models.CharField(max_length=255, blank=True, null=True,verbose_name='部门名称')
    dpt_short_name = models.CharField(max_length=255, blank=True, null=True,verbose_name='简称')
    dpt_charge = models.ForeignKey('Staff', models.DO_NOTHING, blank=True, null=True,verbose_name='负责人ID')
    dpt_site = models.ForeignKey('Sitdsc', models.DO_NOTHING,blank=True, null=True,verbose_name='场地ID')

    class Meta:
        managed = False
        db_table = 'dptm'
        verbose_name = '部门'
    def __str__(self):
        return self.dpt_name

class Dptstaff(models.Model):
    ds_idx = models.IntegerField(primary_key=True)
    dpt = models.ForeignKey('Dptm', models.DO_NOTHING,verbose_name='部门')
    staff = models.ForeignKey('Staff', models.DO_NOTHING,verbose_name='员工')

    class Meta:
        managed = False
        db_table = 'dptstaff'
        unique_together = (('dpt', 'staff'),)
        verbose_name = '部门员工归属'

class Sitdsc(models.Model):
    sit_id = models.SmallIntegerField(primary_key=True)
    sit_name = models.CharField(max_length=80, blank=True, null=True,verbose_name='场地名称')
    sit_short = models.CharField(max_length=20, blank=True, null=True,verbose_name='场地简称')
    CATEGORY_CHOICES = (
        (0, '写字楼'),
        (1, '门店'),
        (2, '停车场'),
    )
    sit_attr = models.IntegerField(blank=True, null=True,verbose_name='场地用途',choices = CATEGORY_CHOICES)
    CATEGORY_CHOICES1 = (
        (0, '自有'),
        (1, '租赁'),
    )
    sit_owner = models.IntegerField(blank=True, null=True,choices = CATEGORY_CHOICES1,verbose_name='场地性质')
    sit_start_date = models.DateField(blank=True, null=True,verbose_name='启用日期')
    sit_end_date = models.DateField(blank=True, null=True,verbose_name='结束日期')
    sit_size = models.FloatField(blank=True, null=True,verbose_name='面积')
    sit_station = models.IntegerField(blank=True, null=True,verbose_name='工位')
    sit_park = models.IntegerField(blank=True, null=True,verbose_name='停车位')

    def __str__(self):
        return self.sit_name

    class Meta:
        managed = False
        db_table = 'sitdsc'
        verbose_name = '场地'

class Staff(models.Model):
    staff_id = models.SmallIntegerField(primary_key=True,verbose_name='员工ID')
    staff_name = models.CharField(max_length=20, blank=True, null=True,verbose_name='姓名')
    CATEGORY_CHOICES = (
        ('M', '男'),
        ('F', '女'),
    )
    staff_sex = models.CharField(max_length=1, blank=True, null=True,verbose_name='性别',choices = CATEGORY_CHOICES)
    staff_cell = models.CharField(max_length=11, blank=True, null=True,verbose_name='手机')
    CATEGORY_CHOICES1 = (
        (0, '业务'),
        (1, '车管'),
        (2, '高管'),
    )
    staff_role = models.IntegerField(blank=True, null=True,verbose_name='角色',choices = CATEGORY_CHOICES1)
    staff_user = models.CharField(max_length=20, blank=True, null=True,verbose_name='登录名')
    staff_pwd = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'staff'
        verbose_name = '员工'

    def __str__(self):
        return self.staff_name

class Cust(models.Model):
    cust_id = models.IntegerField(primary_key=True)
    cust_name = models.CharField(max_length=20, blank=True, null=True)
    cust_tel1 = models.CharField(max_length=13, blank=True, null=True)
    cust_tel2 = models.CharField(max_length=13, blank=True, null=True)
    cust_status = models.SmallIntegerField(blank=True, null=True)
    cust_staff = models.SmallIntegerField(blank=True, null=True)
    cust_edata = models.DateField(blank=True, null=True)
    cust_gdate = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cust'

class CarSeries(models.Model):
    series_idx = models.AutoField(primary_key=True)
    brand = models.ForeignKey('CarBrand', models.DO_NOTHING,verbose_name='品牌')
    prod_id = models.BigIntegerField( verbose_name='产品')
    series_id = models.BigIntegerField(verbose_name='型号ID')
    series_name = models.CharField(max_length=255,verbose_name='型号名称')
    series_price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True,verbose_name='指导价格')

    class Meta:
        managed = False
        db_table = 'car_series'
        verbose_name = '车辆型号'

class CarProd(models.Model):
    prod_idx = models.AutoField(primary_key=True)
    brand = models.ForeignKey('CarBrand', models.DO_NOTHING,verbose_name='品牌')
    prod_id = models.BigIntegerField(verbose_name='产品ID')
    prod_name = models.CharField(max_length=255, verbose_name='产品名称')

    class Meta:
        managed = False
        db_table = 'car_prod'
        verbose_name = '车辆产品'

class CarBrand(models.Model):
    brand_id = models.BigIntegerField(primary_key=True,verbose_name='品牌ID')
    brand_name = models.CharField(max_length=255,verbose_name='品牌名称')
    brand_logo = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'car_brand'
        verbose_name = ' 车辆品牌'
    def __str__(self):
        return self.brand_name

class CarDocum(models.Model):
    docum_car_id = models.IntegerField(primary_key=True)
    docum_type = models.SmallIntegerField()
    docum_item = models.SmallIntegerField()
    docum_num=models.CharField(max_length=255, blank=True, null=True)
    docum_start_date = models.DateTimeField(blank=True, null=True)
    docum_end_date = models.DateTimeField(blank=True, null=True)
    docum_maint_staff = models.SmallIntegerField(blank=True, null=True)
    docum_maint_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'car_docum'
        unique_together = (('docum_car_id', 'docum_type', 'docum_item'),)

class CarHold(models.Model):
    car_id = models.IntegerField(primary_key=True)
    car_brand_id = models.BigIntegerField(blank=True, null=True)
    car_product_id = models.BigIntegerField(blank=True, null=True)
    car_series_id = models.BigIntegerField(blank=True, null=True)
    car_color = models.SmallIntegerField(blank=True, null=True)
    car_dpt_id = models.SmallIntegerField(blank=True, null=True)
    car_sit_id = models.SmallIntegerField(blank=True, null=True)
    car_status = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'car_hold'

class CarLog(models.Model):
    log_type = models.CharField(primary_key=True, max_length=1)
    log_id = models.IntegerField()
    log_item = models.IntegerField()
    log_desc = models.CharField(max_length=255, blank=True, null=True)
    log_staff = models.SmallIntegerField(blank=True, null=True)
    log_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'car_log'
        unique_together = (('log_type', 'log_id', 'log_item'),)

class Stat(models.Model):
    type = models.SmallIntegerField(primary_key=True)
    item = models.SmallIntegerField()
    status = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stat'
        unique_together = (('type', 'item'),)

class CarOver(models.Model):
    over_id = models.IntegerField(primary_key=True)
    over_car = models.IntegerField(blank=True, null=True)
    over_cust = models.IntegerField(blank=True, null=True)
    over_cont = models.CharField(max_length=30, blank=True, null=True)
    over_staff = models.SmallIntegerField(blank=True, null=True)
    over_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'car_over'