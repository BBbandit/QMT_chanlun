import chanlun
import kcharts
import pandas as pd
import logging
import os
import webbrowser
cpath_current = os.path.dirname(os.path.dirname(__file__))
from lib.qmtbt import QMTStore
from typing import Dict
import time
import akshare as ak

def query_stock_klines(symbol, period='1d', start_date: str = None, end_date: str = None, data_source=False) -> pd.DataFrame:
    """从QMT获取K线数据"""
    try:
        if data_source:
            # 日线数据
            res = QMTStore() ._fetch_history(# QMT获取历史数据
                symbol=symbol, period=period,
                start_time=start_date,
                end_time=end_date,
                dividend_type='front_ratio'
            )
            # 转换列名与格式
            df = res.rename(columns={
                'time': 'date', 'openPrice': 'open', 'highPrice': 'high',
                'lowPrice': 'low', 'closePrice': 'close', 'volume': 'volume',
                'amount': 'amount', 'preClose': 'preClose'
            })
            df['date'] = (
                pd.to_datetime(df['date'], unit='ms', utc=True)  # 1. 按UTC解析时间戳
                .dt.tz_convert('Asia/Shanghai')  # 2. 转换为上海时区
                .dt.tz_localize(None)  # 3. 移除时区信息
            )

            # 校准日期：如果时间在15:00（收盘时间）之后，日期+1天（针对夜盘数据）
            df['date'] = df['date'].apply(
                lambda x: x + pd.Timedelta(days=1) if x.hour >= 15 else x
            )
            return df[['date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'preClose']]

        else:
            code_parts = symbol.split('.')
            if len(code_parts) != 2 or code_parts[1].upper() not in ['SH', 'SZ']:
                print(f"股票代码格式不正确: {symbol}")
                return pd.DataFrame()
            exchange = code_parts[1].lower()  # 转换为小写，例如 'sh' 或 'sz'
            akshare_symbol = f"{exchange}{code_parts[0]}"
            res = ak.stock_zh_a_daily(
                symbol=akshare_symbol,
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
            # 转换列名与格式
            df = res.rename(columns={
                'date': 'date', 'open': 'open', 'high': 'high',
                'low': 'low', 'close': 'close', 'volume': 'volume',
                'amount': 'amount', 'outstanding_share': 'preClose'
            })
            return df[['date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'preClose']]

    except Exception as e:
        logging.error(f"数据获取失败: {str(e)}")
        return pd.DataFrame()


def run_single_stock(code = '600678.SH', start_date: str = None, end_date: str = None, data_source = False):
    klines: Dict[str, pd.DataFrame] = {}

    try:
        # 获取各周期K线数据
        for f in ['d']:
            if f != 'd':
                logging.warning(f"暂不支持 {f} 周期，已跳过")
                continue

            df = query_stock_klines(code, '1d',start_date = start_date, end_date = end_date, data_source = data_source)
            if df.empty:
                continue

            logging.info(f"周期 {f} 获取 {len(df)} 条K线数据，耗时 {time.time() - time.time():.2f}s")
            klines[f] = df

        # 批量计算缠论数据
        if not klines:
            logging.error("无有效K线数据，任务终止")
            return

        cl_datas = chanlun.batch_cls(code, klines)
        for i, cd in enumerate(cl_datas):
            title = f"{code} - 【{cd.frequency}】周期缠论图表"
            chart = kcharts.render_charts(title, cd)

            # 生成HTML文件
            html_path = f'cl_chart_{i}.html'
            chart.render(html_path)  # 直接调用图表对象的render方法
            webbrowser.open(os.path.abspath(html_path))

    except Exception as e:
        logging.error(f"主流程执行失败: {str(e)}", exc_info=True)



if __name__ == "__main__":
    #code 带市场后缀，时间按照以下格式填写，data_source 如果有开通QMT则打开QMT 然后填True，如果没有开通QMT 则填False，使用开源的akshare数据源
    run_single_stock(code = '600678.SH',start_date ='20230101' ,end_date = '20250524', data_source = True)



