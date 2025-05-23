import datetime
import os

import numpy as np
import pandas as pd
# 画图配置
from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar, Grid, Scatter
from pyecharts.commons.utils import JsCode
import chanlun

if "JPY_PARENT_PID" in os.environ:
    from pyecharts.globals import CurrentConfig, NotebookType

    CurrentConfig.NOTEBOOK_TYPE = NotebookType.JUPYTER_LAB
    Kline().load_javascript()
    Line().load_javascript()
    Bar().load_javascript()
    Grid().load_javascript()
    Scatter().load_javascript()


def render_charts(title, cl_data: chanlun.CL, show_num=320, orders=[]):
    """
    缠论数据图表化展示
    :param title:
    :param cl_data:
    :param show_num:
    :param orders:
    :return:
    """
    klines = cl_data.klines
    fxs = cl_data.fxs
    bis = cl_data.bis
    xds = cl_data.xds
    zss = cl_data.zss
    idx = cl_data.idx

    range_start = 0
    if len(klines) > show_num:
        range_start = 100 - (show_num / len(klines)) * 100

    # 重新整理Kline数据
    klines_yaxis = []
    klines_xaxis = []
    klines_vols = []

    # 找到顶和底的坐标
    point_ding = {'index': [], 'val': []}
    point_di = {'index': [], 'val': []}

    for k in klines:
        klines_xaxis.append(k.date)
        # 开/收/低/高
        klines_yaxis.append([k.o, k.c, k.l, k.h])
        klines_vols.append(k.a)

    for fx in fxs:
        if fx.type == 'ding':
            point_ding['index'].append(fx.k.date)
            point_ding['val'].append(fx.val)
        else:
            point_di['index'].append(fx.k.date)
            point_di['val'].append(fx.val)

    # 画 笔
    line_bis = {'index': [], 'val': []}
    if len(bis) > 0:
        line_bis['index'].append(bis[0].start.k.date)
        line_bis['val'].append(bis[0].start.val)
    for b in bis:
        line_bis['index'].append(b.end.k.date)
        line_bis['val'].append(b.end.val)

    # 画 线段
    line_xds = {'index': [], 'val': []}
    if len(xds) > 0:
        line_xds['index'].append(xds[0].start.k.date)
        line_xds['val'].append(xds[0].start.val)
    for x in xds:
        line_xds['index'].append(x.start.k.date)
        line_xds['val'].append(x.start.val)

    # 画 笔中枢
    line_bi_zss = []
    for zs in zss:
        start_index = zs.start.k.date
        end_index = zs.end.k.date
        l_zs = [
            # 两竖，两横，5个点，转一圈
            [start_index, start_index, end_index, end_index, start_index],
            [zs.zg, zs.zd, zs.zd, zs.zg, zs.zg],
        ]
        if zs.type == 'up':
            l_zs.append('#FF6666')
        elif zs.type == 'down':
            l_zs.append('#0099CC')
        else:
            l_zs.append('#CCCCCC')

        line_bi_zss.append(l_zs)

    # 画 背驰
    point_bi_bcs = {'i': [], 'val': []}  # 笔背驰
    for bi in bis:
        bc_lable = ''
        bc_is = bi.pz_beichi or bi.qs_beichi
        if bi.qs_beichi:
            bc_lable += '笔趋势背驰 / '
        if bi.pz_beichi:
            bc_lable += '笔盘整背驰 / '

        if bc_is:
            point_bi_bcs['i'].append(bi.end.k.date)
            point_bi_bcs['val'].append([bi.end.val, bc_lable])

    # 画买卖点
    _mmd_maps = {'1buy': '一买', '2buy': '二买', 'l2buy': '类二买', '3buy': '三买', 'l3buy': '类三买',
                 '1sell': '一卖', '2sell': '二卖', 'l2sell': '类二卖', '3sell': '三卖', 'l3sell': '类三卖'}
    scatter_buy = {'i': [], 'val': []}
    scatter_sell = {'i': [], 'val': []}
    for bi in bis:
        mmd_buy_label = ''
        mmd_sell_label = ''

        buy_point_lable = ''
        sell_point_lable = ''
        for bs in bi.mmds:
            if bs in ['1buy', '2buy', '3buy', 'l2buy', 'l3buy']:
                buy_point_lable += '笔' + _mmd_maps[bs] + ' - '

            if bs in ['1sell', '2sell', '3sell', 'l2sell', 'l3sell']:
                sell_point_lable += '笔' + _mmd_maps[bs] + ' - '

        if buy_point_lable != '':
            mmd_buy_label += buy_point_lable + ' / '
        if sell_point_lable != '':
            mmd_sell_label += sell_point_lable + ' / '

        if mmd_buy_label != '':
            scatter_buy['i'].append(bi.end.k.date)
            scatter_buy['val'].append([bi.end.val, mmd_buy_label])
        if mmd_sell_label != '':
            scatter_sell['i'].append(bi.end.k.date)
            scatter_sell['val'].append([bi.end.val, mmd_sell_label])

    # 画订单记录
    scatter_buy_orders = {'i': [], 'val': []}
    scatter_sell_orders = {'i': [], 'val': []}
    if orders:
        for o in orders:
            if type(o['datetime']) == 'str':
                odt = o['datetime']
            else:
                odt = datetime.datetime.strptime(o['datetime'], '%Y-%m-%d %H:%M:%S')
            if odt < klines[0].date:
                continue
            if o['type'] == 'buy':
                scatter_buy_orders['i'].append(odt)
                scatter_buy_orders['val'].append(
                    [o['price'], str(o['price']) + ' - 买入:' + ('' if 'info' not in o else o['info'])])
            elif o['type'] == 'sell':
                scatter_sell_orders['i'].append(odt)
                scatter_sell_orders['val'].append(
                    [o['price'], str(o['price']) + ' - 卖出:' + ('' if 'info' not in o else o['info'])])

    klines = (
        Kline()
            .add_xaxis(xaxis_data=klines_xaxis)
            .add_yaxis(
            series_name="",
            y_axis=klines_yaxis,
            itemstyle_opts=opts.ItemStyleOpts(
                color='#FF6600',
                color0='#009966',
                border_color="#FF6600",
                border_color0="#009966",
            ),
            # markline_opts=opts.MarkLineOpts(
            #     data=[opts.MarkLineItem(name='Close', symbol='none', symbol_size=0, x=kline_xaxis[-1],
            #                             y=kline[-1]['c'])]
            # ),
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title=title, pos_left="0"),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                is_scale=True,
                axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
                axislabel_opts=opts.LabelOpts(is_show=False),
                split_number=20,
                min_="dataMin",
                max_="dataMax",
            ),
            yaxis_opts=opts.AxisOpts(
                is_scale=True, splitline_opts=opts.SplitLineOpts(is_show=True, ), position="right",
                axislabel_opts=opts.LabelOpts(is_show=False),
                axisline_opts=opts.AxisLineOpts(is_show=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis", axis_pointer_type="line"),
            datazoom_opts=[
                opts.DataZoomOpts(is_show=False, type_="inside", xaxis_index=[0, 0], range_start=range_start,
                                  range_end=100),
                opts.DataZoomOpts(is_show=True, xaxis_index=[0, 1], pos_top="97%", range_start=range_start,
                                  range_end=100),
                opts.DataZoomOpts(is_show=False, xaxis_index=[0, 2], range_start=range_start, range_end=100),
            ],
        )
    )

    # 画顶底分型
    fenxing_ding = (
        Scatter()
            .add_xaxis(point_ding['index'])
            .add_yaxis(
            "顶",
            point_ding['val'],
            itemstyle_opts=opts.ItemStyleOpts(color='red'),
            symbol_size=2,
            label_opts=opts.LabelOpts(is_show=False))
    )
    fenxing_di = (
        Scatter()
            .add_xaxis(point_di['index'])
            .add_yaxis(
            "底",
            point_di['val'],
            itemstyle_opts=opts.ItemStyleOpts(color='green'),
            symbol_size=2,
            label_opts=opts.LabelOpts(is_show=False))
    )
    overlap_kline = klines.overlap(fenxing_ding)
    overlap_kline = overlap_kline.overlap(fenxing_di)

    # 画 笔
    line_bi = (
        Line()
            .add_xaxis(line_bis['index'])
            .add_yaxis(
            "笔",
            line_bis['val'],
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(width=1, color='#426ab3'),
        )
    )
    overlap_kline = overlap_kline.overlap(line_bi)

    # 画 线段
    line_xd = (
        Line()
            .add_xaxis(line_xds['index'])
            .add_yaxis(
            "线段",
            line_xds['val'],
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(width=3, type_='dashed', color='#FF9966')
        )
    )
    overlap_kline = overlap_kline.overlap(line_xd)

    # # 画 指标线
    # line_idx = (
    #     Line()
    #         .add_xaxis(xaxis_data=klines_xaxis)
    #         .add_yaxis(
    #         series_name="BOLL",
    #         is_symbol_show=False,
    #         y_axis=idx['boll']['up'],
    #         linestyle_opts=opts.LineStyleOpts(width=1, color='#99CC99'),
    #         label_opts=opts.LabelOpts(is_show=False),
    #     ).add_yaxis(
    #         series_name="BOLL",
    #         is_symbol_show=False,
    #         y_axis=idx['boll']['mid'],
    #         linestyle_opts=opts.LineStyleOpts(width=1, color='#FF6D00'),
    #         label_opts=opts.LabelOpts(is_show=False),
    #     ).add_yaxis(
    #         series_name="BOLL",
    #         is_symbol_show=False,
    #         y_axis=idx['boll']['low'],
    #         linestyle_opts=opts.LineStyleOpts(width=1, color='#99CC99'),
    #         label_opts=opts.LabelOpts(is_show=False),
    #     ).set_global_opts()
    # )
    # overlap_kline = overlap_kline.overlap(line_idx)

    # 画 笔中枢
    for zs in line_bi_zss:
        line_zs = (
            Line()
                .add_xaxis(zs[0])
                .add_yaxis(
                "中枢",
                zs[1],
                symbol=None,
                label_opts=opts.LabelOpts(is_show=False),
                linestyle_opts=opts.LineStyleOpts(width=2, color=zs[2]),
                tooltip_opts=opts.TooltipOpts(is_show=False),
            )
        )
        overlap_kline = overlap_kline.overlap(line_zs)

    # 画 笔背驰
    scatter_bi_bc_tu = (
        Scatter()
            .add_xaxis(xaxis_data=point_bi_bcs['i'])
            .add_yaxis(
            series_name="BI背驰",
            y_axis=point_bi_bcs['val'],
            symbol_size=10,
            symbol='circle',
            itemstyle_opts=opts.ItemStyleOpts(color='#df9464'),
            label_opts=opts.LabelOpts(is_show=False),
            tooltip_opts=opts.TooltipOpts(
                textstyle_opts=opts.TextStyleOpts(font_size=24),
                formatter=JsCode(
                    "function (params) {return params.value[2];}"
                )
            ),
        )
    )
    overlap_kline = overlap_kline.overlap(scatter_bi_bc_tu)

    # 画买卖点
    scatter_buy_tu = (
        Scatter()
            .add_xaxis(xaxis_data=scatter_buy['i'])
            .add_yaxis(
            series_name="买点",
            y_axis=scatter_buy['val'],
            symbol_size=20,
            symbol='arrow',
            itemstyle_opts=opts.ItemStyleOpts(color='red'),
            tooltip_opts=opts.TooltipOpts(
                textstyle_opts=opts.TextStyleOpts(font_size=24),
                formatter=JsCode(
                    "function (params) {return params.value[2];}"
                )
            ),
        )
    )
    scatter_sell_tu = (
        Scatter()
            .add_xaxis(xaxis_data=scatter_sell['i'])
            .add_yaxis(
            series_name="卖点",
            y_axis=scatter_sell['val'],
            symbol_size=20,
            symbol='arrow',
            symbol_rotate=180,
            itemstyle_opts=opts.ItemStyleOpts(color='green'),
            tooltip_opts=opts.TooltipOpts(
                textstyle_opts=opts.TextStyleOpts(font_size=24),
                formatter=JsCode(
                    "function (params) {return params.value[2];}"
                )
            ),
        )
    )
    overlap_kline = overlap_kline.overlap(scatter_buy_tu)
    overlap_kline = overlap_kline.overlap(scatter_sell_tu)

    # 画订单记录
    if orders and len(orders) > 0:
        scatter_buy_orders_tu = (
            Scatter()
                .add_xaxis(xaxis_data=scatter_buy_orders['i'])
                .add_yaxis(
                series_name="买卖点",
                y_axis=scatter_buy_orders['val'],
                symbol_size=15,
                symbol='diamond',
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color='rgba(255,20,147,0.5)'),
                tooltip_opts=opts.TooltipOpts(
                    textstyle_opts=opts.TextStyleOpts(font_size=24),
                    formatter=JsCode(
                        "function (params) {return params.value[2];}"
                    )
                ),
            )
        )
        overlap_kline = overlap_kline.overlap(scatter_buy_orders_tu)
        scatter_sell_orders_tu = (
            Scatter()
                .add_xaxis(xaxis_data=scatter_sell_orders['i'])
                .add_yaxis(
                series_name="买卖点",
                y_axis=scatter_sell_orders['val'],
                symbol_size=15,
                symbol='diamond',
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color='rgba(0,191,255,0.5)'),
                tooltip_opts=opts.TooltipOpts(
                    textstyle_opts=opts.TextStyleOpts(font_size=24),
                    formatter=JsCode(
                        "function (params) {return params.value[2];}"
                    )
                ),
            )
        )
        overlap_kline = overlap_kline.overlap(scatter_sell_orders_tu)

    # 成交量
    bar_vols = (
        Bar()
            .add_xaxis(xaxis_data=klines_xaxis)
            .add_yaxis(
            series_name="Volumn",
            y_axis=klines_vols,
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(color='rgba(236,55,59,0.5)'),
        )
        #     .set_global_opts(
        #     legend_opts=opts.LegendOpts(is_show=True),
        #     xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(is_show=False), ),
        #     yaxis_opts=opts.AxisOpts(
        #         position="right",
        #         axislabel_opts=opts.LabelOpts(is_show=False),
        #         axisline_opts=opts.AxisLineOpts(is_show=False),
        #         axistick_opts=opts.AxisTickOpts(is_show=False),
        #     ),
        # )
    )

    # MACD
    bar_macd = (
        Bar()
            .add_xaxis(xaxis_data=klines_xaxis)
            .add_yaxis(
            series_name="MACD",
            y_axis=list(idx['macd']['hist']),
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(
                color=JsCode('function(p){var c;if (p.data >= 0) {c = \'#ef232a\';} else {c = \'#14b143\';}return c;}')
            ),
        )
            .set_global_opts(
            legend_opts=opts.LegendOpts(is_show=False),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(is_show=False), ),
            yaxis_opts=opts.AxisOpts(
                position="right",
                axislabel_opts=opts.LabelOpts(is_show=False),
                axisline_opts=opts.AxisLineOpts(is_show=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
            ),
        )
    )

    line_macd_dif = (
        Line()
            .add_xaxis(xaxis_data=klines_xaxis)
            .add_yaxis(
            series_name="DIF",
            y_axis=idx['macd']['dif'],
            is_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(color='#fe832d'),
        )
            .add_yaxis(
            series_name="DEA",
            y_axis=idx['macd']['dea'],
            is_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(color='#f5a4df'),
        )
            .set_global_opts(
            legend_opts=opts.LegendOpts(is_show=True),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(is_show=False), ),
            yaxis_opts=opts.AxisOpts(position="right",
                                     axislabel_opts=opts.LabelOpts(is_show=False),
                                     axisline_opts=opts.AxisLineOpts(is_show=False),
                                     axistick_opts=opts.AxisTickOpts(is_show=False)),
        )
    )

    # 最下面的柱状图和折线图
    macd_bar_line = bar_macd.overlap(line_macd_dif)

    # 最后的 Grid
    grid_chart = Grid(init_opts=opts.InitOpts(width="100%", height="800px"))

    grid_chart.add(
        overlap_kline,
        grid_opts=opts.GridOpts(width="96%", height="60%", pos_left='1%', pos_right='3%'),
    )

    # Volumn 柱状图
    grid_chart.add(
        bar_vols,
        grid_opts=opts.GridOpts(
            pos_top="60%", height="10%", width="96%", pos_left='1%', pos_right='3%'
        ),
    )

    # MACD 柱状图
    grid_chart.add(
        macd_bar_line,
        grid_opts=opts.GridOpts(
            pos_top="70%", height="30%", width="96%", pos_left='1%', pos_right='3%'
        ),
    )
    if "JPY_PARENT_PID" in os.environ:
        return grid_chart.render_notebook()
    else:
        return grid_chart


def render_cash(balance_history):
    """
    展示资产变化
    :param balance_history:
    :return:
    """
    history = pd.DataFrame(balance_history)
    history['datetime'] = history['datetime'].map(lambda d: d.strftime('%Y-%m-%d %H:%M:%S'))
    return (
        Line()
            .add_xaxis(xaxis_data=np.array(history['datetime']).tolist())
            .add_yaxis("净资产", np.array(history['net_asset']).tolist(), label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            datazoom_opts=[
                opts.DataZoomOpts(
                    is_realtime=True,
                    type_="inside",
                    start_value='90%',
                    end_value='100%',
                )
            ])
    ).render_notebook()
