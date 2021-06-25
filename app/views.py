import re
import json
from django.http import HttpResponse
from django.views import View
from pyecharts.globals import ChartType, SymbolType
from rest_framework.views import APIView
from pyecharts.charts import Pie, Map, Timeline, Geo, Line
from pyecharts import options as opts
from COVID19.settings import *


def response_as_json(data):
    json_str = json.dumps(data)
    response = HttpResponse(json_str, content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    return response


def json_response(data, code=200):
    data = {
        "code": code,
        "msg": "success",
        "data": data,
    }
    return response_as_json(data)


def json_error(error_string="error", code=500, **kwargs):
    data = {
        "code": code,
        "msg": error_string,
        "data": {}
    }
    data.update(kwargs)
    return response_as_json(data)


JsonResponse = json_response
JsonError = json_error

# data = json.loads(requests.get('https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5').json()['data'])
china_data = mongo_china.find()[0]['map']

chinaTotal = china_data['chinaTotal']
chinaTotal['累计确诊'] = chinaTotal['confirm']
chinaTotal['累计死亡'] = chinaTotal['dead']
chinaTotal['累计治愈'] = chinaTotal['heal']
chinaTotal['现有确诊'] = chinaTotal['nowConfirm']
chinaTotal['境外输入'] = chinaTotal['importedCase']
chinaTotal['无症状'] = chinaTotal['noInfect']
chinaTotal['本土现有确诊'] = chinaTotal['localConfirm']
del chinaTotal['confirm']
del chinaTotal['dead']
del chinaTotal['heal']
del chinaTotal['nowConfirm']
del chinaTotal['importedCase']
del chinaTotal['noInfect']
del chinaTotal['localConfirm']
del chinaTotal['suspect']
del chinaTotal['nowSevere']
del chinaTotal['showLocalConfirm']
del chinaTotal['showlocalinfeciton']
del chinaTotal['noInfectH5']
del chinaTotal['localConfirmH5']

chinaAdd = china_data['chinaAdd']
chinaAdd['新增累计确诊'] = chinaAdd['confirm']
chinaAdd['新增现有确诊'] = chinaAdd['nowConfirm']
chinaAdd['新增疑似'] = chinaAdd['suspect']
chinaAdd['新增累计死亡'] = chinaAdd['dead']
chinaAdd['新增治愈'] = chinaAdd['heal']
chinaAdd['新增本土现有确诊'] = chinaAdd['localConfirm']
chinaAdd['新增无症状'] = chinaAdd['noInfect']
chinaAdd['新增境外输入'] = chinaAdd['importedCase']
del chinaAdd['confirm']
del chinaAdd['nowConfirm']
del chinaAdd['suspect']
del chinaAdd['dead']
del chinaAdd['heal']
del chinaAdd['localConfirm']
del chinaAdd['noInfect']
del chinaAdd['importedCase']
del chinaAdd['nowSevere']
del chinaAdd['noInfectH5']
del chinaAdd['localConfirmH5']


def total_pie() -> Pie:
    return Pie().add(
        series_name="",
        data_pair=[list(z) for z in zip(chinaTotal.keys(), chinaTotal.values())],
        center=["50%", "60%"],
        radius=[75, 100], ).add(
        series_name="",
        data_pair=[list(z) for z in zip(chinaAdd.keys(), chinaAdd.values())],
        center=["50%", "60%"],
        radius=[0, 50]).set_global_opts(
        title_opts=opts.TitleOpts(
            title="国内疫情现状",
            title_link="/pie",
            title_target="blank",
            subtitle="点击查看详情",
            subtitle_link="/pie",
            subtitle_target="blank",
            pos_bottom="0",
            title_textstyle_opts=opts.TextStyleOpts(
                color="#F8F8FF")),
        legend_opts=opts.LegendOpts(
            textstyle_opts=opts.TextStyleOpts(
                color="#FFFFFF"))).set_series_opts(
        label_opts=opts.LabelOpts(
            formatter="{b}:{c}")).dump_options_with_quotes()


class GetPie(APIView):
    def get(self, request):
        return JsonResponse(json.loads(total_pie()))


def big_total_pie() -> Pie:
    return Pie().add(
        series_name="",
        data_pair=[list(z) for z in zip(chinaTotal.keys(), chinaTotal.values())],
        center=["50%", "50%"],
        radius=[200, 300]).add(
        series_name="",
        data_pair=[list(z) for z in zip(chinaAdd.keys(), chinaAdd.values())],
        center=["50%", "50%"],
        radius=[0, 50]).set_global_opts(
        title_opts=opts.TitleOpts(
            title="国内疫情现状",
            pos_bottom="0",
            title_textstyle_opts=opts.TextStyleOpts(
                font_size=60))).set_series_opts(
        label_opts=opts.LabelOpts(
            formatter="{b}:{c}")).dump_options_with_quotes()


class GetBigPie(APIView):
    def get(self, request):
        return JsonResponse(json.loads(big_total_pie()))


global_list = []
results = mongo_world.find()
for result in results:
    global_list.append({
        '国家': result['name'],
        '累计确诊': result['data'][-1]['confirm'],
        '累计死亡': result['data'][-1]['dead'],
        '累计治愈': result['data'][-1]['heal'],
    })

global_list.append({
    '国家': '中国',
    '累计确诊': chinaTotal['累计确诊'],
    '累计死亡': chinaTotal['累计死亡'],
    '累计治愈': chinaTotal['累计治愈'],
})

global_data = pd.merge(
    pd.DataFrame(global_list),
    world_name,
    left_on="国家",
    right_on="中文",
    how="inner")[["国家", "累计确诊", "累计死亡", "累计治愈", "英文", "中文"]]

confirm_world_map = (Map().add(
    series_name="",
    data_pair=[list(z) for z in zip(list(global_data["英文"]), list(global_data["累计确诊"]))],
    maptype="world",
    zoom=1.3,
    is_map_symbol_show=False).set_series_opts(
    label_opts=opts.LabelOpts(
        is_show=False),
    toolbox_opts=opts.ToolboxOpts(
        orient='vertical',
        pos_right="10%")).set_global_opts(
    title_opts=opts.TitleOpts(
        title="全球累计确诊数量地图",
        title_link="/global-timeline",
        title_target="blank",
        subtitle="点击查看详情",
        subtitle_link="/global-timeline",
        subtitle_target="blank",
        pos_top='5%',
        title_textstyle_opts=opts.TextStyleOpts(
            color="#F8F8FF")),
    visualmap_opts=opts.VisualMapOpts(
        is_piecewise=False,
        max_=10000000,
        textstyle_opts=opts.TextStyleOpts(
            color="#F5FFFA"))))

dead_world_map = (Map().add(
    series_name="",
    data_pair=[list(z) for z in zip(list(global_data["英文"]), list(global_data["累计死亡"]))],
    maptype="world",
    zoom=1.3,
    is_map_symbol_show=False).set_series_opts(
    label_opts=opts.LabelOpts(
        is_show=False),
    toolbox_opts=opts.ToolboxOpts(
        orient='vertical',
        pos_right="10%")).set_global_opts(
    title_opts=opts.TitleOpts(
        title="全球累计死亡数量地图",
        title_link="/global-timeline",
        title_target="blank",
        subtitle="点击查看详情",
        subtitle_link="/global-timeline",
        subtitle_target="blank",
        pos_top='5%',
        title_textstyle_opts=opts.TextStyleOpts(
            color="#F8F8FF")),
    visualmap_opts=opts.VisualMapOpts(
        is_piecewise=False,
        max_=500000,
        textstyle_opts=opts.TextStyleOpts(
            color="#F5FFFA"))))

heal_world_map = (Map().add(
    series_name="",
    data_pair=[list(z) for z in zip(list(global_data["英文"]), list(global_data["累计治愈"]))],
    maptype="world",
    zoom=1.3,
    is_map_symbol_show=False).set_series_opts(
    label_opts=opts.LabelOpts(
        is_show=False),
    toolbox_opts=opts.ToolboxOpts(
        orient='vertical',
        pos_right="10%")).set_global_opts(
    title_opts=opts.TitleOpts(
        title="全球累计治愈数量地图",
        title_link="/global-timeline",
        title_target="blank",
        subtitle="点击查看详情",
        subtitle_link="/global-timeline",
        subtitle_target="blank",
        pos_top='5%',
        title_textstyle_opts=opts.TextStyleOpts(
            color="#F8F8FF")),
    visualmap_opts=opts.VisualMapOpts(
        is_piecewise=False,
        max_=20000000,
        textstyle_opts=opts.TextStyleOpts(
            color="#F5FFFA"))))


def global_timeline() -> Timeline:
    return (Timeline().add_schema(
        play_interval=2000,
        is_auto_play=True,
        width='70%',
        height='10%',
        pos_left='center',
        linestyle_opts=opts.LineStyleOpts(),
        label_opts=opts.LabelOpts(
            position='bottom',
            color="white")).add(
        confirm_world_map, "全球累计确诊").add(
        dead_world_map, "全球累计死亡").add(
        heal_world_map, "全球累计治愈")).dump_options_with_quotes()


class GetGlobalTimeline(APIView):
    def get(self, request):
        return JsonResponse(json.loads(global_timeline()))


big_confirm_world_map = (Map().add(
    series_name="",
    data_pair=[list(z) for z in zip(list(global_data["英文"]), list(global_data["累计确诊"]))],
    maptype="world",
    is_map_symbol_show=False).set_series_opts(
    label_opts=opts.LabelOpts(
        is_show=False),
    toolbox_opts=opts.ToolboxOpts(
        orient='vertical',
        pos_right="10%")).set_global_opts(
    title_opts=opts.TitleOpts(
        title_textstyle_opts=opts.TextStyleOpts(
            font_size=40),
        title="全球累计确诊数量地图"),
    visualmap_opts=opts.VisualMapOpts(
        is_piecewise=False,
        max_=10000000)))

big_dead_world_map = (Map().add(
    series_name="",
    data_pair=[list(z) for z in zip(list(global_data["英文"]), list(global_data["累计死亡"]))],
    maptype="world",
    is_map_symbol_show=False).set_series_opts(
    label_opts=opts.LabelOpts(
        is_show=False),
    toolbox_opts=opts.ToolboxOpts(
        orient='vertical',
        pos_right="10%")).set_global_opts(
    title_opts=opts.TitleOpts(
        title_textstyle_opts=opts.TextStyleOpts(
            font_size=40),
        title="全球累计死亡数量地图"),
    visualmap_opts=opts.VisualMapOpts(
        is_piecewise=False,
        max_=500000)))

big_heal_world_map = (Map().add(
    series_name="",
    data_pair=[list(z) for z in zip(list(global_data["英文"]), list(global_data["累计治愈"]))],
    maptype="world",
    is_map_symbol_show=False).set_series_opts(
    label_opts=opts.LabelOpts(
        is_show=False),
    toolbox_opts=opts.ToolboxOpts(
        orient='vertical',
        pos_right="10%")).set_global_opts(
    title_opts=opts.TitleOpts(
        title_textstyle_opts=opts.TextStyleOpts(
            font_size=40),
        title="全球累计治愈数量地图", ),
    visualmap_opts=opts.VisualMapOpts(
        is_piecewise=False,
        max_=20000000)))


def big_global_timeline() -> Timeline:
    return (Timeline().add_schema(
        play_interval=2000,
        is_auto_play=True,
        width='70%',
        height='10%',
        pos_left='center',
        linestyle_opts=opts.LineStyleOpts(),
        label_opts=opts.LabelOpts(
            position='bottom')).add(
        big_confirm_world_map, "全球累计确诊").add(
        big_dead_world_map, "全球累计死亡").add(
        big_heal_world_map, "全球累计治愈")).dump_options_with_quotes()


class GetBigGlobalTimeline(APIView):
    def get(self, request):
        return JsonResponse(json.loads(big_global_timeline()))


# china_data = json.loads(
#     re.search("jQuery\d+_\d+\((.*?)\)", requests.get(
#         "https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5&callback=jQuery35105166268218631691_1624330960369"
#     ).text).group(1))['data']

china_detail = pd.DataFrame(columns=("省份", "累计确诊", "累计死亡", "累计治愈", "死亡率", "治愈率"))
for i in china_data['areaTree'][0]['children']:
    china_detail = china_detail.append(pd.Series({
        "省份": i['name'],
        "累计确诊": i['total']['confirm'],
        "累计死亡": i['total']['dead'],
        "累计治愈": i['total']['heal'],
        "死亡率": i['total']['deadRate'],
        "治愈率": i['total']['healRate'],
    }), ignore_index=True)

confirm_china_map = (Map().add(
    series_name="",
    data_pair=[list(z) for z in zip(list(china_detail["省份"]), list(china_detail["累计确诊"]))],
    maptype="china",
    is_map_symbol_show=False,
    label_opts=opts.LabelOpts(
        color="#fff"),
    tooltip_opts=opts.TooltipOpts(
        is_show=True),
    center=[105, 35]).set_series_opts(
    label_opts=opts.LabelOpts(
        is_show=False)).set_global_opts(
    title_opts=opts.TitleOpts(
        title="中国疫情分布图 - 累计确诊",
        title_link="/china-detail-timeline",
        title_target="blank",
        subtitle="点击查看详情",
        subtitle_link="/china-detail-timeline",
        subtitle_target="blank",
        title_textstyle_opts=opts.TextStyleOpts(
            color="#F8F8FF")),
    visualmap_opts=opts.VisualMapOpts(
        is_piecewise=False,
        max_=2000,
        pos_right="0",
        pos_bottom="0",
        textstyle_opts=opts.TextStyleOpts(
            color="#F5FFFA"))))

dead_china_map = (Map().add(
    series_name="",
    data_pair=[list(z) for z in zip(list(china_detail["省份"]), list(china_detail["累计死亡"]))],
    maptype="china",
    is_map_symbol_show=False,
    label_opts=opts.LabelOpts(
        color="#fff"),
    tooltip_opts=opts.TooltipOpts(
        is_show=True),
    center=[105, 35]).set_series_opts(
    label_opts=opts.LabelOpts(
        is_show=False)).set_global_opts(
    title_opts=opts.TitleOpts(
        title="中国疫情分布图 - 累计死亡",
        title_link="/china-detail-timeline",
        title_target="blank",
        subtitle="点击查看详情",
        subtitle_link="/china-detail-timeline",
        subtitle_target="blank",
        title_textstyle_opts=opts.TextStyleOpts(
            color="#F8F8FF")),
    visualmap_opts=opts.VisualMapOpts(
        is_piecewise=False,
        max_=10,
        pos_right="0",
        pos_bottom="0",
        textstyle_opts=opts.TextStyleOpts(
            color="#F5FFFA"))))

heal_china_map = (Map().add(
    series_name="",
    data_pair=[list(z) for z in zip(list(china_detail["省份"]), list(china_detail["累计治愈"]))],
    maptype="china",
    is_map_symbol_show=False,
    label_opts=opts.LabelOpts(
        color="#fff"),
    tooltip_opts=opts.TooltipOpts(
        is_show=True),
    center=[105, 35]).set_series_opts(
    label_opts=opts.LabelOpts(
        is_show=False)).set_global_opts(
    title_opts=opts.TitleOpts(
        title="中国疫情分布图 - 累计治愈",
        title_link="/china-detail-timeline",
        title_target="blank",
        subtitle="点击查看详情",
        subtitle_link="/china-detail-timeline",
        subtitle_target="blank",
        title_textstyle_opts=opts.TextStyleOpts(
            color="#F8F8FF")),
    visualmap_opts=opts.VisualMapOpts(
        is_piecewise=False,
        max_=1000,
        pos_right="0",
        pos_bottom="0",
        textstyle_opts=opts.TextStyleOpts(
            color="#F5FFFA"))))

dead_rate_china_map = (Map().add(
    series_name="",
    data_pair=[list(z) for z in zip(list(china_detail["省份"]), list(china_detail["死亡率"]))],
    maptype="china",
    is_map_symbol_show=False,
    label_opts=opts.LabelOpts(
        color="#fff"),
    tooltip_opts=opts.TooltipOpts(
        is_show=True),
    center=[105, 35]).set_series_opts(
    label_opts=opts.LabelOpts(
        formatter="{b}:{c}%",
        is_show=False)).set_global_opts(
    title_opts=opts.TitleOpts(
        title="中国疫情分布图 - 死亡率",
        title_link="/china-detail-timeline",
        title_target="blank",
        subtitle="点击查看详情",
        subtitle_link="/china-detail-timeline",
        subtitle_target="blank",
        title_textstyle_opts=opts.TextStyleOpts(
            color="#F8F8FF")),
    visualmap_opts=opts.VisualMapOpts(
        is_piecewise=False,
        max_=6,
        pos_right="0",
        pos_bottom="0",
        textstyle_opts=opts.TextStyleOpts(
            color="#F5FFFA"))))

heal_rate_china_map = (Map().add(
    series_name="",
    data_pair=[list(z) for z in zip(list(china_detail["省份"]), list(china_detail["治愈率"]))],
    maptype="china",
    is_map_symbol_show=False,
    label_opts=opts.LabelOpts(
        color="#fff"),
    tooltip_opts=opts.TooltipOpts(
        is_show=True),
    center=[105, 35]).set_series_opts(
    label_opts=opts.LabelOpts(
        formatter="{b}:{c}%", is_show=False)).set_global_opts(
    title_opts=opts.TitleOpts(
        title="中国疫情分布图 - 治愈率",
        title_link="/china-detail-timeline",
        title_target="blank",
        subtitle="点击查看详情",
        subtitle_link="/china-detail-timeline",
        subtitle_target="blank",
        title_textstyle_opts=opts.TextStyleOpts(
            color="#F8F8FF")),
    visualmap_opts=opts.VisualMapOpts(
        is_piecewise=False,
        max_=100,
        min_=90,
        pos_right="0",
        pos_bottom="0",
        textstyle_opts=opts.TextStyleOpts(
            color="#F5FFFA"))))


def china_detail_timeline() -> Timeline:
    return (Timeline().add_schema(
        play_interval=2000,
        is_auto_play=True,
        width='70%',
        height='10%',
        pos_left='center',
        linestyle_opts=opts.LineStyleOpts(),
        label_opts=opts.LabelOpts(
            position='bottom',
            color="white")).add(
        confirm_china_map, "累计确诊").add(
        dead_china_map, "累计死亡").add(
        heal_china_map, "累计治愈").add(
        dead_rate_china_map, "死亡率").add(
        heal_rate_china_map, "治愈率")).dump_options_with_quotes()


class GetChinaDetailTimeline(APIView):
    def get(self, request):
        return JsonResponse(json.loads(china_detail_timeline()))


big_confirm_china_map = (Map().add(
    series_name="",
    data_pair=[list(z) for z in zip(list(china_detail["省份"]), list(china_detail["累计确诊"]))],
    maptype="china",
    is_map_symbol_show=False,
    label_opts=opts.LabelOpts(
        color="#fff"),
    tooltip_opts=opts.TooltipOpts(
        is_show=True),
    center=[105, 35]).set_series_opts(
    label_opts=opts.LabelOpts(
        formatter="{b}:{c}",
        is_show=False)).set_global_opts(
    title_opts=opts.TitleOpts(
        title="中国疫情分布图 - 累计确诊",
        title_textstyle_opts=opts.TextStyleOpts(
            font_size=40)),
    visualmap_opts=opts.VisualMapOpts(
        is_piecewise=False,
        max_=2000,
        pos_right="0",
        pos_bottom="0")))

big_dead_china_map = (Map().add(
    series_name="",
    data_pair=[list(z) for z in zip(list(china_detail["省份"]), list(china_detail["累计死亡"]))],
    maptype="china",
    is_map_symbol_show=False,
    label_opts=opts.LabelOpts(
        color="#fff"),
    tooltip_opts=opts.TooltipOpts(
        is_show=True),
    center=[105, 35]).set_series_opts(
    label_opts=opts.LabelOpts(
        formatter="{b}:{c}",
        is_show=False)).set_global_opts(
    title_opts=opts.TitleOpts(
        title="中国疫情分布图 - 累计死亡",
        title_textstyle_opts=opts.TextStyleOpts(
            font_size=40)),
    visualmap_opts=opts.VisualMapOpts(
        is_piecewise=False,
        max_=10,
        pos_right="0",
        pos_bottom="0")))

big_heal_china_map = (Map().add(
    series_name="",
    data_pair=[list(z) for z in zip(list(china_detail["省份"]), list(china_detail["累计治愈"]))],
    maptype="china",
    is_map_symbol_show=False,
    label_opts=opts.LabelOpts(
        color="#fff"),
    tooltip_opts=opts.TooltipOpts(
        is_show=True),
    center=[105, 35]).set_series_opts(
    label_opts=opts.LabelOpts(
        formatter="{b}:{c}",
        is_show=False)).set_global_opts(
    title_opts=opts.TitleOpts(
        title="中国疫情分布图 - 累计治愈",
        title_textstyle_opts=opts.TextStyleOpts(
            font_size=40)),
    visualmap_opts=opts.VisualMapOpts(
        is_piecewise=False,
        max_=1000,
        pos_right="0",
        pos_bottom="0")))

big_dead_rate_china_map = (Map().add(
    series_name="",
    data_pair=[list(z) for z in zip(list(china_detail["省份"]), list(china_detail["死亡率"]))],
    maptype="china",
    is_map_symbol_show=False,
    label_opts=opts.LabelOpts(
        color="#fff"),
    tooltip_opts=opts.TooltipOpts(
        is_show=True),
    center=[105, 35]).set_series_opts(
    label_opts=opts.LabelOpts(
        formatter="{b}:{c}%",
        is_show=False)).set_global_opts(
    title_opts=opts.TitleOpts(
        title="中国疫情分布图 - 死亡率",
        title_textstyle_opts=opts.TextStyleOpts(
            font_size=40)),
    visualmap_opts=opts.VisualMapOpts(
        is_piecewise=False,
        max_=6,
        pos_right="0",
        pos_bottom="0")))

big_heal_rate_china_map = (Map().add(
    series_name="",
    data_pair=[list(z) for z in zip(list(china_detail["省份"]), list(china_detail["治愈率"]))],
    maptype="china",
    is_map_symbol_show=False,
    label_opts=opts.LabelOpts(
        color="#fff"),
    tooltip_opts=opts.TooltipOpts(
        is_show=True),
    center=[105, 35]).set_series_opts(
    label_opts=opts.LabelOpts(
        formatter="{b}:{c}%",
        is_show=False)).set_global_opts(
    title_opts=opts.TitleOpts(
        title="中国疫情分布图 - 治愈率",
        title_textstyle_opts=opts.TextStyleOpts(
            font_size=40)),
    visualmap_opts=opts.VisualMapOpts(
        is_piecewise=False,
        max_=100,
        min_=90,
        pos_right="0",
        pos_bottom="0")))


def big_china_detail_timeline() -> Timeline:
    return (Timeline().add_schema(
        play_interval=2000,
        is_auto_play=True,
        width='70%',
        height='10%',
        pos_left='center',
        linestyle_opts=opts.LineStyleOpts(),
        label_opts=opts.LabelOpts(
            position='bottom')).add(
        big_confirm_china_map, "累计确诊").add(
        big_dead_china_map, "累计死亡").add(
        big_heal_china_map, "累计治愈").add(
        big_dead_rate_china_map, "死亡率").add(
        big_heal_rate_china_map, "治愈率")).dump_options_with_quotes()


class GetBigChinaDetailTimeline(APIView):
    def get(self, request):
        return JsonResponse(json.loads(big_china_detail_timeline()))


def migration_timeline() -> Timeline:
    migration_timeline = (Timeline().add_schema(
        play_interval=1000,
        is_auto_play=True,
        width='70%',
        height='10%',
        pos_left='center',
        linestyle_opts=opts.LineStyleOpts(),
        label_opts=opts.LabelOpts(
            position='bottom',
            color="white")))

    for date in [str(i).replace(" 00:00:00", "").replace("-", "") for i in
                 pd.date_range(start="20200110", end="20200315", freq="D").tolist()]:
        migration_timeline.add((Geo().add_schema(
            maptype="china",
            itemstyle_opts=opts.ItemStyleOpts(
                color="#FFF0F5",
                border_color="#111")).add(
            series_name="",
            data_pair=[("武汉", _['city']) for _ in mongo_migration.find({"date": date})],
            type_=ChartType.LINES,
            effect_opts=opts.EffectOpts(
                symbol=SymbolType.ARROW,
                symbol_size=6,
                color="blue"),
            linestyle_opts=opts.LineStyleOpts(
                curve=0.2)).set_series_opts(
            label_opts=opts.LabelOpts(
                is_show=False)).set_global_opts(
            title_opts=opts.TitleOpts(
                title="武汉市人员流动图 - " + date[:4] + "-" + date[4:6] + "-" + date[6:8],
                title_link="/migration-timeline",
                title_target="blank",
                subtitle="点击查看详情",
                subtitle_link="/migration-timeline",
                subtitle_target="blank",
                title_textstyle_opts=opts.TextStyleOpts(
                    color="	#F8F8FF")))),
            date[:4] + "-" + date[4:6] + "-" + date[6:8])

    return migration_timeline.dump_options_with_quotes()


class GetMigrationTimeline(APIView):
    def get(self, request):
        return JsonResponse(json.loads(migration_timeline()))


def big_migration_timeline() -> Timeline:
    migration_timeline = (Timeline().add_schema(
        play_interval=1000,
        is_auto_play=True,
        width='70%',
        height='10%',
        pos_left='center',
        linestyle_opts=opts.LineStyleOpts(),
        label_opts=opts.LabelOpts(
            position='bottom',
            color="white")))

    for date in [str(i).replace(" 00:00:00", "").replace("-", "") for i in
                 pd.date_range(start="20200110", end="20200315", freq="D").tolist()]:
        migration_timeline.add((Geo().add_schema(
            maptype="china",
            itemstyle_opts=opts.ItemStyleOpts(
                color="#FFF0F5",
                border_color="#111")).add(
            series_name="",
            data_pair=[("武汉", _['city']) for _ in mongo_migration.find({"date": date})],
            type_=ChartType.LINES,
            effect_opts=opts.EffectOpts(
                symbol=SymbolType.ARROW,
                symbol_size=6,
                color="blue"),
            linestyle_opts=opts.LineStyleOpts(
                curve=0.2)).set_series_opts(
            label_opts=opts.LabelOpts(
                is_show=True)).set_global_opts(
            title_opts=opts.TitleOpts(
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=40),
                title="武汉市人员流动图 - " + date[:4] + "-" + date[4:6] + "-" + date[6:8]))),
            date[:4] + "-" + date[4:6] + "-" + date[6:8]).add_schema(
            label_opts=opts.LabelOpts(
                position='bottom'))

    return migration_timeline.dump_options_with_quotes()


class GetBigMigrationTimeline(APIView):
    def get(self, request):
        return JsonResponse(json.loads(big_migration_timeline()))


# china_timeline = requests.get(
#     'https://api.inews.qq.com/newsqa/v1/query/inner/publish/modules/list?modules=chinaDayList,chinaDayAddList,nowConfirmStatis,provinceCompare'
# ).json()['data']
china_timeline = mongo_china.find()[0]['timeline']
china_day_add_list = china_timeline['chinaDayAddList']

china_day_add_list_date = []  # 日期
china_day_add_list_confirm = []  # 全国新增确诊
china_day_add_list_suspect = []  # 全国新增疑似
china_day_add_list_local_confirm = []  # 本土新增确诊
for i in china_day_add_list:
    china_day_add_list_date.append(i['date'])
    china_day_add_list_local_confirm.append(i['localConfirmadd'])
    china_day_add_list_confirm.append(i['confirm'])
    china_day_add_list_suspect.append(i['suspect'])

local_new_confirm_line = (Line().add_xaxis(
    xaxis_data=china_day_add_list_date).add_yaxis(
    series_name="本土新增确诊趋势",
    y_axis=china_day_add_list_local_confirm,
    is_smooth=True).set_series_opts(
    label_opts=opts.LabelOpts(
        is_show=False)).set_global_opts(
    legend_opts=opts.LegendOpts(
        textstyle_opts=opts.TextStyleOpts(
            color="white")),
    title_opts=opts.TitleOpts(
        title="本土新增确诊趋势",
        subtitle="点击查看详情",
        title_link="/local-trend",
        title_target="blank",
        subtitle_link="/local-trend",
        subtitle_target="blank",
        title_textstyle_opts=opts.TextStyleOpts(
            color="white")),
    yaxis_opts=opts.AxisOpts(
        axisline_opts=opts.AxisLineOpts(
            linestyle_opts=opts.LineStyleOpts(
                color="white"))),
    xaxis_opts=opts.AxisOpts(
        axisline_opts=opts.AxisLineOpts(
            linestyle_opts=opts.LineStyleOpts(
                color="white")))))

china_day_list = china_timeline['chinaDayList']
china_add_line = (
    Line().add_xaxis(
        xaxis_data=china_day_add_list_date).add_yaxis(
        is_smooth=True,
        series_name="新增确诊",
        y_axis=china_day_add_list_confirm).add_yaxis(
        is_smooth=True,
        series_name="新增疑似",
        y_axis=china_day_add_list_suspect).set_global_opts(
        legend_opts=opts.LegendOpts(
            pos_left="0",
            textstyle_opts=opts.TextStyleOpts(
                color="white")),
        yaxis_opts=opts.AxisOpts(
            name="人",
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(
                    color="white"))),
        xaxis_opts=opts.AxisOpts(
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(
                    color="white"))),
        title_opts=opts.TitleOpts(
            title="全国疫情新增趋势",
            pos_right="0")).set_series_opts(
        label_opts=opts.LabelOpts(
            is_show=False)))

china_day_list_date = []  # 日期
china_day_list_confirm = []  # 累计确诊
china_day_list_heal = []  # 累计治愈
china_day_list_dead = []  # 累计死亡
china_day_list_now_confirm = []  # 全国现有确诊
china_day_list_heal_rate = []  # 治愈率
china_day_list_dead_rate = []  # 病死率
china_day_list_local_confirm = []  # 本土现有确诊

for i in china_day_list:
    china_day_list_date.append(i['date'])
    china_day_list_confirm.append(i['confirm'])
    china_day_list_heal.append(i['heal'])
    china_day_list_dead.append(i['dead'])
    china_day_list_now_confirm.append(i['nowConfirm'])
    china_day_list_heal_rate.append(i['healRate'])
    china_day_list_dead_rate.append(i['deadRate'])
    china_day_list_local_confirm.append(i['localConfirm'])

china_merge_confirm_line = (
    Line().add_xaxis(
        xaxis_data=china_day_add_list_date).add_yaxis(
        is_smooth=True,
        series_name="累计确诊",
        y_axis=china_day_list_confirm).add_yaxis(
        is_smooth=True,
        series_name="累计治愈",
        y_axis=china_day_list_heal).add_yaxis(
        is_smooth=True,
        series_name="累计死亡",
        y_axis=china_day_list_dead).set_global_opts(
        legend_opts=opts.LegendOpts(
            pos_left="0",
            textstyle_opts=opts.TextStyleOpts(
                color="white")),
        yaxis_opts=opts.AxisOpts(
            name="人",
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(
                    color="white"))),
        xaxis_opts=opts.AxisOpts(
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(
                    color="white"))),
        title_opts=opts.TitleOpts(
            title="全国疫情累计趋势",
            pos_right="0")).set_series_opts(
        label_opts=opts.LabelOpts(
            is_show=False)))

china_now_confirm_line = (
    Line().add_xaxis(
        xaxis_data=china_day_list_date).add_yaxis(
        series_name="现有确诊",
        y_axis=china_day_list_now_confirm,
        label_opts=opts.LabelOpts(
            is_show=False)).set_series_opts(
        label_opts=opts.LabelOpts(
            is_show=False)).set_global_opts(
        legend_opts=opts.LegendOpts(
            pos_left="0",
            textstyle_opts=opts.TextStyleOpts(
                color="white")),
        yaxis_opts=opts.AxisOpts(
            name="人",
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(
                    color="white"))),
        xaxis_opts=opts.AxisOpts(
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(
                    color="white"))),
        title_opts=opts.TitleOpts(
            title="全国现有确诊趋势",
            pos_right="0",
            subtitle="点击查看详情",
            title_link="/china-trend",
            title_target="blank",
            subtitle_link="/china-trend",
            subtitle_target="blank",
            title_textstyle_opts=opts.TextStyleOpts(
                color="white"))))

rate_line = (
    Line().add_xaxis(
        xaxis_data=china_day_add_list_date).add_yaxis(
        is_smooth=True,
        series_name="治愈率",
        y_axis=china_day_list_heal_rate).add_yaxis(
        is_smooth=True,
        series_name="病死率",
        y_axis=china_day_list_dead_rate).set_global_opts(
        legend_opts=opts.LegendOpts(
            pos_left="0",
            textstyle_opts=opts.TextStyleOpts(
                color="white")),
        yaxis_opts=opts.AxisOpts(
            name="%",
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(
                    color="white"))),
        xaxis_opts=opts.AxisOpts(
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(
                    color="white"))),
        title_opts=opts.TitleOpts(
            title="治愈率/病死率",
            pos_right="0")).set_series_opts(
        label_opts=opts.LabelOpts(
            is_show=False)))

local_now_confirm_line = (
    Line().add_xaxis(
        xaxis_data=china_day_add_list_date).add_yaxis(
        is_smooth=True,
        series_name="本土现有确诊",
        y_axis=china_day_list_local_confirm).set_global_opts(
        legend_opts=opts.LegendOpts(
            textstyle_opts=opts.TextStyleOpts(
                color="white")),
        title_opts=opts.TitleOpts(
            title="本土现有确诊趋势",
            subtitle="点击查看详情",
            title_link="/local-trend",
            title_target="blank",
            subtitle_link="/local-trend",
            subtitle_target="blank",
            title_textstyle_opts=opts.TextStyleOpts(
                color="white"))).set_series_opts(
        label_opts=opts.LabelOpts(
            is_show=False)))


def local_trend() -> Timeline:
    return (Timeline().add_schema(
        play_interval=2000,
        is_auto_play=True,
        width='70%',
        height='10%',
        pos_left='center',
        linestyle_opts=opts.LineStyleOpts(),
        label_opts=opts.LabelOpts(
            position='bottom',
            color="white")).add(
        local_new_confirm_line, "本土新增确诊趋势").add(
        local_now_confirm_line, "本土现有确诊趋势")).dump_options_with_quotes()


class GetLocalTrend(APIView):
    def get(self, request):
        return JsonResponse(json.loads(local_trend()))


def china_trend() -> Timeline:
    return (Timeline().add_schema(
        play_interval=2000,
        is_auto_play=True,
        width='70%',
        height='10%',
        pos_left='center',
        label_opts=opts.LabelOpts(
            position='bottom',
            color="white")).add(
        china_now_confirm_line, "现有").add(
        china_add_line, "新增").add(
        china_merge_confirm_line, "累计").add(
        rate_line, "率")).dump_options_with_quotes()


class GetChinaTrend(APIView):
    def get(self, request):
        return JsonResponse(json.loads(china_trend()))


big_local_new_confirm_line = (Line().add_xaxis(
    xaxis_data=china_day_add_list_date).add_yaxis(
    series_name="本土新增确诊",
    y_axis=china_day_add_list_local_confirm,
    is_smooth=True).set_series_opts(
    label_opts=opts.LabelOpts(
        is_show=False)).set_global_opts(
    title_opts=opts.TitleOpts(
        title="本土新增确诊趋势",
        title_textstyle_opts=opts.TextStyleOpts(
            font_size=30))))

big_china_add_line = (
    Line().add_xaxis(
        xaxis_data=china_day_add_list_date).add_yaxis(
        is_smooth=True,
        series_name="新增确诊",
        y_axis=china_day_add_list_confirm).add_yaxis(
        is_smooth=True,
        series_name="新增疑似",
        y_axis=china_day_add_list_suspect).set_global_opts(
        yaxis_opts=opts.AxisOpts(
            name="人"),
        title_opts=opts.TitleOpts(
            title="全国疫情新增趋势")).set_series_opts(
        legend_opts=opts.LegendOpts(
            pos_left="left",
            pos_top="5%",
            orient="vertical"),
        label_opts=opts.LabelOpts(
            is_show=False)))

big_china_merge_confirm_line = (
    Line().add_xaxis(
        xaxis_data=china_day_add_list_date).add_yaxis(
        is_smooth=True, series_name="累计确诊",
        y_axis=china_day_list_confirm).add_yaxis(
        is_smooth=True, series_name="累计治愈",
        y_axis=china_day_list_heal).add_yaxis(
        is_smooth=True,
        series_name="累计死亡",
        y_axis=china_day_list_dead).set_global_opts(
        yaxis_opts=opts.AxisOpts(
            name="人"),
        title_opts=opts.TitleOpts(
            title="全国疫情累计趋势"),
        legend_opts=opts.LegendOpts(
            pos_left="left",
            pos_top="5%",
            orient="vertical")).set_series_opts(
        label_opts=opts.LabelOpts(
            is_show=False)))

big_china_now_confirm_line = (
    Line().add_xaxis(xaxis_data=china_day_list_date).add_yaxis(
        series_name="现有确诊",
        y_axis=china_day_list_now_confirm,
        label_opts=opts.LabelOpts(
            is_show=False)).set_series_opts(
        label_opts=opts.LabelOpts(
            is_show=False)).set_global_opts(
        yaxis_opts=opts.AxisOpts(
            name="人"),
        title_opts=opts.TitleOpts(
            title="全国现有确诊趋势"),
        legend_opts=opts.LegendOpts(
            pos_left="left",
            pos_top="5%",
            orient="vertical")))

big_rate_line = (
    Line().add_xaxis(xaxis_data=china_day_add_list_date).add_yaxis(
        is_smooth=True,
        series_name="治愈率",
        y_axis=china_day_list_heal_rate).add_yaxis(
        is_smooth=True,
        series_name="病死率",
        y_axis=china_day_list_dead_rate).set_global_opts(
        yaxis_opts=opts.AxisOpts(
            name="%"),
        title_opts=opts.TitleOpts(
            title="治愈率/病死率"),
        legend_opts=opts.LegendOpts(
            pos_left="left",
            pos_top="5%",
            orient="vertical")).set_series_opts(
        label_opts=opts.LabelOpts(
            is_show=False)))

big_local_now_confirm_line = (
    Line().add_xaxis(
        xaxis_data=china_day_add_list_date).add_yaxis(
        is_smooth=True,
        series_name="本土现有确诊",
        y_axis=china_day_list_local_confirm).
        set_global_opts(
        title_opts=opts.TitleOpts(
            title="本土现有确诊趋势",
            title_textstyle_opts=opts.TextStyleOpts(
                font_size=30))).set_series_opts(
        label_opts=opts.LabelOpts(
            is_show=False)))


def big_local_trend() -> Timeline:
    return (Timeline().add_schema(
        play_interval=2000,
        is_auto_play=True,
        width='10%',
        height='10%',
        pos_right='1%',
        pos_top="1%",
        orient="vertical",
        linestyle_opts=opts.LineStyleOpts(),
        label_opts=opts.LabelOpts(
            position='top')).add(
        big_local_new_confirm_line, "本土新增确诊趋势").add(
        big_local_now_confirm_line, "本土现有确诊趋势")).dump_options_with_quotes()


class GetBigLocalTrend(APIView):
    def get(self, request):
        return JsonResponse(json.loads(big_local_trend()))


def big_china_trend() -> Timeline:
    return (Timeline().add_schema(
        play_interval=2000,
        is_auto_play=True,
        width='70%',
        height='10%',
        pos_left='25%',
        pos_top="1%",
        linestyle_opts=opts.LineStyleOpts(),
        label_opts=opts.LabelOpts(
            position='top')).add(
        big_china_now_confirm_line, "全国现有确诊趋势").add(
        big_china_add_line, "全国疫情新增趋势").add(
        big_china_merge_confirm_line, "全国疫情累计趋势").add(
        big_rate_line, "治愈率/病死率")).dump_options_with_quotes()


class GetBigChinaTrend(APIView):
    def get(self, request):
        return JsonResponse(json.loads(big_china_trend()))


def get_data_by_country_name(country):
    country_trend_date = []  # 日期
    country_trend_confirm_add = []  # 新增确诊
    country_trend_confirm = []  # 累计确诊
    country_trend_heal = []  # 累计治愈
    country_trend_dead = []  # 累计死亡
    for i in mongo_world.find({"name": country})[0]['data']:
        country_trend_date.append(i['y'] + "-" + i['date'].replace(".", "-"))
        country_trend_confirm_add.append(i['confirm_add'])
        country_trend_confirm.append(i['confirm'])
        country_trend_heal.append(i['heal'])
        country_trend_dead.append(i['dead'])
    return country_trend_date, country_trend_confirm_add, country_trend_confirm, country_trend_heal, country_trend_dead


def country_detail(country) -> Line:
    d = get_data_by_country_name(country)
    return (Line()
        .add_xaxis(d[0])
        .add_yaxis("新增确诊", d[1])
        .add_yaxis("累计确诊", d[2])
        .add_yaxis("累计治愈", d[3])
        .add_yaxis("累计死亡", d[4])
        .set_global_opts(
        title_opts=opts.TitleOpts(
            title=country + "疫情趋势"),
        datazoom_opts=opts.DataZoomOpts(
            range_start=0,
            range_end=100))).dump_options_with_quotes()


class APICountryDetail(View):
    def get(self, request, country):
        return JsonResponse(json.loads(country_detail(re.findall(".*?【(.*?)】.*?", country)[0])))


def get_map_data_by_province_name(province):
    cities = []  # 市
    today_now_confirm = []  # 现有确诊
    total_confirm = []  # 累计确诊
    p = None
    for i in china_data['areaTree'][0]['children']:
        if i['name'] == province:
            p = i
    if p['name'] == "上海":
        for i in p['children']:
            if i['name'] != "境外输入" and (i['name'] != "地区待确认") and (i['name'] != "境外来沪") and (i['name'] != "外地来沪"):
                cities.append(i['name'] + ("区" if i['name'] != "浦东" else "新区"))
                today_now_confirm.append(i['total']['nowConfirm'])
                total_confirm.append(i['total']['confirm'])
    elif p['name'] == "天津":
        for i in p['children']:
            if i['name'] != "境外输入" and (i['name'] != "外地来津"):
                cities.append(i['name'])
                today_now_confirm.append(i['total']['nowConfirm'])
                total_confirm.append(i['total']['confirm'])
    elif p['name'] == "北京":
        for i in p['children']:
            if i['name'] != "境外输入" and (i['name'] != "地区待确认"):
                cities.append(i['name'] + "区")
                today_now_confirm.append(i['total']['nowConfirm'])
                total_confirm.append(i['total']['confirm'])
    elif p['name'] == "重庆":
        for i in p['children']:
            if i['name'] != "境外输入":
                if i['name'] == "秀山县":
                    cities.append("秀山土家族苗族自治县")
                elif i['name'] == "酉阳县":
                    cities.append("酉阳土家族苗族自治县")
                elif i['name'] == "彭水县":
                    cities.append("彭水苗族土家族自治县")
                elif i['name'] == "武隆区":
                    cities.append("武隆县")
                elif i['name'] == "梁平区":
                    cities.append("梁平县")
                elif i['name'] == "石柱县":
                    cities.append("石柱土家族自治县")
                else:
                    cities.append(i['name'])
                today_now_confirm.append(i['total']['nowConfirm'])
                total_confirm.append(i['total']['confirm'])
    else:
        for i in p['children']:
            if i['name'] != "境外输入" and (i['name'] != "地区待确认"):
                cities.append(i['name'] + ("市" if i['name'] != "大兴安岭" else "地区"))
                today_now_confirm.append(i['total']['nowConfirm'])
                total_confirm.append(i['total']['confirm'])
    return cities, today_now_confirm, total_confirm


def province_detail(province) -> Timeline:
    p = get_map_data_by_province_name(province)
    cities = p[0]
    today_now_confirm = p[1]
    total_confirm = p[2]
    today_now_confirm_map = (Map().add(
        province + "现有确诊", [list(z) for z in zip(cities, today_now_confirm)],
        province).set_global_opts(
        visualmap_opts=opts.VisualMapOpts(
            is_piecewise=False,
            max_=int((max(today_now_confirm) + 1) * 1.1)),
        title_opts=opts.TitleOpts(title=province + "现有确诊")))
    total_confirm_map = (Map().add(
        province + "累计确诊", [list(z) for z in zip(cities, total_confirm)],
        province).set_global_opts(
        visualmap_opts=opts.VisualMapOpts(
            is_piecewise=False,
            max_=int((max(total_confirm) + 1) * 1.1)
        ),
        title_opts=opts.TitleOpts(title=province + "累计确诊")))
    province_timeline = (Timeline()).add_schema(
        play_interval=2000,
        is_auto_play=True,
        width='70%',
        height='10%',
        pos_left='center',
        linestyle_opts=opts.LineStyleOpts(),
        label_opts=opts.LabelOpts(position='bottom')).add(
        today_now_confirm_map, "现有确诊").add(total_confirm_map, "累计确诊")
    return province_timeline.dump_options_with_quotes()


class APIProvinceDetail(View):
    def get(self, request, province):
        return JsonResponse(json.loads(province_detail(province)))


def get_line_data_by_province_name(province):
    dates = []  # 时间
    province_new_confirm = []  # 新增确诊
    province_new_heal = []  # 新增治愈
    province_new_dead = []  # 新增死亡
    province_total_confirm = []  # 累计确诊
    province_total_heal = []  # 累计治愈
    province_total_dead = []  # 累计死亡

    # for i in requests.get(
    #         'https://api.inews.qq.com/newsqa/v1/query/pubished/daily/list?' + urlencode(
    #             {"province": province})).json()['data']:
    for i in mongo_provinces.find_one({"province": province})['data']:
        dates.append(str(i['year']) + "-" + i['date'].replace(".", "-"))
        province_new_confirm.append(i['newConfirm'])
        province_new_heal.append(i['newHeal'])
        province_new_dead.append(i['newDead'])
        province_total_confirm.append(i['confirm'])
        province_total_heal.append(i['heal'])
        province_total_dead.append(i['dead'])
    return dates, province_new_confirm, province_new_heal, province_new_dead, province_total_confirm, province_total_heal, province_total_dead


def province_new(province) -> Line:
    p = get_line_data_by_province_name(province)
    return (Line().add_xaxis(p[0]).add_yaxis(
        "新增确诊趋势", p[1],
        is_smooth=True).add_yaxis(
        "新增治愈趋势", p[2],
        is_smooth=True).add_yaxis(
        "新增死亡趋势", p[3],
        is_smooth=True).set_series_opts(
        label_opts=opts.LabelOpts(
            is_show=False)).set_global_opts(
        datazoom_opts=opts.DataZoomOpts(
            range_start=0,
            range_end=100),
        title_opts=opts.TitleOpts(
            title=province + "新增趋势"))).dump_options_with_quotes()


class APIProvinceNew(View):
    def get(self, request, province):
        return JsonResponse(json.loads(province_new(province)))


def province_total(province) -> Line:
    p = get_line_data_by_province_name(province)
    return (Line().add_xaxis(p[0]).add_yaxis(
        "累计确诊趋势", p[4],
        is_smooth=True).add_yaxis(
        "累计治愈趋势", p[5],
        is_smooth=True).add_yaxis(
        "累计死亡趋势", p[6],
        is_smooth=True).set_series_opts(
        label_opts=opts.LabelOpts(
            is_show=False)).set_global_opts(
        datazoom_opts=opts.DataZoomOpts(
            range_start=0,
            range_end=100),
        title_opts=opts.TitleOpts(
            title=province + "累计趋势"))).dump_options_with_quotes()


class APIProvinceTotal(View):
    def get(self, request, province):
        return JsonResponse(json.loads(province_total(province)))
