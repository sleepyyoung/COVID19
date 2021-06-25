"""COVID19 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
import json
from django.contrib import admin
from django.shortcuts import render
from django.urls import path, re_path
from django.views import View
from app import views
import requests
from urllib.parse import urlencode
from COVID19.settings import *
from apscheduler.schedulers.background import BackgroundScheduler


class GetIndex(View):
    def get(self, request):
        provinces = PROVINCES
        countries = COUNTRIES
        last_update_time = mongo_china.find()[0]['map']['lastUpdateTime']
        return render(request, "index.html", locals())


class GetPie(View):
    def get(self, request):
        return render(request, "pie.html")


class GetGlobalTimeline(View):
    def get(self, request):
        return render(request, "global_timeline.html")


class GetChinaDetailTimeline(View):
    def get(self, request):
        return render(request, "china_detail_timeline.html")


class GetMigrationTimeline(View):
    def get(self, request):
        return render(request, "migration_timeline.html")


class GetLocalTrend(View):
    def get(self, request):
        return render(request, "local_trend.html")


class GetChinaTrend(View):
    def get(self, request):
        return render(request, "china_trend.html")


class GetCountryDetail(View):
    def get(self, request, country):
        return render(request, "country_detail.html", locals())


class GetProvinceDetail(View):
    def get(self, request, province):
        return render(request, "province_detail.html", locals())


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', GetIndex.as_view()),

    path('pie/', GetPie.as_view()),
    path('api/pie/', views.GetPie.as_view()),
    path('api/big-pie/', views.GetBigPie.as_view()),

    path('global-timeline/', GetGlobalTimeline.as_view()),
    path('api/global-timeline/', views.GetGlobalTimeline.as_view()),
    path('api/big-global-timeline/', views.GetBigGlobalTimeline.as_view()),

    path('china-detail-timeline/', GetChinaDetailTimeline.as_view()),
    path('api/china-detail-timeline/', views.GetChinaDetailTimeline.as_view()),
    path('api/big-china-detail-timeline/', views.GetBigChinaDetailTimeline.as_view()),

    path('migration-timeline/', GetMigrationTimeline.as_view()),
    path('api/migration-timeline/', views.GetMigrationTimeline.as_view()),
    path('api/big-migration-timeline/', views.GetBigMigrationTimeline.as_view()),

    path('local-trend/', GetLocalTrend.as_view()),
    path('api/local-trend/', views.GetLocalTrend.as_view()),
    path('api/big-local-trend/', views.GetBigLocalTrend.as_view()),

    path('china-trend/', GetChinaTrend.as_view()),
    path('api/china-trend/', views.GetChinaTrend.as_view()),
    path('api/big-china-trend/', views.GetBigChinaTrend.as_view()),

    re_path('api/country-detail/(?P<country>.*?)/', views.APICountryDetail.as_view()),
    re_path('country-detail/(?P<country>.*?)/', GetCountryDetail.as_view()),

    re_path('api/province-detail/(?P<province>.*?)/', views.APIProvinceDetail.as_view()),
    re_path('province-detail/(?P<province>.*?)/', GetProvinceDetail.as_view()),

    re_path('api/province-new/(?P<province>.*?)/', views.APIProvinceNew.as_view()),

    re_path('api/province-total/(?P<province>.*?)/', views.APIProvinceTotal.as_view()),

]


# 抓取中国疫情数据
def get_china_data():
    # mongo_china.insert_one({
    #     "country": "china",
    #     "map": json.loads(requests.get('https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5').json()['data']),
    #     "timeline": requests.get(
    #         'https://api.inews.qq.com/newsqa/v1/query/inner/publish/modules/list?modules=chinaDayList,chinaDayAddList,nowConfirmStatis,provinceCompare').json()[
    #         'data']})
    mongo_china.update_one({"country": "china"}, {"$set": {
        "country": "china",
        "map": json.loads(requests.get('https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5').json()['data']),
        "timeline": requests.get(
            'https://api.inews.qq.com/newsqa/v1/query/inner/publish/modules/list?modules=chinaDayList,chinaDayAddList,nowConfirmStatis,provinceCompare').json()[
            'data']}})


# 抓取各省疫情数据
def get_province_data():
    # for province in PROVINCES:
    #     mongo_provinces.insert_one({"data": requests.get(
    #         'https://api.inews.qq.com/newsqa/v1/query/pubished/daily/list?' + urlencode(
    #             {"province": province})).json()['data'], "province": province})
    for province in PROVINCES:
        mongo_provinces.update_one({"province": province}, {"$set": {"data": requests.get(
            'https://api.inews.qq.com/newsqa/v1/query/pubished/daily/list?' + urlencode(
                {"province": province})).json()['data'], "province": province}})


# 抓取迁徙数据
def get_migration_data():
    for i in [
        str(i).replace(" 00:00:00", "").replace("-", "") for i in
        pd.date_range(start="20200110", end="20200315", freq="D").tolist()]:
        datas = json.loads(
            requests.get(
                'https://huiyan.baidu.com/migration/cityrank.jsonp?',
                params={
                    'dt': 'city',
                    'id': '420100',
                    'type': 'move_out',
                    'date': i,
                },
                headers={
                    'User-Agent':
                        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.204 Safari/537.36',
                }).text[4:-1])
        for data in datas['data']['list']:
            city = data['city_name'].replace("市", "")
            province = data['province_name']
            ratio = data['value']
            # mongo_migration.insert_one({
            #     "date": i,
            #     "city": city,
            #     "province": province,
            #     "ratio": ratio
            # })
            mongo_migration.update_one({"date": i}, {"$set": {
                "date": i,
                "city": city,
                "province": province,
                "ratio": ratio
            }})


# 抓取世界各国疫情数据
def get_foreign_data():
    for i in world_name['中文'].tolist():
        foreign_data = requests.get(
            "https://api.inews.qq.com/newsqa/v1/automation/foreign/daily/list?" +
            urlencode({"country": i})).json()['data']
        if foreign_data is not None:
            # mongo_world.insert_one({
            #     "name": i,
            #     "data": foreign_data
            # })
            mongo_world.update_one({"name": i}, {"$set": {
                "name": i,
                "data": foreign_data
            }})


# 定时运行爬虫
def tick():
    get_china_data()
    get_province_data()
    # get_migration_data()
    get_foreign_data()


scheduler = BackgroundScheduler()
# 每10分钟执行一次
scheduler.add_job(tick, 'interval', seconds=600)
scheduler.start()
