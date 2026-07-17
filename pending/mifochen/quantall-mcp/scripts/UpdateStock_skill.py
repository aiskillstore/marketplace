"""
【目的】创建和更新全市场的本地股票数据，
【背景说明】本人为了能秒算全市场5000+股票，制作了软件‘全A解析’，其需要全市场数据。
进而为给‘全A解析’配套数据方案，开发了本skill，旨在帮用户创建和管理全市场的股票数据。
【补充】软件全A解析也制作成skill，可以安装QuantAll技能或者用随文件安装和启动技能调用
"""
import os, sys, json, re, time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import duckdb
import tushare as ts
import baostock as bs
import socket
from mcp.server.fastmcp import FastMCP, Context
from typing import Annotated
from pydantic import Field



class Updb:
    def __init__(self, db_path = ".\\Test.duckdb"):
        # 默认是适配软件全A解析的设置，加载失败使用自定义路径db_path
        path = os.path.dirname(__file__)  
        option_path = os.path.join(path,"DB_setting.json") 
        if os.path.isfile(option_path):
            # 软件【全A解析】的设置文件，里面存储当前使用的数据库信息。
            # 单独使用该脚本时，默认不存在该设置文件，不会触发该选项
            with open(option_path,'r',encoding='utf-8') as file:
                fd:dict = json.load(file)
        else:
            fd: dict = {}
        self.db_path = fd.get("db_path", db_path) # 数据库的路径
        self.st_tab = fd.get('stock','stock')
        self.st_map = fd.get("map_stock",{})
        self.id_tab = fd.get("stock_index","stock_index")
        self.id_map = fd.get("map_stock_index",{})
        self.basic_tab =  fd.get("stock_basic","stock_basic")
        self.basic_map = fd.get("map_stock_basic",{})
        self.factor_tab = fd.get("stock_factor","stock_factor")
        self.factor_map = fd.get("map_stock_factor",{})
        self.forecast_tab = fd.get("stock_forecast","stock_forecast")
        self.forecast_map = fd.get("map_stock_forecast",{})
        self.dividend_tab = fd.get("stock_dividend","stock_dividend")
        self.dividend_map = fd.get("map_stock_dividend",{})
        self.report_tab = fd.get("stock_report","stock_report")
        self.report_map = fd.get("map_stock_report",{})

        with duckdb.connect(self.db_path) as conn:
            # 第一步检查table_date表是否存在，不存在传教table_date表
            conn.execute("""
            CREATE TABLE IF NOT EXISTS table_date (
                table_name STRING,          -- 表格
                update_date DATE,         -- 更新日期
                PRIMARY KEY (table_name)
            );
            """)
            self.table_date = {"stock_forecast":None,
                               "stock_dividend":None,
                               "stock_report":None}
            # 从 table_date 表读取已记录的更新日期
            rows = conn.execute(
                "SELECT table_name, update_date FROM table_date"
            ).fetchall()
            for table_name, update_date in rows:
                if table_name in self.table_date:
                    self.table_date[table_name] = update_date

        self.exist_stocks = []
        self.count_stocks = 0
        # 读取上证指数最新交易日，作为写入 table_date 的日期基准
        self.update_date = self.date_stock_index("000001")

    def write_table_date(self, table_name: str):
        """写入 table_date 记录（skip 路径也需要记录，避免下次重复扫描）。"""
        with duckdb.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO table_date (table_name, update_date) VALUES (?, ?)",
                [table_name, self.update_date]
            )
        self.table_date[table_name] = self.update_date

    def date_stock_index(self, symbol):
        """获取数据库中指定指数的最新交易日。"""
        symbol = ''.join(re.findall(r'\d', symbol))
        gp_col = self.id_map.get("symbol","symbol")
        td_col = self.id_map.get("trade_date","trade_date")
        with duckdb.connect(self.db_path) as conn:
            last_date = conn.execute(f"SELECT MAX({td_col}) FROM {self.id_tab} "
                                    f"WHERE {gp_col}='{symbol}'").fetchone()[0]
            if last_date is None:
                last_date = conn.execute(f"SELECT MIN({td_col}) FROM {self.id_tab} "
                                     ).fetchone()[0]
        return last_date

    def update_stock_index(self,df:pd.DataFrame)->str:
        """更新指数数据，日线"""
        try:
            # 检测df的列名是否正常
            col_default = ["trade_date","symbol","open","high","low","close","pre_close","vol","voe"]
            if not all(col in df.columns for col in col_default):
                return f"数据缺少必要列，必要的列名：{col_default}"
            # 规范symbol列，值保留6为数值，不包含sh\sz之类的
            df.loc[:, 'symbol'] = self.norm_symbol(df['symbol'])
            df['trade_date'] = df['trade_date'].astype(object)  # 新的pandas版本str不再是object
            df.loc[:,'trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce').dt.date
            # 删除无法识别的错误日期
            df = df.dropna(subset=['trade_date'])
            # 去重提取，提取含有的指数代码
            symbols = df['symbol'].unique().tolist()
            # 增加对名称不一致的支持，转换到数据库的名称
            df.rename(columns=self.id_map, inplace=True)
            
            conn = duckdb.connect(self.db_path)
            # 检测数据库的列名是否有异常
            table_columns = [row[0] for row in conn.execute(f"DESCRIBE {self.id_tab}").fetchall()]
            # 检测输入数据是否包含数据库需要的完整信息
            if not all(col in df.columns for col in table_columns):
                return f"列名不匹配：数据：{df.columns.to_list()},数据库：{table_columns}"
            
            df = df[table_columns]  # 保留需要的数据
            gp_col = self.id_map.get('symbol','symbol')
            for symbol in symbols:
                last_date = conn.execute(f"""
                    SELECT MAX({self.id_map.get('trade_date','trade_date')}) 
                    FROM {self.id_tab} WHERE {gp_col}='{symbol}';
                    """).fetchone()[0]
                if last_date is None:
                    df2 = df[df[gp_col]==symbol]
                    conn.execute(f"INSERT OR REPLACE INTO {self.id_tab}  SELECT * FROM df2")
                else:
                    df2 = df[df[gp_col]==symbol]  # 提取
                    conn.execute(f"INSERT OR IGNORE INTO {self.id_tab}  SELECT * FROM df2")
            conn.close()
            # 更新了上证指数后刷新 update_date
            if '000001' in symbols:
                self.update_date = self.date_stock_index("000001")
            return "OK"
        except Exception as e:
            return f"更新stock_index运行异常：{e}"
    
    def dates_await(self,table="stock") -> list:
        """返回需要更新的日期清单"""
        conn = duckdb.connect(self.db_path)
        if table == "stock":
            # 按交易日期更新
            td_col = self.st_map.get("trade_date","trade_date")
            last_date = conn.execute(f"SELECT MAX({td_col}) FROM {self.st_tab} "
                                    ).fetchone()[0]
        elif table == "stock_factor":
            # 按交易日期更新
            td_col = self.factor_map.get("trade_date","trade_date")
            last_date = conn.execute(f"SELECT MAX({td_col}) FROM {self.factor_tab} "
                                    ).fetchone()[0]
        elif table == "stock_forecast":
            # 按公告日期更新
            if self.table_date.get("stock_forecast"):
                last_date = self.table_date.get("stock_forecast")
            else:
                ad_col = self.forecast_map.get("ann_date","ann_date")
                last_date = conn.execute(f"SELECT MAX({ad_col}) FROM {self.forecast_tab} "
                                        ).fetchone()[0]
        elif table == "stock_dividend":
            # 按除权日期更新
            if self.table_date.get("stock_dividend"):
                last_date = self.table_date.get("stock_dividend")
            else:
                ed_col = self.dividend_map.get("ex_date","ex_date")
                last_date = conn.execute(f"SELECT MAX({ed_col}) FROM {self.dividend_tab} "
                                        ).fetchone()[0]
        elif table == "stock_report":
            # 按公告日期更新
            if self.table_date.get("stock_report"):
                last_date = self.table_date.get("stock_report")
            else:
                ad_col = self.report_map.get("ann_date","ann_date")
                last_date = conn.execute(f"SELECT MAX({ad_col}) FROM {self.report_tab} "
                                        ).fetchone()[0]
        else:
            return []
        td_col_id = self.id_map.get("trade_date","trade_date")
        if last_date is None:
            trade_days = conn.execute(f"SELECT DISTINCT {td_col_id} FROM {self.id_tab} "
                                  f"ORDER BY {td_col_id} ASC").fetchall()
            conn.close()
            return [row[0] for row in trade_days]
        else:
            trade_days = conn.execute(f"SELECT DISTINCT {td_col_id} FROM {self.id_tab} "
                                      f"WHERE {td_col_id} > ? "
                                  f"ORDER BY {td_col_id} ASC",[last_date]).fetchall()
            conn.close()
            return [row[0] for row in trade_days]

    def norm_symbol(self, stock_series: pd.Series) -> pd.Series:
        """把股票代码规范到内部标准格式"""
        s = stock_series.astype(str).str.strip()
        s = s.apply(lambda x: ''.join(re.findall(r'\d', x)))
        # s = s.where(s.str.len()==6, None)  # 7位是指数前加负号，港股5位
        return s.astype('string')
                
    def update_stock(self,df:pd.DataFrame, ignore_check=False) -> str:
        """股票是按日期更新的，给每日的全A数据"""
        # 检测df的列名是否正常
        try:
            # 规范symbol列，值保留6为数值，不包含sh\sz之类的
            df.loc[:,'symbol'] = self.norm_symbol(df['symbol'])
            df['trade_date'] = df['trade_date'].astype(object) 
            df.loc[:,'trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce').dt.date
            # 删除无法识别的错误日期
            df = df.dropna(subset=['trade_date'])
            if len(df)<=0:
                return "无符号时间格式的数据"
            # 增加支持自定义名称
            df.rename(columns=self.st_map,inplace=True)
            td_col = self.st_map.get('trade_date','trade_date')
            gp_col = self.st_map.get('symbol','symbol')
            # col_default = ["trade_date","symbol","open","high","low","close","pre_close","vol","voe"]
            conn = duckdb.connect(self.db_path)
            # 检测数据库的列名是否有异常
            table_columns = [row[0] for row in conn.execute(f"DESCRIBE {self.st_tab}").fetchall()]
            if not all(col in df.columns for col in table_columns):
                return f"列名不匹配：数据：{df.columns.to_list()},数据库：{table_columns}"
            df = df[table_columns]  # 保留需要的数据
            
            # 要获取最新的股票清单，检测每次更新时的数量不能缺少太多
            # 检测一下数据一致性，不能突然变多或突然变少太多
            if not self.exist_stocks:
                e_stocks = conn.execute(f"""
                    WITH max_date AS (SELECT MAX({td_col}) AS last_day FROM {self.st_tab}) 
                    SELECT DISTINCT {gp_col} FROM {self.st_tab} 
                    WHERE {td_col} = (SELECT last_day FROM max_date)
                    ORDER BY {gp_col} ASC;
                    """).fetchall()
                self.exist_stocks = [row[0] for row in e_stocks]
                self.count_stocks = len(self.exist_stocks)
            
            if not self.exist_stocks:
                # 空数据更新
                conn.execute(f"INSERT OR REPLACE INTO {self.st_tab}  SELECT * FROM df")
            else:
                # 检查数据是否充足
                # print(self.exist_stocks)
                intersection = set(self.exist_stocks) & set(df[gp_col].to_list())
                if self.count_stocks*0.95 > len(intersection):  # 停牌数过多判断为异常
                    if ignore_check:
                        conn.execute(f"INSERT OR IGNORE INTO {self.st_tab}  SELECT * FROM df")
                    else:
                        return f"股票数量{len(intersection)}，缺失过多，可能有异常"
                conn.execute(f"INSERT OR IGNORE INTO {self.st_tab}  SELECT * FROM df")
            conn.close()
            return "OK"
        except Exception as e:
            return f"更新stock运行异常,{e}"
    
    def update_stock_basic(self,df:pd.DataFrame) -> str:
        try:
            if 'symbol' not in df.columns:
                if "ts_code" in df.columns:
                    df['symbol'] = self.norm_symbol(df['ts_code'])
                else:
                    return "无symbol列,股票代码"
            else:
                df['symbol'] = self.norm_symbol(df['symbol'])
            if 'update_date' not in df.columns:
                today = datetime.now().date()
                df['update_date'] = today
            if 'list_date' in df.columns:
                # 上市日期转日期格式
                df['list_date'] = df['list_date'].astype(object) 
                df.loc[:,'list_date'] = pd.to_datetime(df['list_date'], errors='coerce').dt.date
            # 增加对名称不匹配的支持
            df.rename(columns=self.basic_map,inplace=True)
            conn = duckdb.connect(self.db_path)
            # 检测数据库的列名是否有异常
            table_columns = [row[0] for row in conn.execute(f"DESCRIBE {self.basic_tab}").fetchall()]
            ab_cols = list(set(df.columns.to_list()) & set(table_columns))
            df = df[ab_cols]
            col_txt = ','.join(ab_cols)
            conn.execute(f"""
                INSERT OR REPLACE INTO {self.basic_tab} ({col_txt})
                SELECT {col_txt} FROM df
                """)
            conn.close()
            return "OK"
        except Exception as e:
            return f"更新stock_basic运行异常:{e}"

    def date_stock_basic(self):
        conn = duckdb.connect(self.db_path)
        last_date = conn.execute(f"SELECT MAX(update_date) FROM {self.basic_tab};").fetchone()[0]
        # 后续可以考虑是否加一个检测，检测是否有新股，每新股不更新？
        conn.close()
        return last_date

    def update_stock_factor(self,df:pd.DataFrame, ignore_check:bool=False) ->str:
        """每日指标，按日期更新"""
        # 检测df的列名是否正常
        try:
            # 规范symbol列，值保留6为数值，不包含sh\sz之类的
            df.loc[:,'symbol'] = self.norm_symbol(df['symbol'])
            df['trade_date'] = df['trade_date'].astype(object) 
            df.loc[:,'trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce').dt.date
            # 删除无法识别的错误日期
            df = df.dropna(subset=['trade_date'])
            if len(df)<=0:
                return "无符号日期格式的数据"
            df.rename(columns=self.factor_map,inplace=True)
            td_col = self.factor_map.get("trade_date","trade_date")
            gp_col = self.factor_map.get("symbol","symbol")
            # 要不要执行数据库匹配是的名称转换？
            conn = duckdb.connect(self.db_path)
            # 检测数据库的列名是否有异常
            table_columns = [row[0] for row in conn.execute(f"DESCRIBE {self.factor_tab}").fetchall()]
            # 检测输入数据是否包含数据库需要的完整信息
            if not all(col in df.columns for col in table_columns):
                return f"列名不匹配：数据：{df.columns.to_list()},数据库：{table_columns}"
            df = df[table_columns]  # 保留需要的数据
           
            # 检测一下数据一致性，不能突然变多或突然变少太多
            if not self.exist_stocks:
                e_stocks = conn.execute(f"""
                    WITH max_date AS (SELECT MAX({td_col}) AS last_day FROM {self.factor_tab}) 
                    SELECT DISTINCT {gp_col} FROM {self.factor_tab} 
                    WHERE {td_col} = (SELECT last_day FROM max_date)
                    ORDER BY {gp_col} ASC;
                    """).fetchall()
                self.exist_stocks = [row[0] for row in e_stocks]
                self.count_stocks = len(self.exist_stocks)
            if not self.exist_stocks:
                # 空数据更新
                conn.execute(f"INSERT OR REPLACE INTO {self.factor_tab}  SELECT * FROM df")
            else:
                # 检查数据是否充足
                # print(self.exist_stocks)
                intersection = set(self.exist_stocks) & set(df['symbol'].to_list())
                if self.count_stocks*0.95 > len(intersection):  # 停牌数过多判断为异常
                    if ignore_check:
                        conn.execute(f"INSERT OR IGNORE INTO {self.factor_tab}  SELECT * FROM df")
                    else:
                        return f"股票数量{len(intersection)}，缺失过多，可能有异常"
                conn.execute(f"INSERT OR IGNORE INTO {self.factor_tab}  SELECT * FROM df")
            return "OK"
        except Exception as e:
            return f"更新stock_factor运行异常,{e}"

    def update_stock_forecast(self,df:pd.DataFrame,date) ->str:
        """更新业绩预告"""
        # 检测df的列名是否正常
        try:
            # 规范symbol列，值保留6为数值，不包含sh\sz之类的
            df.loc[:,'symbol'] = self.norm_symbol(df['symbol'])
            # 日期格式转换
            df['end_date'] = df['end_date'].astype(object) 
            df.loc[:,'end_date'] = pd.to_datetime(df['end_date'], errors='coerce').dt.date
            df['ann_date'] = df['ann_date'].astype(object) 
            df.loc[:,'ann_date'] = pd.to_datetime(df['ann_date'], errors='coerce').dt.date
            if 'first_ann_date' in df.columns:
                df['first_ann_date'] = df['first_ann_date'].astype(object)
                df.loc[:,'first_ann_date'] = pd.to_datetime(df['first_ann_date'],
                                                             errors='coerce').dt.date
            # 删除无法识别的错误日期
            df = df.dropna(subset=['end_date','ann_date'])
            if len(df)<=0:
                return "无符合日期格式的数据"
            # 增加一个名称匹配
            df.rename(columns=self.factor_map,inplace=True)
            # 要不要执行数据库匹配是的名称转换？
            with duckdb.connect(self.db_path) as conn:
                # 检测数据库的列名是否有异常
                table_columns = [row[0] for row in conn.execute(f"DESCRIBE {self.forecast_tab}").fetchall()]
                # 检测输入数据是否包含数据库需要的完整信息
                if not all(col in df.columns for col in table_columns):
                    return f"列名不匹配：数据：{df.columns.to_list()},数据库：{table_columns}"
                df = df[table_columns]  # 保留需要的数据
                
                # 检测现有数据库是否是空表
                exist_tab = conn.execute(f"SELECT EXISTS (SELECT 1 FROM {self.forecast_tab})"
                                        ).fetchone()[0]
                # print("forecast表格是否为空",exist_tab)
                if exist_tab:
                    conn.execute(f"INSERT OR IGNORE INTO {self.forecast_tab}  SELECT * FROM df")
                else:
                    conn.execute(f"INSERT OR REPLACE INTO {self.forecast_tab}  SELECT * FROM df")
                conn.execute("""
                    INSERT OR REPLACE INTO table_date (table_name, update_date)
                    VALUES (?, ?)
                """, ["stock_forecast", self.update_date])

            return "OK"
            # 后续加一个二次检查，检查数据是否遗漏
        except Exception as e:
            return f"更新stock_forecast运行异常,{e}"

    def update_stock_dividend(self,df:pd.DataFrame,date) ->str:
        """更新业绩预告"""
        # 检测df的列名是否正常
        try:
            # 规范symbol列，值保留6为数值，不包含sh\sz之类的
            df.loc[:,'symbol'] = self.norm_symbol(df['symbol'])
            # 日期格式转换
            df['end_date'] = df['end_date'].astype(object) 
            df.loc[:,'end_date'] = pd.to_datetime(df['end_date'], errors='coerce').dt.date
            df['ann_date'] = df['ann_date'].astype(object) 
            df.loc[:,'ann_date'] = pd.to_datetime(df['ann_date'], errors='coerce').dt.date
            for s in ['record_date','ex_date','pay_date','imp_ann_date','div_listdate']:
                if s in df.columns:
                    df[s] = df[s].astype(object) 
                    df.loc[:,s] = pd.to_datetime(df[s], errors='coerce').dt.date

            # 删除无法识别的错误日期
            df = df.dropna(subset=['end_date','ex_date'])
            if len(df)<=0:
                return "无符合日期格式的数据"
            df.rename(columns=self.dividend_map, inplace=True)
            # 要不要执行数据库匹配是的名称转换？
            with duckdb.connect(self.db_path) as conn:
                # 检测数据库的列名是否有异常
                table_columns = [row[0] for row in conn.execute(f"DESCRIBE {self.dividend_tab}").fetchall()]
                # 检测输入数据是否包含数据库需要的完整信息
                if not all(col in df.columns for col in table_columns):
                    return f"列名不匹配：数据：{df.columns.to_list()},数据库：{table_columns}"
                df = df[table_columns]  # 保留需要的数据
                
                # 检测现有数据库是否是空表
                exist_tab = conn.execute(f"SELECT EXISTS (SELECT 1 FROM {self.dividend_tab})"
                                        ).fetchone()[0]
                if exist_tab:
                    conn.execute(f"INSERT OR IGNORE INTO {self.dividend_tab}  SELECT * FROM df")
                else:
                    conn.execute(f"INSERT OR REPLACE INTO {self.dividend_tab}  SELECT * FROM df")
                conn.execute("""
                    INSERT OR REPLACE INTO table_date (table_name, update_date)
                    VALUES (?, ?)
                """, ["stock_dividend", self.update_date])

            return "OK"
            # 后续加一个二次检查，检查数据是否遗漏
        except Exception as e:
            return f"更新stock_dividend运行异常,{e}"

    def update_stock_report(self,df:pd.DataFrame) ->str:
        """更新财务指标"""
        # 检测df的列名是否正常
        try:
            # 规范symbol列，值保留6为数值，不包含sh\sz之类的
            df.loc[:,'symbol'] = self.norm_symbol(df['symbol'])
            # 日期格式转换
            df['end_date'] = df['end_date'].astype(object) 
            df.loc[:,'end_date'] = pd.to_datetime(df['end_date'], errors='coerce').dt.date
            df['ann_date'] = df['ann_date'].astype(object) 
            df.loc[:,'ann_date'] = pd.to_datetime(df['ann_date'], errors='coerce').dt.date
            # 删除无法识别的错误日期
            df = df.dropna(subset=['end_date','ann_date'])
            if len(df)<=0:
                return "无符合日期格式的数据"
            df.rename(columns=self.report_map,inplace=True)
            # 要不要执行数据库匹配是的名称转换？
            with duckdb.connect(self.db_path) as conn:
                # 检测数据库的列名是否有异常
                table_columns = [row[0] for row in conn.execute(f"DESCRIBE {self.report_tab}").fetchall()]
                # 检测输入数据是否包含数据库需要的完整信息
                if not all(col in df.columns for col in table_columns):
                    return f"列名不匹配：数据：{df.columns.to_list()},数据库：{table_columns}"
                df = df[table_columns]  # 保留需要的数据
            
                # 检测现有数据库是否是空表
                conn.execute(f"INSERT OR REPLACE INTO {self.report_tab}  SELECT * FROM df")
                conn.execute("""
                    INSERT OR REPLACE INTO table_date (table_name, update_date)
                    VALUES (?, ?)
                """, ["stock_report", self.update_date])

            return "OK"
            # 后续加一个二次检查，检查数据是否遗漏
        except Exception as e:
            return f"更新stock_report运行异常,{e}"

    def creat_duckdb(self,path='') -> str:
        if not path:
            path = os.path.join(os.path.dirname(__file__),'Test.duckdb')
        if os.path.isfile(path):
            return "文件已存在，放弃执行"
        with duckdb.connect(path) as conn:
            # 创建存储股市每日行情数据
            conn.execute("""
            CREATE TABLE IF NOT EXISTS stock (
                trade_date DATE,       
                symbol STRING,          
                open REAL,            
                high REAL,            
                low REAL,             
                close REAL,            
                pre_close REAL,       
                vol REAL,            
                voe REAL,    
                PRIMARY KEY (trade_date, symbol)      
            );
            """)
            # 索引，会使数据库变大，能加快一点查询速度
            # conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON stock(trade_date);")

            # 创建指数数据表
            conn.execute("""
            CREATE TABLE IF NOT EXISTS stock_index (
                trade_date DATE,        
                symbol STRING,          
                open REAL,          
                high REAL,          
                low REAL,           
                close REAL,
                pre_close REAL,           
                vol REAL,            
                voe REAL,         
                PRIMARY KEY (trade_date, symbol)
            );
            """)
            # 索引，会使数据库变大，能加快一点查询速度
            # conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON stock_index(trade_date);")

            # 创建 基础信息表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stock_basic ( 
                    symbol STRING,              --股票代码
                    name STRING,                --股票名称
                    update_date DATE,           --数据更新日期
                    list_date DATE,             --上市日期
                    act_name STRING,            --实控人名称
                    act_ent_type STRING,        --实控人企业性质
                    industry STRING,            --所属行业
                    com_name STRING,            --公司名称
                    com_id STRING,              --统一社会信用代码
                    chairman STRING,            --法人代表
                    manager STRING,             --总经理
                    secretary STRING,           --董秘
                    reg_capital REAL,           --注册资本
                    setup_date STRING,          --注册日期
                    province STRING,            --所在省份
                    city STRING,                --所在城市
                    introduction STRING,         --公司介绍
                    website STRING,             --公司主页
                    email STRING,               --电子邮件
                    office STRING,              --办公室
                    business_scope STRING,      --经营范围
                    employees INTEGER,          --员工人数
                    main_business STRING,       --主要业务及产品
                    exchange STRING,            --交易所
                    concept STRING,             --概念
                    PRIMARY KEY (symbol)
                );
                """)
            
            # 传教 每日行情因子
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stock_factor (
                    symbol STRING,                -- TS股票代码
                    trade_date DATE,             -- 交易日期
                    close REAL,                   -- 当日收盘价
                    turnover_rate REAL,           -- 换手率
                    turnover_rate_f REAL,         -- 换手率(自由流通股)
                    volume_ratio REAL,            -- 量比
                    pe REAL,                      -- 市盈率
                    pe_ttm REAL,                  -- 市盈率TTM
                    pb REAL,                      -- 市净率
                    ps REAL,                      -- 市销率
                    ps_ttm REAL,                  -- 市销率TTM
                    dv_ratio REAL,                -- 股息率
                    dv_ttm REAL,                  -- 股息率TTM
                    total_share REAL,             -- 总股本
                    float_share REAL,             -- 流通股本
                    free_share REAL,              -- 自由流通股本
                    total_mv REAL,                -- 总市值
                    circ_mv REAL,                -- 流通市值
                    limit_status INTEGER,           -- 涨跌停状态
                    PRIMARY KEY (symbol, trade_date)  -- 联合主键（必须！）
                );
                """)
            
            # 业绩预告
            conn.execute("""
            CREATE TABLE IF NOT EXISTS stock_forecast (
                symbol STRING,               -- TS股票代码
                end_date DATE,               -- 报告期
                ann_date DATE,               -- 公告日期
                first_ann_date DATE,          -- 首次公告日
                type STRING,                  -- 业绩预告类型
                p_change_min REAL,             -- 预告净利润变动幅度下限（%）
                p_change_max REAL,             -- 预告净利润变动幅度上限（%）
                net_profit_min REAL,           -- 预告净利润下限（万元）
                net_profit_max REAL,           -- 预告净利润上限（万元）
                last_parent_net REAL,          -- 上年同期归属母公司净利润
                summary STRING,               -- 业绩预告摘要
                change_reason STRING,         -- 业绩变动原因
                update_flag STRING,           -- 更新标志
                PRIMARY KEY (symbol, end_date)
            );
            """)

            # 创建 股票分红表 stock_dividend
            conn.execute("""
            CREATE TABLE IF NOT EXISTS stock_dividend (
                symbol STRING,             -- TS代码
                end_date DATE,            -- 分送年度
                ann_date DATE,            -- 预案公告日（董事会）
                imp_ann_date DATE,       -- 实施公告日
                record_date DATE,        -- 股权登记日
                div_listdate DATE,       -- 红股上市日
                ex_date DATE,            -- 除权除息日
                pay_date DATE,           -- 派息日
                div_proc STRING,            -- 实施进度
                stk_div REAL,                -- 每股送转
                stk_bo_rate REAL,           -- 每股送股比例
                stk_co_rate REAL,            -- 每股转增比例
                cash_div REAL,              -- 每股分红（税后）
                cash_div_tax REAL,          -- 每股分红（税前）
                PRIMARY KEY (symbol, end_date)
            );
            """)

            # 创建 财务主要指标表 stock_report
            conn.execute("""
            CREATE TABLE IF NOT EXISTS stock_report (
                symbol STRING,                        -- TS代码
                end_date DATE,                       -- 报告期 
                ann_date DATE,                       -- 公告日期
                eps REAL,                               -- 基本每股收益
                dt_eps REAL,                            -- 稀释每股收益
                total_revenue_ps REAL,                  -- 每股营业总收入
                revenue_ps REAL,                        -- 每股营业收入
                capital_rese_ps REAL,                   -- 每股资本公积
                surplus_rese_ps REAL,                    -- 每股盈余公积
                undist_profit_ps REAL,                   -- 每股未分配利润
                extra_item REAL,                        -- 非经常性损益
                profit_dedt REAL,                       -- 扣除非经常性损益后的净利润
                gross_margin REAL,                      -- 毛利
                current_ratio REAL,                     -- 流动比率
                quick_ratio REAL,                       -- 速动比率
                cash_ratio REAL,                        -- 保守速动比率
                
                ar_turn REAL,                           -- 应收账款周转率
                ca_turn REAL,                           -- 流动资产周转率
                fa_turn REAL,                           -- 固定资产周转率
                assets_turn REAL,                       -- 总资产周转率
                op_income REAL,                         -- 经营活动净收益
                
                ebit REAL,                              -- 息税前利润
                ebitda REAL,                            -- 息税折旧摊销前利润
                fcff REAL,                              -- 企业自由现金流量
                fcfe REAL,                              -- 股权自由现金流量
                current_exint REAL,                     -- 无息流动负债
                noncurrent_exint REAL,                  -- 无息非流动负债
                interestdebt REAL,                      -- 带息债务
                netdebt REAL,                           -- 净债务
                tangible_asset REAL,                    -- 有形资产
                working_capital REAL,                   -- 营运资金
                networking_capital REAL,                -- 营运流动资本
                invest_capital REAL,                    -- 全部投入资本
                retained_earnings REAL,                 -- 留存收益
                diluted2_eps REAL,                      -- 期末摊薄每股收益
                bps REAL,                               -- 每股净资产
                ocfps REAL,                             -- 每股经营活动产生的现金流量净额
                retainedps REAL,                        -- 每股留存收益
                cfps REAL,                              -- 每股现金流量净额
                ebit_ps REAL,                           -- 每股息税前利润
                fcff_ps REAL,                           -- 每股企业自由现金流量
                fcfe_ps REAL,                           -- 每股股东自由现金流量
                netprofit_margin REAL,                  -- 销售净利率
                grossprofit_margin REAL,                -- 销售毛利率
                cogs_of_sales REAL,                     -- 销售成本率
                expense_of_sales REAL,                  -- 销售期间费用率
                profit_to_gr REAL,                      -- 净利润/营业总收入
                saleexp_to_gr REAL,                     -- 销售费用/营业总收入
                adminexp_of_gr REAL,                    -- 管理费用/营业总收入
                finaexp_of_gr REAL,                     -- 财务费用/营业总收入
                impai_ttm REAL,                         -- 资产减值损失/营业总收入
                gc_of_gr REAL,                          -- 营业总成本/营业总收入
                op_of_gr REAL,                          -- 营业利润/营业总收入
                ebit_of_gr REAL,                        -- 息税前利润/营业总收入
                roe REAL,                               -- 净资产收益率
                roe_waa REAL,                           -- 加权平均净资产收益率
                roe_dt REAL,                            -- 净资产收益率(扣除非经常损益)
                roa REAL,                               -- 总资产报酬率
                npta REAL,                              -- 总资产净利润
                roic REAL,                              -- 投入资本回报率
                roe_yearly REAL,                        -- 年化净资产收益率
                roa2_yearly REAL,                       -- 年化总资产报酬率
                
                debt_to_assets REAL,                    -- 资产负债率
                assets_to_eqt REAL,                     -- 权益乘数
                dp_assets_to_eqt REAL,                  -- 权益乘数(杜邦分析)
                ca_to_assets REAL,                      -- 流动资产/总资产
                nca_to_assets REAL,                     -- 非流动资产/总资产
                tbassets_to_totalassets REAL,           -- 有形资产/总资产
                int_to_talcap REAL,                     -- 带息债务/全部投入资本
                eqt_to_talcapital REAL,                 -- 归属于母公司的股东权益/全部投入资本
                currentdebt_to_debt REAL,               -- 流动负债/负债合计
                longdeb_to_debt REAL,                   -- 非流动负债/负债合计
                ocf_to_shortdebt REAL,                  -- 经营活动产生的现金流量净额/流动负债
                debt_to_eqt REAL,                       -- 产权比率
                eqt_to_debt REAL,                       -- 归属于母公司的股东权益/负债合计
                eqt_to_interestdebt REAL,               -- 归属于母公司的股东权益/带息债务
                tangibleasset_to_debt REAL,              -- 有形资产/负债合计
                tangasset_to_intdebt REAL,               -- 有形资产/带息债务
                tangibleasset_to_netdebt REAL,           -- 有形资产/净债务
                ocf_to_debt REAL,                       -- 经营活动产生的现金流量净额/负债合计
                
                turn_days REAL,                         -- 营业周期
                roa_yearly REAL,                        -- 年化总资产净利率
                roa_dp REAL,                            -- 总资产净利率(杜邦分析)
                fixed_assets REAL,                      -- 固定资产合计
                
                profit_to_op REAL,                      -- 利润总额／营业收入
                
                q_saleexp_to_gr REAL,                   -- 销售费用／营业总收入 (单季度)
                
                q_gc_to_gr REAL,                        -- 营业总成本／营业总收入 (单季度)
                
                q_roe REAL,                             -- 净资产收益率(单季度)
                q_dt_roe REAL,                          -- 净资产单季度收益率(扣除非经常损益)
                q_npta REAL,                            -- 总资产净利润(单季度)
                
                q_ocf_to_sales REAL,                    -- 经营活动产生的现金流量净额／营业收入(单季度)

                basic_eps_yoy REAL,                     -- 基本每股收益同比增长率(%)
                dt_eps_yoy REAL,                        -- 稀释每股收益同比增长率(%)
                cfps_yoy REAL,                          -- 每股经营活动产生的现金流量净额同比增长率(%)
                op_yoy REAL,                            -- 营业利润同比增长率(%)
                ebt_yoy REAL,                           -- 利润总额同比增长率(%)
                netprofit_yoy REAL,                     -- 归属母公司股东的净利润同比增长率(%)
                dt_netprofit_yoy REAL,                  -- 归属母公司股东的净利润-扣除非经常损益同比增长率(%)
                ocf_yoy REAL,                           -- 经营活动产生的现金流量净额同比增长率(%)
                roe_yoy REAL,                           -- 净资产收益率(摊薄)同比增长率(%)
                bps_yoy REAL,                           -- 每股净资产相对年初增长率(%)
                assets_yoy REAL,                        -- 资产总计相对年初增长率(%)
                eqt_yoy REAL,                           -- 归属母公司的股东权益相对年初增长率(%)
                tr_yoy REAL,                            -- 营业总收入同比增长率(%)
                or_yoy REAL,                            -- 营业收入同比增长率(%)

                q_sales_yoy REAL,                       -- 营业收入同比增长率(%)(单季度)
                
                q_op_qoq REAL,                          -- 营业利润环比增长率(%)(单季度)
                
                equity_yoy REAL,                        -- 净资产同比增长率
                PRIMARY KEY (symbol, end_date)
            );
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS table_date (
                table_name STRING,          -- 表格
                update_date DATE,         -- 更新日期
                PRIMARY KEY (table_name)
            );
            """)

            # 关闭时间库
        # conn.close()
        return f"数据库创建完成{path}"
    
    def check_report_miss(self):
        """检查财报是否有中间缺失,只支持默认命名规则"""
        # 第一步，把数据全读出来
        conn = duckdb.connect(self.db_path)
        # 读取股票 + 报告期（去重，保证干净）
        df = conn.execute(f"""
                        SELECT symbol, end_date FROM {self.report_tab}
                        ORDER BY symbol, end_date 
                    """).df()
        # 获取上市日期
        df_list = conn.execute(f"SELECT symbol, list_date FROM {self.basic_tab}").df()
        list_dict = dict(zip(df_list["symbol"], pd.to_datetime(df_list["list_date"])))
        conn.close()
        if df.empty:
            return pd.DataFrame([])
        # 生成一个标准的财报时间
        df['end_date'] = pd.to_datetime(df["end_date"])
        min_year = df['end_date'].min().year
        max_year = df['end_date'].max().year
        standard_quarters = ["03-31", "06-30", "09-30", "12-31"]

        # 生成全局标准财报日期列表（DATE 格式）
        norm_end_date = []
        for y in range(min_year, max_year + 1):
            for q in standard_quarters:
                norm_end_date.append(pd.to_datetime(f"{y}-{q}"))

        norm_end_date = np.array(sorted(norm_end_date))  # 转 numpy 加速
        # 检查
        missing_records = []

        for symbol, group in df.groupby("symbol"):
            # 1. 缺失上市日期 → 用 1900-03-31（日期格式）
            # default_list_date = pd.to_datetime("1900-03-31")
            symbol_ld = list_dict.get(symbol)
            if not symbol_ld:
                # 可能股票还没上市,或者基础信息数据库异常
                continue
            # 2.只保留 上市后 的财报日期（剔除上市前数据）
            group_valid = group[group["end_date"] >= symbol_ld].copy()
            if group_valid.empty:
                continue  # 无有效数据，跳过
            # 3. 转 numpy 数组（只保留日期值，提速）
            s_dates = np.array(pd.to_datetime(group_valid["end_date"]).sort_values())
            s_min = s_dates.min()
            s_max = s_dates.max()
            # 4. 定位标准日期区间
            left = np.searchsorted(norm_end_date, s_min, side="left")
            right_idx = np.searchsorted(norm_end_date, s_max, side="right")
            expected = norm_end_date[left:right_idx]
            # 数量相等 → 无缺失
            if len(s_dates) == len(expected):
                continue

            # 数量不等 → 找缺失
            missing = np.setdiff1d(expected, s_dates)
            for d in missing:
                missing_records.append({
                    "symbol": symbol,
                    "missing_end_date": pd.to_datetime(d).strftime("%Y-%m-%d")
                })

        missing_df = pd.DataFrame(missing_records)
        if not missing_df.empty:
            print(f"缺失报告期总数：{len(missing_df)}")
            print(missing_df)
        else:
            print("所有股票期间完整，无中间缺失！")
        return missing_df


def update_report_from_symbols(symbols:list=[],api:str="你的API"):
    """财报相关用个股更新方式，容易有遗漏，不漏用的"""
    updb = Updb()  # 辅助适配到软件的数据库
    pro = ts.pro_api(api)
    result_list = []
    err_list = []
    for i, code in enumerate(symbols, 1):
        try:
            # 单只查询，最稳定
            df = pro.fina_indicator(ts_code=code)
            if len(df)>0:
                result_list.append(df)
            else:
                print(f"{code}无财报指标数据")
                # 可能加弹窗会合理点
        except Exception as e:
            print(f"{code}失败：{str(e)}")
            err_list.append(code)
        finally:
            if (i+1)%10 == 0:
                sl_time = 10-time.time()+t0
                if sl_time >0:
                    time.sleep(sl_time)  # 避免频率太高
                t0 = time.time()

    # 汇总所有成功数据
    if result_list:
        df = pd.concat(result_list, ignore_index=True)
        print(f"财务指标全部拉取完成！共汇总 {len(df)} 条财报指标")
        df.rename(columns={"ts_code":"symbol"},inplace=True)
        err = updb.update_stock_report(df)
        print("财务指标,补缺",err)
    else:
        print("未获取到任何财报数据")


async def _log(ctx: Context, phase: int, total_phases: int, message: str):
    """向 MCP 客户端发送进度通知和日志。ctx 为 None 时退化为 print。"""
    if ctx is not None:
        await ctx.report_progress(phase, total_phases, message)
        await ctx.info(message)
    else:
        print(f"[{phase}/{total_phases}] {message}")


async def example_tushare_2000(api:str='你的API',DB_path:str='',ignore_check:bool=False, ctx: Context=None):
    TOTAL_PHASES = 7
    if datetime.now().hour<15:  # 15点前不更新当天的，避免异常
        today = datetime.now().date() - timedelta(days=1)
    else:
        today = datetime.now().date()
    # 调整到工作日
    if today.weekday() == 6:
        today = today - timedelta(days=2)
    elif today.weekday() == 5:
        today = today - timedelta(days=1)
    
    today_s = today.strftime('%Y%m%d')  # "2026-06-06" 格式
    updb = Updb(DB_path)  # 辅助适配到软件的数据库
    pro = ts.pro_api(api)
    # region 2000积分，更新指数
    await _log(ctx, 1, TOTAL_PHASES, "开始更新指数数据")
    id_list = ["399001.SZ","000001.SH"]
    t0 = time.time()
    for i, ts_code in enumerate(id_list):
        start_date:datetime = updb.date_stock_index(ts_code)
        if start_date is None:
            # 数据库是空白的，设置你的数据库开始时间，默认两年
            start_date =  today - timedelta(days=730) # 两年前
            start_date_s = start_date.strftime('%Y%m%d')
        else:
            if today <= start_date:
                continue
            start_date_s = start_date.strftime('%Y%m%d')
        df_date:pd.DataFrame = pro.index_daily(ts_code=ts_code, 
                             start_date=start_date_s,
                             end_date=today_s)
        if len(df_date)>0:
            df_date.rename(columns={"ts_code":"symbol","amount":"voe"},inplace=True)
            df_date = df_date.sort_values(by='trade_date',ignore_index=True)  # 按交易日期从小到大排序
            # tushare 单位 成交量 手 成交额 千元
            err = updb.update_stock_index(df_date)
            await _log(ctx, 1, TOTAL_PHASES, f"指数 {ts_code}: {err}")

        if (i+1)%10 == 0:
            sl_time = 10-time.time()+t0
            if sl_time >0:
                time.sleep(sl_time)  # 避免频率太高
            t0 = time.time()
    await _log(ctx, 1, TOTAL_PHASES, "指数数据更新完成")
    updb.update_date = updb.date_stock_index("000001")
    # endregion 更新指数
    # region 120积分，更新股票数据
    dates_id:list[datetime] = updb.dates_await("stock")
    if not dates_id:
        await _log(ctx, 2, TOTAL_PHASES, "股票数据已是最新，无需更新")
    else:
        await _log(ctx, 2, TOTAL_PHASES, f"开始更新股票行情，共 {len(dates_id)} 个交易日待更新")
        t0 = time.time()
        for i,date in enumerate(dates_id):
            date_s = date.strftime('%Y%m%d')
            df_date = pro.daily(trade_date=date_s)
            if len(df_date)>0:
                df_date.rename(columns={"ts_code":"symbol","amount":"voe"},inplace=True)
                # 成交量tushare单位是手，成交额tushare单位是千元
                # 剔除北证券
                # df = df[~df['symbol'].str.startswith(tuple(['9']))]  # 如果你的数据库里有北证的，删掉这行
                err = updb.update_stock(df_date,ignore_check)  # 更新成功返回OK，否则返回错误原因
                await _log(ctx, 2, TOTAL_PHASES, f"股票行情 {date_s}: {err} ({i+1}/{len(dates_id)})")
                if err != "OK":
                    break
            else:
                # 交易日期用指数数据提取的，都是正常交易日，不能有数据缺失
                await _log(ctx, 2, TOTAL_PHASES, f"异常，{date_s}获取空数据")
                break
            # time.sleep(1.5)  # 连续跑大量的时候，减低点频率更稳定点
            if (i+1)%10 == 0:
                sl_time = 10-time.time()+t0
                if sl_time >0:
                    time.sleep(sl_time)  # 避免频率太高
                t0 = time.time()
    # endregion 更新股票数据

    # region 2000积分，更新基础数据
    # 判断是否又更新需求
    await _log(ctx, 3, TOTAL_PHASES, "开始更新基础数据")
    last_date_basic = updb.date_stock_basic()
    if last_date_basic is None or last_date_basic < today:
        df_date = pro.stock_basic(
            fields=["symbol", "name", "list_date", "industry","act_name","act_ent_type"])
        if len(df_date)>0:
            err1 = updb.update_stock_basic(df_date)
            await _log(ctx, 3, TOTAL_PHASES, f"stock_basic_1: {err1}")
        df_date = pro.stock_company()
        df_date.rename(columns={"ts_code":"symbol"},inplace=True)
        if len(df_date)>0:
            err2 = updb.update_stock_basic(df_date)
            await _log(ctx, 3, TOTAL_PHASES, f"stock_basic_2: {err2}")
    else:
        await _log(ctx, 3, TOTAL_PHASES, "基础数据已是最新")
    await _log(ctx, 3, TOTAL_PHASES, "基础数据更新完成")
    # endregion 更新基础数据

    # region 2000积分，更新行情因子
    daily_basic_dates:list[datetime] = updb.dates_await("stock_factor")
    updb.exist_stocks = []  # 因为更新stock数据时会读取一次，短时间范围可以不清除
    if not daily_basic_dates:
        await _log(ctx, 4, TOTAL_PHASES, "行情因子已是最新，无需更新")
    else:
        await _log(ctx, 4, TOTAL_PHASES, f"开始更新行情因子，共 {len(daily_basic_dates)} 个交易日待更新")
    fields = ["ts_code","trade_date","close","turnover_rate",
              "turnover_rate_f","volume_ratio","pe","pe_ttm",
                "pb","ps", "ps_ttm", "dv_ratio", "dv_ttm",
                "total_share", "float_share", "free_share",
                "total_mv", "circ_mv", "limit_status"]
    for i,date in enumerate(daily_basic_dates):
        date_s = date.strftime('%Y%m%d')
        df_date = pro.daily_basic(trade_date = date_s, fields=fields)
        if len(df_date)>0:
            df_date.rename(columns={"ts_code":"symbol"},inplace=True)
            # 成交量tushare单位是手，成交额tushare单位是千元
            # df = df[~df['symbol'].str.startswith(tuple(['9']))]  # 要剔除北证的话
            err = updb.update_stock_factor(df_date,date)  # 更新成功返回OK，否则返回错误原因
            await _log(ctx, 4, TOTAL_PHASES, f"行情因子 {date_s}: {err} ({i+1}/{len(daily_basic_dates)})")
            if err != "OK":
                break
        else:
            # 交易日期用指数数据提取的，都是正常交易日，不能有数据缺失
            await _log(ctx, 4, TOTAL_PHASES, f"异常，{date_s}获取空数据")
            break
        # time.sleep(1.5)  # 连续跑大量的时候，减低点频率更稳定点
        if (i+1)%10 == 0:
            sl_time = 10-time.time()+t0
            if sl_time >0:
                time.sleep(sl_time)  # 避免频率太高
            t0 = time.time()

    # endregion 更新行情因子

    # region 2000积分，更新业绩预告
    forecast_dates:list[datetime] = updb.dates_await("stock_forecast")
    if not forecast_dates:
        await _log(ctx, 5, TOTAL_PHASES, "业绩预告已是最新，无需更新")
        updb.write_table_date("stock_forecast")
    else:
        await _log(ctx, 5, TOTAL_PHASES, f"开始更新业绩预告，共 {len(forecast_dates)} 个日期待更新")
    for i,date in enumerate(forecast_dates):
        date_s = date.strftime('%Y%m%d')
        df_date = pro.forecast(ann_date=date_s)
        if len(df_date)>0:
            df_date.rename(columns={"ts_code":"symbol"},inplace=True)
            err = updb.update_stock_forecast(df_date,date)  # 更新成功返回OK，否则返回错误原因
            await _log(ctx, 5, TOTAL_PHASES, f"业绩预告 {date_s}: {err} ({i+1}/{len(forecast_dates)})")
            if err != "OK":
                break
        else:
            # 交易日期用指数数据提取的，都是正常交易日，不能有数据缺失
            await _log(ctx, 5, TOTAL_PHASES, f"{date_s}无业绩预告数据 ({i+1}/{len(forecast_dates)})")
        # time.sleep(1.5)  # 连续跑大量的时候，减低点频率更稳定点
        if (i+1)%10 == 0:
            sl_time = 10-time.time()+t0
            if sl_time >0:
                time.sleep(sl_time)  # 避免频率太高
            t0 = time.time()
    # endregion 更新业绩预告
    
    # region 2000积分，更新分红
    dividend_dates:list[datetime] = updb.dates_await("stock_dividend")
    if not dividend_dates:
        await _log(ctx, 6, TOTAL_PHASES, "分红数据已是最新，无需更新")
        updb.write_table_date("stock_dividend")
    else:
        await _log(ctx, 6, TOTAL_PHASES, f"开始更新分红数据，共 {len(dividend_dates)} 个日期待更新")
    for i,date in enumerate(dividend_dates):
        date_s = date.strftime('%Y%m%d')
        df_date = pro.dividend(ex_date=date_s)
        if len(df_date)>0:
            df_date.rename(columns={"ts_code":"symbol"},inplace=True)
            err = updb.update_stock_dividend(df_date,date)  # 更新成功返回OK，否则返回错误原因
            await _log(ctx, 6, TOTAL_PHASES, f"分红 {date_s}: {err} ({i+1}/{len(dividend_dates)})")
            if err != "OK":
                break
        else:
            await _log(ctx, 6, TOTAL_PHASES, f"{date_s}无分红数据 ({i+1}/{len(dividend_dates)})")
        # time.sleep(1.5)  # 连续跑大量的时候，减低点频率更稳定点
        if (i+1)%10 == 0:
            sl_time = 10-time.time()+t0
            if sl_time >0:
                time.sleep(sl_time)  # 避免频率太高
            t0 = time.time()

    # endregion 更新分红
    
    # region 2000积分，更新财务指标
    # ── 进度心跳辅助：避免逐只拉取时长时间无输出导致 AI 误判断连 ──
    HEARTBEAT_SEC = 30  # 超过此秒数无输出则强制发送进度脉冲
    def _heartbeat_msg(i: int, total: int, t_start: float) -> str:
        elapsed = time.time() - t_start
        if i > 0:
            rate = i / elapsed
            eta = (total - i) / rate if rate > 0 else 0
            eta_m = int(eta // 60); eta_s = int(eta % 60)
            return f"财报拉取进度 {i}/{total}（{i*100//total}%） 已耗时 {int(elapsed//60)}m{int(elapsed%60)}s 预计剩余 {eta_m}m{eta_s}s"
        return f"财报拉取进度 0/{total}（0%）"

    report_dates:list[datetime] = updb.dates_await("stock_report")
    if not report_dates:
        await _log(ctx, 7, TOTAL_PHASES, "财务指标已是最新，无需更新")
        updb.write_table_date("stock_report")
    else:
        await _log(ctx, 7, TOTAL_PHASES, f"开始更新财务指标，共 {len(report_dates)} 个日期待汇总清单")
    # 第一步，整理需要更新的清单
    all_stocks = set()  # 自动去重
    await _log(ctx, 7, TOTAL_PHASES, f"财报清单汇总中，扫描 {len(report_dates)} 个披露日期...")
    t_phase7 = time.time()
    for i,date in enumerate(report_dates):
        diff_days = (today - date).days
        if diff_days>275:  # 不超过两份财报间的最长跨距
            # 快速跳过一些不需要的日期，不发出信息
            continue
        date_s = date.strftime('%Y%m%d')
        try:
            df_date = pro.disclosure_date(actual_date=date_s)
            if len(df_date)>0:
                codes = df_date['ts_code'].tolist()
                all_stocks.update(codes)
        except Exception as e:
            await _log(ctx, 7, TOTAL_PHASES, f"获取财报更新清单 {date_s} 失败：{str(e)}")
            return
        # 每10条或超30秒发送一次进度
        if (i+1) % 10 == 0 or time.time() - t_phase7 > HEARTBEAT_SEC:
            await _log(ctx, 7, TOTAL_PHASES, f"财报清单汇总 {i+1}/{len(report_dates)}（已收集 {len(all_stocks)} 只股票）")
            t_phase7 = time.time()
        if (i+1) % 10 == 0:
            sl_time = 10-time.time()+t0
            if sl_time >0:
                time.sleep(sl_time)  # 避免频率太高
            t0 = time.time()

    stock_list = sorted(list(all_stocks))
    if not stock_list:
        await _log(ctx, 7, TOTAL_PHASES, "财报数据已是最新，无需更新")
        updb.write_table_date("stock_report")
        return
    await _log(ctx, 7, TOTAL_PHASES, f"财报清单汇总完成，待更新股票总数：{len(stock_list)} 只，开始拉取财务指标")

    # 第二步，提取数据（逐只拉取）
    result_list = []
    err_list = []
    t_start = time.time()
    last_log_time = t_start
    t_rate = t_start
    for i, code in enumerate(stock_list, 1):
        try:
            df = pro.fina_indicator(ts_code=code)
            if len(df)>0:
                result_list.append(df)
        except Exception as e:
            err_list.append(code)
        # 进度脉冲：每10只 或 超30秒无输出 发送一次
        now = time.time()
        if i % 10 == 0 or now - last_log_time > HEARTBEAT_SEC:
            await _log(ctx, 7, TOTAL_PHASES, _heartbeat_msg(i, len(stock_list), t_start))
            last_log_time = now
        # 频率控制：每10只后确保至少10秒间隔
        if (i+1) % 10 == 0:
            sl = 10 - (time.time() - t_rate)
            if sl > 0:
                time.sleep(sl)
            t_rate = time.time()

    # 汇总所有成功数据
    if result_list:
        await _log(ctx, 7, TOTAL_PHASES, f"财务指标全部拉取完成！成功 {len(result_list)} 只（失败 {len(err_list)} 只），开始写入数据库")
        df = pd.concat(result_list, ignore_index=True)
        df.rename(columns={"ts_code":"symbol"},inplace=True)
        err = updb.update_stock_report(df)
        await _log(ctx, 7, TOTAL_PHASES, f"财务指标写入: {err}（共 {len(df)} 条记录）")
    else:
        await _log(ctx, 7, TOTAL_PHASES, "未获取到任何财报数据")

    # 尝试二次拉取失败的股票
    if err_list:
        await _log(ctx, 7, TOTAL_PHASES, f"开始二次拉取 {len(err_list)} 只失败的股票")
        retry_list = list(err_list)
        err_list = []
        result_list = []
        t_start = time.time()
        last_log_time = t_start
        for i, code in enumerate(retry_list, 1):
            try:
                df = pro.fina_indicator(ts_code=code)
                if len(df)>0:
                    result_list.append(df)
                else:
                    err_list.append(code)
            except Exception as e:
                err_list.append(code)
            now = time.time()
            if i % 5 == 0 or now - last_log_time > HEARTBEAT_SEC:
                await _log(ctx, 7, TOTAL_PHASES, f"二次拉取 {i}/{len(retry_list)}（成功 {len(result_list)} 失败 {len(err_list)}）")
                last_log_time = now
            if (i+1) % 10 == 0:
                sl_time = 10-time.time()+t0
                if sl_time >0:
                    time.sleep(sl_time)
                t0 = time.time()
        if result_list:
            df = pd.concat(result_list, ignore_index=True)
            df.rename(columns={"ts_code":"symbol"},inplace=True)
            err = updb.update_stock_report(df)
            await _log(ctx, 7, TOTAL_PHASES, f"二次读取财务指标写入: {err}（补录 {len(result_list)} 只）")
    # 最终汇报
    if err_list:
        await _log(ctx, 7, TOTAL_PHASES, f"财报指标更新完成（最终失败 {len(err_list)} 只：{err_list[:8]}{'...' if len(err_list)>8 else ''}）")
    else:
        await _log(ctx, 7, TOTAL_PHASES, "财务指标全部更新完成！")
            
    # endregion 更新财务指标


async def example_baostock(DB_path:str='', ctx: Context=None):
    if datetime.now().hour<15:  # 15点前不更新当天的，避免异常
        today = datetime.now().date() - timedelta(days=1)
    else:
        today = datetime.now().date()
    # 调整到工作日
    if today.weekday() == 6:
        today = today - timedelta(days=2)
    elif today.weekday() == 5:
        today = today - timedelta(days=1)
    today_s = today.strftime('%Y-%m-%d')  # "2026-06-06" 格式
    updb = Updb(DB_path)  # 辅助适配到软件的数据库

    # 获取指数数据
    lg = bs.login()
    # 显示登陆返回信息
    if lg.error_code != '0':
        await _log(ctx, 1, 2, f'baostock login error: {lg.error_code} {lg.error_msg}')
    else:
        await _log(ctx, 1, 2, "baostock 登录成功")
    # 翻译字典，不同渠道的列名规则不不同，没有的可以自行添加
    translate = {"date":"trade_date",
                 "code":"symbol",
                 "preclose":"pre_close",
                 "volume":"vol",
                 "amount":"voe"}
    # 更新指数
    id_list = ["sz.399001","sh.000001"]
    for code in id_list:
        start_date:datetime = updb.date_stock_index(code)
        if start_date is None:
            # 数据库是空白的，设置你的数据库开始时间，默认两年
            start_date =  today - timedelta(days=730) # 两年前
            # start_date = datetime.strptime("2021-01-01",'%Y-%m-%d')
        elif today <= start_date:
            # 已更新到最新
            continue
        rs = bs.query_history_k_data_plus(code,
            "date,code,open,high,low,close,preclose,volume,amount",
            start_date=start_date.strftime('%Y-%m-%d'), 
            end_date=today_s, 
            frequency="d")
        if rs.error_code != '0':
            await _log(ctx, 1, 2, f'baostock query error: {rs.error_code} {rs.error_msg}')
        # 打印结果集
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        df = pd.DataFrame(data_list, columns=rs.fields)
        if len(df)>0:
            df.rename(columns=translate,inplace=True)
            df['vol'] = df['vol'].astype(float)/100  # 把单位调整成手
            df['vol'] = df['vol'].round(2)
            df['voe'] = df['voe'].astype(float)/1000  # 把单位调整成千元
            df['voe'] = df['voe'].round(2)
            err = updb.update_stock_index(df)
            await _log(ctx, 1, 2, f"baostock 指数 {code}: {err}")
        # time.sleep(1) 
    # return
    # 更新股票数据,这里比较麻烦，没看到按日期获取全A股票行情数据。
    # 需要遍历更新，这种行为服务器压力大，估计用不了多久就会被封IP
    # # 登出系统
    bs.logout() 
    await _log(ctx, 1, 2, "baostock 指数数据更新完成")


async def example_tushare_120(api:str='你的API',DB_path:str='',ignore_check:bool=False, ctx: Context=None):
    TOTAL_PHASES = 2
    if datetime.now().hour<15:  # 15点前不更新当天的，避免异常
        today = datetime.now().date() - timedelta(days=1)
    else:
        today = datetime.now().date()
    # 调整到工作日
    if today.weekday() == 6:
        today = today - timedelta(days=2)
    elif today.weekday() == 5:
        today = today - timedelta(days=1)
    
    today_s = today.strftime('%Y%m%d')  # "2026-06-06" 格式
    updb = Updb(DB_path)  # 辅助适配到软件的数据库
    pro = ts.pro_api(api)

    # region 120积分，更新股票数据
    dates_id:list[datetime] = updb.dates_await("stock")
    if not dates_id:
        await _log(ctx, 2, TOTAL_PHASES, "股票数据已是最新，无需更新")
    else:
        await _log(ctx, 2, TOTAL_PHASES, f"开始更新股票行情，共 {len(dates_id)} 个交易日待更新")
        t0 = time.time()
        for i,date in enumerate(dates_id):
            date_s = date.strftime('%Y%m%d')
            df_date = pro.daily(trade_date=date_s)
            if len(df_date)>0:
                df_date.rename(columns={"ts_code":"symbol","amount":"voe"},inplace=True)
                # 成交量tushare单位是手，成交额tushare单位是千元
                # 剔除北证券
                # df = df[~df['symbol'].str.startswith(tuple(['9']))]  # 如果你的数据库里有北证的，删掉这行
                err = updb.update_stock(df_date,ignore_check)  # 更新成功返回OK，否则返回错误原因
                await _log(ctx, 2, TOTAL_PHASES, f"股票行情 {date_s}: {err} ({i+1}/{len(dates_id)})")
                if err != "OK":
                    break
            else:
                # 交易日期用指数数据提取的，都是正常交易日，不能有数据缺失
                await _log(ctx, 2, TOTAL_PHASES, f"异常，{date_s}获取空数据")
                break
            # time.sleep(1.5)  # 连续跑大量的时候，减低点频率更稳定点
            if (i+1)%10 == 0:
                sl_time = 10-time.time()+t0
                if sl_time >0:
                    time.sleep(sl_time)  # 避免频率太高
                t0 = time.time()
    # endregion 更新股票数据
   
    await _log(ctx, 2, TOTAL_PHASES, "OK")  # 全A解析软件理解为脚本运行正常，不弹窗


def _is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """检查指定主机的端口是否处于监听状态（即服务已就绪）。"""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def _get_default_option()->dict:
    return {"db_path":os.path.join(os.path.dirname(__file__),"Test.duckdb"),
                "days": 730, 
                "ex_do": True, 
                "stock_index": "stock_index", 
                "map_stock_index": {
                    "trade_date": "trade_date", 
                    "symbol": "symbol", 
                    "open": "open", 
                    "high": "high", 
                    "low": "low", 
                    "close": "close", 
                    "pre_close": "pre_close", 
                    "vol": "vol", 
                    "voe": "voe"}, 
                "stock": "stock", 
                "map_stock": {
                    "trade_date": "trade_date", 
                    "symbol": "symbol", 
                    "open": "open", 
                    "high": "high", 
                    "low": "low", 
                    "close": "close", 
                    "pre_close": "pre_close", 
                    "vol": "vol", 
                    "voe": "voe"}, 
                "stock_basic": "stock_basic", 
                "map_stock_basic": {
                    "symbol": "symbol", 
                    "name": "name", 
                    "check": ["industry", "business_scope", "main_business", "province", "city", "act_ent_type", "concept"]}, 
                "stock_factor": "stock_factor", 
                "map_stock_factor": {
                    "symbol": "symbol", 
                    "trade_date": "trade_date"}, 
                "stock_forecast": "stock_forecast", 
                "map_stock_forecast": {
                    "symbol": "symbol", 
                    "ann_date": "ann_date"}, 
                "stock_dividend": "stock_dividend", 
                "map_stock_dividend": {
                    "symbol": "symbol", 
                    "ann_date": "ann_date", 
                    "ex_date": "ex_date"}, 
                "stock_report": "stock_report", 
                "map_stock_report": {
                    "symbol": "symbol", 
                    "ann_date": "ann_date"}, 
                "_": "_", 
                "map__": {}
            }


mcp = FastMCP("UpdateStock")

@mcp.tool()
def Creat_DB(
    DB_path: Annotated[str, Field(
        description="数据库的路径，空白为同目录下Test.duckdb的数据库。")]=''
    ) -> str:
    """
    创建存储股票数据的DuckDB数据库
    默认创建表格如下:
    stock:股票每日市场数据,
    stock_index:指数每日市场数据,
    stock_basic:股票列表及基础数据,
    stock_factor:股票每日因子数据,
    stock_forecast:业绩预告,
    stock_dividend:股票分红,
    stock_report:股票财报,
    """
    try:
        if not DB_path:
            DB_path = os.path.join(os.path.dirname(__file__),"Test.duckdb")
        if os.path.exists(DB_path):
            return f"运行失败，{DB_path}已经存在"
        updb = Updb(DB_path)
        updb.creat_duckdb(DB_path)
        return f"数据库创建完成，路径:{DB_path}"
    except Exception as e:
        return f"失败: {e}"


@mcp.tool()
def get_adj_stock(
    symbol: Annotated[str, Field(description="股票标示码，6为数字")]='000001',
    start_date: Annotated[str, Field(description="开始日期 格式:yyyy-MM-dd")]='',
    end_date: Annotated[str, Field(description="截止日期 格式:yyyy-MM-dd")]='',
              ) ->str:
    """
    获取前复权股票行情数据，输入股票标示码, 获取json文件
    """
    try:
        option_path = os.path.join(os.path.dirname(__file__) ,"DB_setting.json") 
        if os.path.isfile(option_path):
            with open(option_path,'r',encoding='utf-8') as file:
                fd:dict = json.load(file)
        else:
            fd = _get_default_option()
            with open(option_path, "w", encoding="utf-8") as file:
                json.dump(fd, file, ensure_ascii=False)
        DB_path = fd.get("db_path", "")

        sql = f"SELECT * FROM stock WHERE symbol='{symbol}' "
        if start_date:
            sql += f"AND trade_date >= '{start_date}' "
        if end_date:
            sql += f"AND trade_date <= '{end_date}' "
        sql += " ORDER BY trade_date;"
        with duckdb.connect(DB_path) as conn:
            df = conn.execute(sql).df()
        if len(df)<=0:
            return f"没找到{symbol}从{start_date}到{end_date}的数据"
        # df里面的列[trade_date, symbol, open, high, low, close, pre_close, vol,voe]
        # 利用pre_close对open, high, low, close进行前复权处理
        # ===================== 核心：前复权计算（纯 pandas） =====================
        # 转为 YYYY-MM-DD 字符串（AI 最容易理解、解析、计算）

        df['trade_date'] = pd.to_datetime(df['trade_date']).dt.strftime('%Y-%m-%d')
        # 1. 计算每日因子：下一日 pre_close / 当日 close
        df['factor'] = df['pre_close'].shift(-1) / df['close']
        df['factor'] = df['factor'].fillna(1.0)  # 最后一天因子为1

        # 2. 倒序 → 累乘 → 恢复顺序（完全参考你的逻辑）
        df_rev = df[::-1].copy()               # 倒装
        df_rev['adj_factor'] = df_rev['factor'].cumprod()  # 累积乘积
        df['adj_factor'] = df_rev['adj_factor'][::-1]      # 恢复顺序

        # 3. 前复权价格（直接覆盖原列，不改名字）
        df['open'] = df['open'] * df['adj_factor']
        df['high'] = df['high'] * df['adj_factor']
        df['low'] = df['low'] * df['adj_factor']
        df['close'] = df['close'] * df['adj_factor']

        # 4. 清理列：删除中间计算列 + 删除 pre_close
        df = df[['trade_date', 'symbol', 'open', 'high', 'low', 'close', 'vol', 'voe']]
        return df.to_json(orient='records', force_ascii=False)
    except Exception as e:
        return f"异常：{e}"


@mcp.tool()
def get_stock(
    symbol: Annotated[str, Field(description="股票标示码，6为数字")]='000001',
    start_date: Annotated[str, Field(description="开始日期 格式:yyyy-MM-dd")]='',
    end_date: Annotated[str, Field(description="截止日期 格式:yyyy-MM-dd")]='',
              ) ->dict:
    """
    从配置的数据库中，获取获取非复权股票行情数据，输入股票标示码, 获取json文件
    """
    try:
        option_path = os.path.join(os.path.dirname(__file__) ,"DB_setting.json") 
        if os.path.isfile(option_path):
            with open(option_path,'r',encoding='utf-8') as file:
                fd:dict = json.load(file)
        else:
            fd = _get_default_option()
            with open(option_path, "w", encoding="utf-8") as file:
                json.dump(fd, file, ensure_ascii=False)
        DB_path = fd.get("db_path", "")

        sql = f"SELECT * FROM stock WHERE symbol='{symbol}' "
        if start_date:
            sql += f"AND trade_date >= '{start_date}' "
        if end_date:
            sql += f"AND trade_date <= '{end_date}' "
        sql += " ORDER BY trade_date;"
        with duckdb.connect(DB_path) as conn:
            df = conn.execute(sql).df()
        if len(df)<=0:
            return f"没找到{symbol}从{start_date}到{end_date}的数据"
        df['trade_date'] = pd.to_datetime(df['trade_date']).dt.strftime('%Y-%m-%d')
        # df里面的列[trade_date, symbol, open, high, low, close, pre_close, vol,voe]
        return df.to_json(orient='records', force_ascii=False)
    except Exception as e:
        return f"异常：{e}"


@mcp.tool()
async def Update_Stock_Data(
    ctx: Context,
    ignore_check: Annotated[bool, Field(
        description="是否跳过部分检查，更新数据库")]=False,
    ) -> str:
    """
    更新全股票市场的数据，tushare的积分需要2000以上。
    DB_path 是数据库的路径，缺失会在文件所在目录，查找【Test.duckdb】的数据库。
    API 是你的tushare的API
    为方便调用，可在文件DB_setting.json和API_tushare.txt里设置相应的默认值。
    备注：
    1.脚本优先会优先选择【全A解析】的数据库，缺失时才使用DB_path；
    2.第一次更新数据库，需要的时间会比较长，可能要几小时；
    3.更新过程中会持续发送进度通知，避免长时间无响应导致连接超时。
    """
    try:
        option_path = os.path.join(os.path.dirname(__file__) ,"DB_setting.json") 
        if os.path.isfile(option_path):
            with open(option_path,'r',encoding='utf-8') as file:
                fd:dict = json.load(file)
        else:
            fd = _get_default_option()
            with open(option_path, "w", encoding="utf-8") as file:
                json.dump(fd, file, ensure_ascii=False)
        DB_path = fd.get("db_path", "")
        # 没有输入数据库路径，找同目录下是否有指定数据库
        if not os.path.exists(DB_path):
            return f"运行失败，{DB_path}不存在"
        # # 没有输入API，找同目录下是否有保存API的文件
        
        fp = os.path.join(os.path.dirname(__file__),"API_tushare.txt")
                # 检查fp文件是否存在
        if not os.path.exists(fp):
            # 不存在则创建文件并写入空白文本
            with open(fp, 'w', encoding='utf-8') as f:
                f.write('')  # 写入空字符串
        # 读取文件内容
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        if content:
            API = content
        else:
            return  f"没API,请在{fp}里面添加thshare的API"
        await example_tushare_2000(API,DB_path,ignore_check, ctx)
        return f"数据库更新完成"
    except Exception as e:
        return f"计算错误: {e}"


@mcp.tool()
async def Update_Stock_Data_easy(
    ctx: Context,
    ignore_check: Annotated[bool, Field(
        description="是否跳过部分检查，更新数据库")]=False,
    ) -> str:
    """
    部分更新全股票市场数据，对于tushare积分只有120的用户，仅更新指数行情和股票行情两张表；
    DB_path 是数据库的路径，缺失会在文件所在目录，查找【Test.duckdb】的数据库。
    API 是你的tushare的API
    为方便调用，可在文件DB_setting.json和API_tushare.txt里设置相应的默认值。
    备注，脚本优先会优先选择QuantAll(全A解析)的数据库，缺失时才使用DB_path。
    更新过程中会持续发送进度通知，避免长时间无响应导致连接超时。
    """
    try:
        option_path = os.path.join(os.path.dirname(__file__) ,"DB_setting.json") 
        if os.path.isfile(option_path):
            with open(option_path,'r',encoding='utf-8') as file:
                fd:dict = json.load(file)
        else:
            fd = _get_default_option()
            with open(option_path, "w", encoding="utf-8") as file:
                json.dump(fd, file, ensure_ascii=False)
        DB_path = fd.get("db_path", "")
        # 没有输入数据库路径，找同目录下是否有指定数据库
        if not os.path.exists(DB_path):
            return f"运行失败，{DB_path}不存在"
        fp = os.path.join(os.path.dirname(__file__),"API_tushare.txt")
        # 检查fp文件是否存在
        if not os.path.exists(fp):
            # 不存在则创建文件并写入空白文本
            with open(fp, 'w', encoding='utf-8') as f:
                f.write('')  # 写入空字符串
        # 读取文件内容
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        if content:
            API = content
        else:
            return  f"没API,请在{fp}里面添加thshare的API"
        await example_baostock(DB_path, ctx)
        await example_tushare_120(API,DB_path,ignore_check, ctx)
        return f"数据库更新完成"
    except Exception as e:
        return f"计算错误: {e}"


@mcp.tool()
def Start_QuantAll() -> str:
    """
    启动 QuantAll（全A解析）MCP 服务。

    【功能定位】
    本工具用于在本地启动另一个独立的 MCP 服务——QuantAll。
    QuantAll 提供全市场股票数据的高效计算引擎，将所有维度数据组织为矩阵向量，自动处理停牌、复权等问题，
    并为 AI 预置了 Python 执行环境。AI 只需编写简洁的算法代码，即可在几秒内完成全市场结构分析。

    【使用场景】
    当您需要调用 QuantAll 提供的市场数据或执行批量计算时，应首先调用本工具启动该服务。
    服务启动后，QuantAll 会以 HTTP 方式在本地 8686 端口提供 MCP 接口。

    【启动流程】
    1. 本工具首先检查本地 8686 端口是否已被占用：
       - 如果已被占用，则认为 QuantAll 服务已在运行，直接返回已就绪提示。
       - 否则，会在相同的 Python 解释器环境下，异步启动与当前文件同目录的 `QuantAll.py` 子进程。
    2. 启动子进程后，本工具会循环检测 8686 端口是否开放，直到服务就绪或超过 30 秒超时。
    3. 一旦端口开放，立即返回成功信息，表明服务已完全就绪，可直接连接使用。

    【重要注意事项】
    - 本工具内置了端口检测机制，可防止重复启动多个 QuantAll 实例。
    - 如果端口被其他非 QuantAll 服务占用，本工具会误判为已启动，请确保端口独占。
    - 启动后若长时间无法就绪（超过 15 秒），请检查 Start_QuantAll.py 是否正常运行或端口是否被防火墙拦截。

    Returns:
        str: 包含服务状态、PID（若新启动）和连接地址的提示信息。
    """
    # 1. 检查端口是否已占用（服务已在运行）
    if _is_port_open("127.0.0.1", 8686, timeout=0.5):
        return (f"QuantAll 服务已在运行，可直接连接 http://127.0.0.1:8686/mcp 。\n"
                "如需重启，请先终止已有进程。")

    # 2. 检查 QuantAll 包是否已安装
    try:
        from QuantAll import  Start_main
        # 可选：检查是否有 Start_main 函数（但不强制，因为启动用 -m）
    except ImportError as e:
        # 查找当前目录下是否有 whl 文件，以提供更精确的安装提示
        return ("QuantAll 包未安装。\n"
                "安装方法 pip install quantall -i https://pypi.tuna.tsinghua.edu.cn/simple")

    # 3. 准备启动子进程
    current_dir = Path(__file__).parent.resolve()
    target_script = current_dir / "Start_QuantAll.py"
    # if not target_script.exists():
        # 创建该文件，
        # return f"错误：未找到 Start_QuantAll.py 文件（期望路径：{target_script}）"
    if not target_script.exists():
    # 写入内容
        content = '''import os
from QuantAll import Start_main
Start_main(os.path.dirname(__file__))
'''
        target_script.write_text(content, encoding='utf-8')


    python_exe = sys.executable
    try:
        # 启动子进程（忽略 I/O）
        if sys.platform == "win32":
            process = subprocess.Popen(
                [python_exe, str(target_script)],
                cwd=str(current_dir),
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )
        else:
            process = subprocess.Popen(
                [python_exe, str(target_script)],
                cwd=str(current_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True
            )
        pid = process.pid
    except Exception as e:
        return f"启动 QuantAll 子进程失败：{e}"

    # 3. 等待端口就绪（轮询检测）
    start_time = time.time()
    while time.time() - start_time < 15:
        if _is_port_open("127.0.0.1", 8686, timeout=0.001):
            elapsed = round(time.time() - start_time, 1)
            return (f"QuantAll 服务已启动（PID: {pid}），已就绪。\n"
                    f"请连接 http://127.0.0.1:8686/mcp 使用。")
        time.sleep(1)

    # 超时未就绪
    return (f"QuantAll 子进程已启动（PID: {pid}），但在 10 秒内未能检测到端口8686 开放。\n"
            "请检查 QuantAll.py 是否正常运行或端口是否被占用。\n"
            "【提示】有些智能体，比如WorkBuddy需要在连接器里面重新连接或者重启才能正常使用"
            )


@mcp.tool()
def Set_QuantAll_DataBase(
    path: Annotated[str, Field(description="数据库的路径")]='',
    days: Annotated[int, Field(
        description="QuantAll加载数据的天数，大于5，默认连年730")]=730,
        ) -> str:
    """
    设置QuantAll加载的数据库路径及需要读取的天数。
    对应的数据库优先使用本mcp提供的'Creat_DB'，默认参数已经匹配好了。
    自定义的数据库，可在本py文件同目录下的"DB_setting.json"文件里面设置，
    """
    option_path = os.path.join(os.path.dirname(__file__),"DB_setting.json") 
    if os.path.isfile(option_path):
        with open(option_path,'r',encoding='utf-8') as file:
            fd:dict = json.load(file)
    else:
        fd = _get_default_option()
        with open(option_path, "w", encoding="utf-8") as file:
            json.dump(fd, file, ensure_ascii=False)
    old_path = fd.get("db_path","") # 数据库的路径
    
    # 如果没传入数据库路径
    if not path or not os.path.isfile(path):
        return f"修改失败！传入路径{path}无效，当前使用的路径{old_path}"
    fd["db_path"] = path
    if days>=5:
        fd["days"] = int(days)
    else:
        return f"设置参数异常，days:{days}应该是大于5整数"
    with open(option_path, "w", encoding="utf-8") as file:
        json.dump(fd, file, ensure_ascii=False)

    return f"修改成功，当前数据库的路径{path}，加载天数{days}"


@mcp.tool()
def ping()->str:
    """
    检查是否能连接
    """
    return "Pong"


if __name__=='__main__':
    # 检查数据库设置文件是否存在，缺失时自动创建默认值的设置文件
    option_path = os.path.join(os.path.dirname(__file__) ,"DB_setting.json") 
    if not os.path.isfile(option_path):
        fd = _get_default_option()
        with open(option_path, "w", encoding="utf-8") as file:
            json.dump(fd, file, ensure_ascii=False)

    mcp.run()
   
