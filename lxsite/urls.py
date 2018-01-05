"""lxsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from login import  views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',views.login),
    path('index/',views.general),
    path('logout/',views.logout),
    path('general/',views.general),
    path('carinfo/',views.carinfo),
    path('custinfo/',views.custinfo),
    path('mywork/',views.mywork),
    path('carinfo/getCarls/',views.getCarls),
    path('getBrand/',views.getBrand),
    path('getProd/',views.getProd),
    path('getSeries/',views.getSeries),
    path('carsBuy/',views.carsBuy),
    path('sndCarnum/',views.sndCarnum),
    path('getColor/',views.getColor),
    path('saveColor/',views.saveColor),
    path('getDpt/',views.getDpt),
    path('saveDpt/',views.saveDpt),
    path('getSit/',views.getSit),
    path('saveSit/',views.saveSit),
    path('sndDoc/',views.sndDoc),
    path('getDatil/',views.getDatil),
    path('custinfo/saveCust/',views.saveCust),
    path('custinfo/getCstls/',views.getCstls),
    path('custinfo/submitS/',views.submitS),
    path('savePwd/',views.savePwd),
    path('carinfo/sndJc/',views.sndJc),
    path('custinfo/getCust/',views.getCust),
    path('custinfo/dapCust/',views.dapCust),
    path('custinfo/saveGua/',views.saveGua),
    path('custinfo/getstf/',views.getstf),
    path('custinfo/getCstlog/',views.getCstlog),
]
