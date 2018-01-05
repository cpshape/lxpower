from django.shortcuts import render
from django.shortcuts import redirect
from werkzeug.security import check_password_hash, generate_password_hash
from . import models
from . import forms
from pyecharts import Bar, Pie, Style
from django.core.paginator import Paginator
from django.http.response import HttpResponse
from django.db import transaction
import json
import datetime


# Create your views here.

def getDatil(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = []
    if request.method == "GET":
        car_sel = models.CarHold.objects.get(car_id=request.GET['dcar_id'])
        brand_sel = models.CarBrand.objects.get(brand_id=car_sel.car_brand_id).brand_name
        prod_sel = models.CarProd.objects.get(brand_id=car_sel.car_brand_id, prod_id=car_sel.car_product_id).prod_name
        series_sel = models.CarSeries.objects.get(brand_id=car_sel.car_brand_id, prod_id=car_sel.car_product_id,
                                                  series_id=car_sel.car_series_id).series_name
        sta_sel = models.Stat.objects.get(type=1, item=car_sel.car_status).status
        desc = "未选定"
        if not (car_sel.car_color is None):
            desc = models.Stat.objects.get(type=7, item=car_sel.car_color).status
        response_data.append(
            {'d_name': '车辆',
             'd_item': '',
             'd_desc': str(car_sel.car_id) + '#：' + brand_sel + prod_sel + series_sel + '，颜色：' + desc + '，状态：' + sta_sel
             })

        desc = '无'
        sele = models.CarDocum.objects.filter(docum_car_id=car_sel.car_id, docum_type=2, docum_item=1).values()
        if sele.count() > 0:
            desc = sele[0]['docum_num']
        response_data.append(
            {'d_name': '车牌',
             'd_item': '',
             'd_desc': desc})

        desc = "未指定"
        if not (car_sel.car_dpt_id is None):
            desc = models.Dptm.objects.get(dpt_id=car_sel.car_dpt_id).dpt_name
        response_data.append(
            {'d_name': '归属',
             'd_item': '',
             'd_desc': desc})

        desc = "未指定"
        if not (car_sel.car_sit_id is None):
            desc = models.Sitdsc.objects.get(sit_id=car_sel.car_sit_id).sit_name
        response_data.append(
            {'d_name': '停放',
             'd_item': '',
             'd_desc': desc})

        sele = models.CarOver.objects.filter(over_car=request.GET['dcar_id'])
        if sele.count()>0:
            for i in sele:
                desc =models.Staff.objects.get(staff_id=i.over_staff).staff_name +' 于 '+i.over_date.strftime('%Y-%m-%d')+' 交车给：'+models.Cust.objects.get(cust_id=i.over_cust).cust_name
                response_data.append(
                    {'d_name': '客户',
                     'd_item': '',
                     'd_desc': desc})
        else:
            response_data.append(
                {'d_name': '客户',
                 'd_item': '',
                 'd_desc': '未定'})

        sele = models.Stat.objects.filter(type=2, item__gt=1)
        for i in sele:
            try:
                obj = models.CarDocum.objects.get(docum_car_id=car_sel.car_id, docum_type=2, docum_item=i.item)
            except:
                desc = '未指定'
            else:
                desc = '编号：' + obj.docum_num + ' 效期：'
                if (obj.docum_start_date is None):
                    desc = desc + '-'
                else:
                    desc = desc + obj.docum_start_date.strftime('%Y-%m-%d')
                desc = desc + '——'
                if (obj.docum_end_date is None):
                    desc = desc + '-'
                else:
                    desc = desc + obj.docum_end_date.strftime('%Y-%m-%d')
            response_data.append({'d_name': i.status, 'd_item': '', 'd_desc': desc})

        sele = models.CarLog.objects.filter(log_type='D', log_id=car_sel.car_id)
        for i in sele:
            response_data.append(
                {'d_name': '日志',
                 'd_item': i.log_item,
                 'd_desc': models.Staff.objects.get(staff_id=i.log_staff).staff_name + '于' + i.log_date.strftime(
                     '%Y-%m-%d') + '：' + i.log_desc})

    return HttpResponse(json.dumps(response_data))


def getCstlog(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = []

    if request.method == "GET":
        sel = models.CarLog.objects.filter(log_type='C', log_id=request.GET['dcust_id'])

        for i in sel:
            response_data.append(
                {
                    'c_item': i.log_item,
                    'c_desc': models.Staff.objects.get(staff_id=i.log_staff).staff_name + ' 于 ' + i.log_date.strftime(
                        '%Y-%m-%d') + '： ' + i.log_desc})
    return HttpResponse(json.dumps(response_data))


def login(request):
    if request.session.get('is_login', None):
        return redirect('/general/')
    if request.method == "POST":
        request.session.flush()
        login_form = forms.UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = models.Staff.objects.get(staff_user=username)
                if check_password_hash(user.staff_pwd, password):
                    request.session['is_login'] = True
                    request.session['user_name'] = user.staff_name
                    request.session['user_id'] = user.staff_id
                    request.session['user_role'] = user.staff_role
                    return redirect('/index/')
                else:
                    message = '密码不正确！'
            except Exception as e:
                message = e
    login_form = forms.UserForm()
    return render(request, 'login.html', locals())


def logout(request):
    if request.session.get('is_login', None):
        request.session.flush()
    return redirect('/login/')


def savePwd(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = [{'status': 'ok'}]
    sel = models.Staff.objects.get(staff_id=request.session['user_id'])
    if check_password_hash(sel.staff_pwd, request.GET['old_pwd']):
        if request.method == "GET":
            try:
                with transaction.atomic():
                    sel.staff_pwd = generate_password_hash(request.GET['new_pwd'])
                    sel.save()
            except Exception as e:
                print('err:' + str(e))
                response_data = [{'status': 'err'}]
    else:
        response_data = [{'status': 'pwd'}]
    return HttpResponse(json.dumps(response_data))


def sndJc(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = [{'status': 'ok'}]
    sta = int(request.GET['dcar_sta'])
    if sta == 2:
        desc = "接收采购车辆"
    if sta == 3:
        desc = "手续办理完毕，入库等候交车"
    if sta == 9:
        desc = "送修理厂维修"
    try:
        with transaction.atomic():
            ls = request.GET['dcar_id'][1:-1]
            for i in ls.split(','):
                sel = models.CarHold.objects.get(car_id=int(i))
                sel.car_status = sta
                sel.save()
                cnt = models.CarLog.objects.filter(log_type='D', log_id=int(i)).count() + 1
                models.CarLog.objects.create(log_type='D', log_id=int(i), log_item=cnt, log_desc=desc,
                                             log_staff=request.session['user_id'], log_date=datetime.datetime.now())
    except Exception as e:
        print('err:' + str(e))
        response_data = [{'status': 'err'}]
    return HttpResponse(json.dumps(response_data))


def saveGua(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = [{'status': 'ok'}]
    sta = int(request.GET['dcar_sta'])
    try:
        with transaction.atomic():
            ls = request.GET['dcar_id'][1:-1]
            for i in ls.split(','):
                sel = models.Cust.objects.get(cust_id=int(i))
                sel.cust_status = sta
                sel.cust_gdate = datetime.datetime.now()
                sel.save()
                cnt = models.CarLog.objects.filter(log_type='C', log_id=int(i)).count() + 1
                models.CarLog.objects.create(log_type='C', log_id=int(i), log_item=cnt,
                                             log_desc='客户挂起：' + sel.cust_name,
                                             log_staff=request.session['user_id'], log_date=datetime.datetime.now())
    except Exception as e:
        print('err:' + str(e))
        response_data = [{'status': 'err'}]
    return HttpResponse(json.dumps(response_data))


def carinfo(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')

    return render(request, 'carinfo.html', locals())


def custinfo(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    return render(request, 'custinfo.html', locals())


def mywork(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    return render(request, 'mywork.html', locals())


def getBrand(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = []
    if request.method == "GET":
        brand = models.CarBrand.objects.values()
        for items in brand:
            response_data.append({
                "id": items['brand_id'],
                "name": items['brand_name'],
            })
    return HttpResponse(json.dumps(response_data))


def getProd(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = []
    if request.method == "GET":
        prod = models.CarProd.objects.filter(brand_id=(request.GET)['brand_sel']).values()
        for items in prod:
            response_data.append({
                "id": items['prod_id'],
                "name": items['prod_name'],
            })
    return HttpResponse(json.dumps(response_data))


def saveDpt(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = [{'status': 'ok'}]
    if request.method == "GET":
        try:
            with transaction.atomic():
                sel = models.CarHold.objects.get(car_id=request.GET['dcar_id'])
                sel.car_dpt_id = request.GET['dcar_dpt']
                sel.save()

                cnt = models.CarLog.objects.filter(log_type='D', log_id=request.GET['dcar_id']).count() + 1
                sel = models.Dptm.objects.get(dpt_id=request.GET['dcar_dpt'])
                models.CarLog.objects.create(log_type='D', log_id=request.GET['dcar_id'], log_item=cnt,
                                             log_desc='分配到部门' + ': ' + sel.dpt_short_name,
                                             log_staff=request.session['user_id'], log_date=datetime.datetime.now())
        except Exception as e:
            print('err:' + str(e))
            response_data = [{'status': 'err'}]
    return HttpResponse(json.dumps(response_data))


def dapCust(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = [{'status': 'ok'}]
    if request.method == "GET":
        try:
            with transaction.atomic():

                sel = models.CarHold.objects.get(car_id=request.GET['dcar_id'])
                sel.car_status = 4
                sel.save()
                sel = models.Cust.objects.get(cust_id=request.GET['dcar_cust'])
                sel.cust_status = 6
                sel.save()

                models.CarOver.objects.create(over_car=request.GET['dcar_id'],over_cust=request.GET['dcar_cust'],
                                              over_cont=request.GET['dcar_cont'],
                                              over_staff=request.session['user_id'],over_date=datetime.datetime.now())

                cnt = models.CarLog.objects.filter(log_type='D', log_id=request.GET['dcar_id']).count() + 1
                models.CarLog.objects.create(log_type='D', log_id=request.GET['dcar_id'], log_item=cnt,
                                             log_desc='交车给客户: ' + sel.cust_name,
                                             log_staff=request.session['user_id'], log_date=datetime.datetime.now())

                num = models.CarDocum.objects.get(docum_car_id=request.GET['dcar_id'], docum_type=2,docum_item=1).docum_num
                models.CarLog.objects.create(log_type='C', log_id=request.GET['dcar_cust'], log_item=cnt + 1,
                                             log_desc='交车：' + num,
                                             log_staff=request.session['user_id'], log_date=datetime.datetime.now())
        except Exception as e:
            print('err:' + str(e))
            response_data = [{'status': 'err'}]
    return HttpResponse(json.dumps(response_data))


def saveCust(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = [{'status': 'ok'}]
    if request.method == "GET":
        try:
            with transaction.atomic():
                if request.GET['dcst_tye'] == '1':
                    cnt = models.Cust.objects.all().count() + 1
                    models.Cust.objects.create(cust_id=cnt, cust_name=request.GET['dcst_name'],
                                               cust_tel1=request.GET['dcst_tel1'], cust_tel2=request.GET['dcst_tel2'],
                                               cust_status=1, cust_staff=request.session['user_id'],
                                               cust_edata=datetime.datetime.now())
                    logc = models.CarLog.objects.filter(log_type='C', log_id=cnt).count() + 1
                    models.CarLog.objects.create(log_type='C', log_id=cnt, log_item=logc,
                                                 log_desc='新客户' + ': ' + request.GET['dcst_name'],
                                                 log_staff=request.session['user_id'], log_date=datetime.datetime.now())
                if request.GET['dcst_tye'] == '2':
                    sel = models.Cust.objects.get(cust_id=request.GET['dcst_name'])
                    sel.cust_staff = request.GET['dcst_tel1']
                    sel.save()

                    usr = models.Staff.objects.get(staff_id=sel.cust_staff)
                    cnt = models.CarLog.objects.filter(log_type='C', log_id=sel.cust_id).count() + 1
                    models.CarLog.objects.create(log_type='C', log_id=sel.cust_id, log_item=cnt,
                                                 log_desc='重新分配给跟单经理：' + usr.staff_name,
                                                 log_staff=request.session['user_id'], log_date=datetime.datetime.now())
        except Exception as e:
            print('err:' + str(e))
            response_data = [{'status': 'err'}]
    return HttpResponse(json.dumps(response_data))


def submitS(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = [{'status': 'ok'}]
    if request.method == "GET":
        try:
            with transaction.atomic():
                sel = models.Cust.objects.get(cust_id=request.GET['dcst_id'])
                sel.cust_status = request.GET['dcst_sta']
                sel.save()
                logc = models.CarLog.objects.filter(log_type='C', log_id=sel.cust_id).count() + 1
                models.CarLog.objects.create(log_type='C', log_id=sel.cust_id, log_item=logc,
                                             log_desc=models.Stat.objects.get(type=3,
                                                                              item=sel.cust_status).status + ': ' + sel.cust_name,
                                             log_staff=request.session['user_id'], log_date=datetime.datetime.now())
        except Exception as e:
            print('err:' + str(e))
            response_data = [{'status': 'err'}]
    return HttpResponse(json.dumps(response_data))


def saveColor(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = [{'status': 'ok'}]
    if request.method == "GET":
        try:
            with transaction.atomic():
                sel = models.CarHold.objects.get(car_id=request.GET['dcar_id'])
                sel.car_color = request.GET['dcar_color']
                sel.save()
        except Exception as e:
            print('err:' + str(e))
            response_data = [{'status': 'err'}]
    return HttpResponse(json.dumps(response_data))


def getColor(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = []
    if request.method == "GET":
        color = models.Stat.objects.filter(type=7).values()
        for items in color:
            response_data.append({
                "id": items['item'],
                "name": items['status'],
            })
    return HttpResponse(json.dumps(response_data))


def saveSit(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = [{'status': 'ok'}]
    if request.method == "GET":
        try:
            with transaction.atomic():
                sel = models.CarHold.objects.get(car_id=request.GET['dcar_id'])
                sel.car_sit_id = request.GET['dcar_sit']
                sel.save()
                cnt = models.CarLog.objects.filter(log_type='D', log_id=request.GET['dcar_id']).count() + 1
                sel = models.Sitdsc.objects.get(sit_id=request.GET['dcar_sit'])
                models.CarLog.objects.create(log_type='D', log_id=request.GET['dcar_id'], log_item=cnt,
                                             log_desc='停放到' + ': ' + sel.sit_short,
                                             log_staff=request.session['user_id'], log_date=datetime.datetime.now())
        except Exception as e:
            print('err:' + str(e))
            response_data = [{'status': 'err'}]
    return HttpResponse(json.dumps(response_data))


def getSit(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = []
    if request.method == "GET":
        sit = models.Sitdsc.objects.all().values()
        for items in sit:
            response_data.append({
                "id": items['sit_id'],
                "name": items['sit_short'],
            })
    return HttpResponse(json.dumps(response_data))


def getCust(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = []
    if request.method == "GET":
        cust = models.Cust.objects.filter(cust_status=3).values()
        for items in cust:
            response_data.append({
                "id": items['cust_id'],
                "name": items['cust_name'],
            })
    return HttpResponse(json.dumps(response_data))


def getDpt(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = []
    if request.method == "GET":
        dpt = models.Dptm.objects.filter(dpt_is_yw=1).values()
        for items in dpt:
            response_data.append({
                "id": items['dpt_id'],
                "name": items['dpt_short_name'],
            })
    return HttpResponse(json.dumps(response_data))


def getSeries(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = []
    if request.method == "GET":
        series = models.CarSeries.objects.filter(brand_id=request.GET['brand_sel'],
                                                 prod_id=request.GET['prod_sel']).values()
        for items in series:
            response_data.append({
                "id": items['series_id'],
                "name": items['series_name'] + ',￥' + str(items['series_price']),
            })
    return HttpResponse(json.dumps(response_data))


def getstf(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = []
    if request.method == "GET":
        series = models.Staff.objects.filter(staff_role=0).values()
        for items in series:
            response_data.append({
                "id": items['staff_id'],
                "name": items['staff_name'],
            })
    return HttpResponse(json.dumps(response_data))


def carsBuy(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = [{'status': 'ok'}]
    if request.method == "GET":
        i = int(request.GET['cars_num'])
        sel = models.CarHold.objects.all().order_by('-car_id').values()
        if len(sel) == 0:
            carid = 1
        else:
            carid = sel[0]['car_id'] + 1
        try:
            with transaction.atomic():
                while i > 0:
                    models.CarHold.objects.create(car_id=carid, car_brand_id=request.GET['brand_sel'],
                                                  car_product_id=request.GET['prod_sel'],
                                                  car_series_id=request.GET['series_sel'], car_status=1)
                    cnt = models.CarLog.objects.filter(log_type='D', log_id=carid).count() + 1
                    models.CarLog.objects.create(log_type='D', log_id=carid, log_item=cnt, log_desc='采购',
                                                 log_staff=request.session['user_id'], log_date=datetime.datetime.now())
                    i = i - 1
                    carid = carid + 1
        except Exception as e:
            print('err:' + str(e))
            response_data = [{'status': 'err'}]
    return HttpResponse(json.dumps(response_data))


def sndCarnum(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = [{'status': 'ok'}]
    if request.method == "GET":
        carnn = request.GET['dcar_qq'] + (request.GET['dcar_num'].strip()).upper()
        try:
            with transaction.atomic():
                sel = models.CarDocum.objects.filter(docum_car_id=request.GET['dcar_id'], docum_type=2, docum_item=1)
                if sel.count() > 0:
                    sel.update(docum_num=carnn, docum_maint_staff=request.session['user_id'],
                               docum_maint_date=datetime.datetime.now())
                else:
                    models.CarDocum.objects.create(docum_car_id=request.GET['dcar_id'], docum_type=2, docum_item=1,
                                                   docum_num=carnn, docum_maint_staff=request.session['user_id'],
                                                   docum_maint_date=datetime.datetime.now())

                cnt = models.CarLog.objects.filter(log_type='D', log_id=request.GET['dcar_id']).count() + 1
                models.CarLog.objects.create(log_type='D', log_id=request.GET['dcar_id'], log_item=cnt,
                                             log_desc='上牌:' + carnn,
                                             log_staff=request.session['user_id'], log_date=datetime.datetime.now())
        except Exception as e:
            print('err:' + str(e))
            response_data = [{'status': 'err'}]
    return HttpResponse(json.dumps(response_data))


def sndDoc(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    response_data = [{'status': 'ok'}]
    if request.method == "GET":
        seq = int(request.GET['dcar_ty']) + 1
        if request.GET['dcar_star'] == '':
            d_star = None
        else:
            date_s = str(request.GET['dcar_star'])
            d_star = datetime.datetime.strptime(date_s, "%Y-%m-%d")

        if request.GET['dcar_end'] == '':
            d_end = None
        else:
            date_s = str(request.GET['dcar_end'])
            d_end = datetime.datetime.strptime(date_s, "%Y-%m-%d")

        try:
            with transaction.atomic():
                sel = models.CarDocum.objects.filter(docum_car_id=request.GET['dcar_id'], docum_type=2, docum_item=seq)
                if sel.count() > 0:
                    sel.update(
                        docum_num=request.GET['dcar_dnum'],
                        docum_start_date=d_star,
                        docum_end_date=d_end,
                        docum_maint_staff=request.session['user_id'],
                        docum_maint_date=datetime.datetime.now())
                else:
                    models.CarDocum.objects.create(docum_car_id=request.GET['dcar_id'], docum_type=2, docum_item=seq,
                                                   docum_num=request.GET['dcar_dnum'],
                                                   docum_start_date=d_star, docum_end_date=d_end,
                                                   docum_maint_staff=request.session['user_id'],
                                                   docum_maint_date=datetime.datetime.now())

                cnt = models.CarLog.objects.filter(log_type='D', log_id=request.GET['dcar_id']).count() + 1
                dsc = models.Stat.objects.filter(type=2, item=seq).values()[0]['status']
                models.CarLog.objects.create(log_type='D', log_id=request.GET['dcar_id'], log_item=cnt,
                                             log_desc=dsc + ':' + request.GET['dcar_dnum'],
                                             log_staff=request.session['user_id'], log_date=datetime.datetime.now())
        except Exception as e:
            print('err:' + str(e))
            response_data = [{'status': 'err'}]
    return HttpResponse(json.dumps(response_data))


def getCarls(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    if request.method == "GET":
        limit = request.GET.get('limit')
        offset = request.GET.get('offset')
        lstty = request.GET.get('lstty')
#        search = request.GET.get('search')
        #       sort_column=request.GET.get('sort')
        #     order=request.GET.get('order')

        if not offset:
            offset = 0
        if not limit:
            limit = 10
        if lstty=='1':
            all_rcd = models.CarHold.objects.filter(car_status__in=[1, 2, 3, 9])
        if lstty=='2':
            all_rcd = models.CarHold.objects.filter(car_status__in=[4,5])

        if request.session.get('user_role') == 0:
            dptls = []
            dpts = models.Dptstaff.objects.filter(staff_id=request.session.get('user_id'))
            if dpts.count() > 0:
                for dpt in dpts:
                    dptls.append(dpt.dpt_id)
            all_rcd = all_rcd.filter(car_dpt_id__in=dptls)

        all_rcd = all_rcd.values().order_by('car_id')
        all_rcd_num = all_rcd.count()
        paginator = Paginator(all_rcd, limit)

        page = int(int(offset) / int(limit) + 1)
        data = paginator.page(page)
        response_data = {'total': all_rcd_num, 'rows': []}
        for items in data:
            brand = models.CarBrand.objects.get(brand_id=items['car_brand_id'])
            prod = models.CarProd.objects.get(brand_id=items['car_brand_id'],
                                                 prod_id=items['car_product_id'])
            cseries = models.CarSeries.objects.get(brand_id=items['car_brand_id'], prod_id=items['car_product_id'],
                                                      series_id=items['car_series_id'])

            if items['car_color']:
                color = models.Stat.objects.get(type=7, item=items['car_color']).status
            else:
                color = None

            if items['car_dpt_id']:
                dptn = models.Dptm.objects.get(dpt_id=items['car_dpt_id']).dpt_short_name
            else:
                dptn = None

            sel= models.CarOver.objects.filter(over_car=items['car_id']).order_by('-over_id')
            if sel.count() > 0:
                cust=  models.Cust.objects.get(cust_id=sel.values()[0]['over_cust']).cust_name
                ht = sel.values()[0]['over_cont']
                jcrq =sel.values()[0]['over_date'].strftime('%Y-%m-%d')
            else:
                cust = None

            if items['car_sit_id']:
                sit = models.Sitdsc.objects.get(sit_id=items['car_sit_id']).sit_short
            else:
                sit = None

            if items['car_status']:
                sta = models.Stat.objects.get(type=1, item=items['car_status']).status
            else:
                sta = None

            doc=[None,None,None,None,None,None,None,None,None,None,None,None,None]
            sel=models.CarDocum.objects.filter(docum_car_id=items['car_id'], docum_type=2)
            for i in sel:
                if i.docum_item==1:
                    doc[i.docum_item-1]=i.docum_num
                else:
                    doc[i.docum_item - 1] = '<i class="icon-ok"></i>'

            if lstty=='2':
                response_data['rows'].append({"car_id": items['car_id'],
                                              "car_name": brand.brand_name + ' ' + prod.prod_name + ' ' + cseries.series_name,
                                              "cust_name": cust,
                                              "car_num": doc[0],
                                              "car_color_d": color,
                                              "car_ht":ht,
                                              "car_jcrq":jcrq,
                                              })

            if lstty == '1':
                response_data['rows'].append({"car_id": items['car_id'],
                                          "car_name": brand.brand_name + ' ' + prod.prod_name + ' ' + cseries.series_name,
                                          "series_price": str(cseries.series_price),
                                          "car_color_d": color,
                                          "dpt_name": dptn,
                                          "sit_name": sit,
                                          "car_st_desc": sta,
                                          "cust_name": cust,
                                          "car_num": doc[0],
                                          "have_hege": doc[1],
                                          "have_invo": doc[2],
                                          "have_baoyang": doc[3],
                                          "have_shuom": doc[4],
                                          "have_yizhix": doc[5],
                                          "have_shangx": doc[6],
                                          "have_shui": doc[7],
                                          "have_xzu": doc[8],
                                          "have_gps": doc[9],
                                          "have_jiaoq": doc[10],
                                          "have_vin": doc[11],
                                          "have_ein": doc[12],
                                          })
    return HttpResponse(json.dumps(response_data))


def getCstls(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    if request.method == "GET":
        limit = request.GET.get('limit')
        offset = request.GET.get('offset')
        lstty = request.GET.get('lstty')
        #        search = request.GET.get('search')
        #       sort_column=request.GET.get('sort')
        #     order=request.GET.get('order')

        if not offset:
            offset = 0
        if not limit:
            limit = 10

        if lstty == '1':
            lststr = [1, 2, 3, 4, 5]
        if lstty == '2':
            lststr = [6]
        if lstty == '3':
            lststr = [7]
        all_rcd = models.Cust.objects.filter(cust_status__in=lststr)

        if request.session.get('user_role') == 0:
            lststr = []
            lststr.append(request.session.get('user_id'))
            dpt = models.Dptm.objects.filter(dpt_charge=request.session.get('user_id'))
            if dpt.count() > 0:
                for d in dpt:
                    usr = models.Dptstaff.objects.filter(dpt_id=d.dpt_id)
                    for u in usr:
                        if (u.staff_id != request.session.get('user_id')):
                            lststr.append(u.staff_id)
            all_rcd = all_rcd.filter(cust_staff__in=lststr)

        all_rcd = all_rcd.values().order_by('cust_id')
        all_rcd_num = all_rcd.count()
        paginator = Paginator(all_rcd, limit)
        page = int(int(offset) / int(limit) + 1)
        data = paginator.page(page)
        response_data = {'total': all_rcd_num, 'rows': []}
        for items in data:
            try:
                staff = models.Staff.objects.get(staff_id=items['cust_staff'])
            except:
                stfname = None
            else:
                stfname = staff.staff_name
            if lstty == '2':
                cars=models.CarOver.objects.filter(over_cust=items['cust_id'])
                if cars.count() > 0:
                    for car in cars:
                        carn = models.CarDocum.objects.get(docum_car_id=car.over_car, docum_type=2,
                                                           docum_item=1).docum_num
                        response_data['rows'].append({"cust_id": items['cust_id'],
                                                      "cust_name": items['cust_name'],
                                                      "cust_tel1": items['cust_tel1'],
                                                      "cust_tel2": items['cust_tel2'],
                                                      "cust_staff": stfname,
                                                      "cust_data": items['cust_edata'].strftime('%Y-%m-%d'),
                                                      "cust_car": carn,
                                                      "cust_car_id":car.over_car,
                                                      "cust_cont":car.over_cont,
                                                      "cust_car_date":car.over_date.strftime('%Y-%m-%d'),
                                                      })
            if lstty == '1':
                response_data['rows'].append({"cust_id": items['cust_id'],
                                              "cust_name": items['cust_name'],
                                              "cust_tel1": items['cust_tel1'],
                                              "cust_tel2": items['cust_tel2'],
                                              "cust_staff": stfname,
                                              "cust_data": items['cust_edata'].strftime('%Y-%m-%d'),
                                              "cust_sta": models.Stat.objects.get(type=3,
                                                                                  item=items['cust_status']).status
                                              })
            if lstty == '3':
                response_data['rows'].append({"cust_id": items['cust_id'],
                                              "cust_name": items['cust_name'],
                                              "cust_tel1": items['cust_tel1'],
                                              "cust_tel2": items['cust_tel2'],
                                              "cust_staff": stfname,
                                              "cust_data": items['cust_edata'].strftime('%Y-%m-%d'),
                                              "cust_gdate": items['cust_gdate'].strftime('%Y-%m-%d'),
                                              })
    return HttpResponse(json.dumps(response_data))


def general(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    request.session['chart_reque'] = echart_reque()
    request.session['chart_auto'] = echart_auto()
    request.session['chart_cust'] = echart_cust()
    return render(request, 'general.html', locals())


def echart_reque():
    v1 = [0]
    v2 = [0]
    v1[0] = models.CarHold.objects.filter(car_status__in=[2, 3, 9]).count()
    v2[0] = models.Cust.objects.filter(cust_status=3).count()

    style = Style()
    attr = [""]
    chart = Bar("", **style.init_style)
    chart.add("可订车辆", attr, v1)
    chart.add("等待客户", attr, v2, is_convert=True)
    return chart.render_embed()


def echart_auto():
    style = Style()
    attr = ["订购中", "上牌中", "仓储中", "维修中"]
    v = [0, 0, 0, 0]
    v[0] = models.CarHold.objects.filter(car_status=1).count()
    v[1] = models.CarHold.objects.filter(car_status=2).count()
    v[2] = models.CarHold.objects.filter(car_status=3).count()
    v[3] = models.CarHold.objects.filter(car_status=9).count()

    chart = Pie("", **style.init_style)
    chart.add("", attr, v, is_label_show=True)
    return chart.render_embed()


def echart_cust():
    style = Style()
    attr = ["意向客户", "提交审批", "审批通过", "审批拒绝", "用户退单"]
    v = [0, 0, 0, 0, 0]
    v[0] = models.Cust.objects.filter(cust_status=1).count()
    v[1] = models.Cust.objects.filter(cust_status=2).count()
    v[2] = models.Cust.objects.filter(cust_status=3).count()
    v[3] = models.Cust.objects.filter(cust_status=4).count()
    v[4] = models.Cust.objects.filter(cust_status=5).count()

    chart = Pie("", **style.init_style)
    chart.add("", attr, v, is_label_show=True)
    return chart.render_embed()
