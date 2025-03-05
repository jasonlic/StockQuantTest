#测试 英伟达 和 nvidia 股价相关性，算法源自 deepseek
'''
pip install akshare

'''
import pandas as pd
import akshare as ak

from pylab import mpl
import matplotlib.pyplot as plt
mpl.rcParams['font.sans-serif']=['SimHei']
mpl.rcParams['axes.unicode_minus']=False
'''
工业富联和NVIDIA股价的相关性，代码实现,基于deepseek
'''

# 设置股票代码和时间范围
start_date = '2024-01-01'
end_date = '2025-03-03'
#foxconn = yf.download('601138.SS', start=start_date, end=end_date)  # 工业富联（A股）
#date	datetime64
nvda  = ak.stock_us_daily(symbol="NVDA", adjust="qfq")      # 英伟达（美股）
'''
     date         open      high       low      close       volume
0    1999-01-22   -0.1599   -0.1573   -0.1624   -0.1612   67867200.0
1    1999-01-25   -0.1596   -0.1588   -0.1612   -0.1591   12762000.0
'''
df_nvda = nvda[["date","close"]].rename(columns={"date":"日期","close": "英伟达"})
#df_nvda['日期'] = pd.to_datetime(df_nvda['日期']).astype('object')
#df_nvda['日期'] = df_nvda['日期'].dt.strftime('%Y-%m-%d')
#print(df_nvda)
#print(type(df_nvda['日期']))
'''
     日期     英伟达
0    1999-01-22   -0.1612
1    1999-01-25   -0.1591
'''

# 获取工业富联历史股价数据（示例为2024年数据）
#日期	object	交易日
gongye_fulian = ak.stock_zh_a_hist(symbol="601138", period="daily", 
    start_date="20240101", 
    end_date="20250304",
    adjust="qfq"  # 前复权
)
#print(gongye_fulian)
'''
   日期    股票代码     开盘     收盘     最高     最低      成交量           成交额    振幅   涨跌幅   涨跌额   换手率
0    2024-01-02  601138  14.42  13.62  14.42  13.45  1280166  1.834238e+09  6.67 -6.33 -0.92  0.65
'''
# 提取收盘价并合并
df_gf = gongye_fulian[["日期", "收盘"]].rename(columns={"收盘": "工业富联"})
df_gf['日期']=pd.to_datetime(df_gf['日期']).dt.normalize()
#print(type(df_gf['日期']))
#print(df_gf)
'''
     日期        工业富联
0    2024-01-02  13.62
'''


#merged_df = pd.merge(df_gf, df_nvda, left_on="日期", right_index=True, how="inner")
merged_df = pd.merge(df_gf, df_nvda, on='日期', how='outer').sort_values('日期')
#print(merged_df)
#merged_df.dropna(axis=0,how='any')
merged_df = merged_df.dropna()
#print(merged_df)
'''
  日期   工业富联      英伟达
5086 2024-01-02  13.62   48.134
5087 2024-01-03  13.30   47.535
5088 2024-01-04  12.89   47.964
5089 2024-01-05  12.72   49.063
5090 2024-01-08  12.50   52.219
...         ...    ...      ...
5386 2025-02-26  22.77  131.280
5387 2025-02-27  21.96  120.150
5388 2025-02-28  21.19  124.920
5389 2025-03-03  21.07  114.060
5390 2025-03-04  21.04  115.990

[268 rows x 3 columns]
'''


#步骤2：计算收益率与相关系数
# 计算每日收益率
#returns = merged_df.pct_change().dropna()
returns_gyfl = merged_df["工业富联"].pct_change()
returns_nvida = merged_df["英伟达"].pct_change()
#print(returns_gyfl)
# print(type(returns_gyfl)) <class 'pandas.core.series.Series'>
returns = pd.concat([returns_gyfl,returns_nvida], axis=1)
#print(returns)
'''
 工业富联       英伟达
5086       NaN       NaN
5087 -0.023495 -0.012444
5088 -0.030827  0.009025
5089 -0.013189  0.022913
5090 -0.017296  0.064325
...        ...       ...
5386 -0.013432  0.036721
5387 -0.035573 -0.084781
5388 -0.035064  0.039700
5389 -0.005663 -0.086936
5390 -0.001424  0.016921

[268 rows x 2 columns]
'''
# Pearson相关系数
correlation = returns.corr().iloc[0, 1]
print(f"收益率相关系数：{correlation:.2f}")

#步骤3：可视化分析
# 输出示例（假设）：收益率相关系数：0.68

import matplotlib.pyplot as plt
import seaborn as sns

# 股价走势对比
plt.figure(figsize=(12, 6))
merged_df.plot(x='日期',secondary_y=['英伟达'], 
                title='工业富联 vs 英伟达股价走势')
plt.show()

# 收益率散点图与回归线
sns.jointplot(x=returns_gyfl, 
              y=returns_nvida, 
              kind='reg', height=8)
plt.suptitle('收益率相关性分析', y=1.02)
plt.show()

#步骤4：滚动相关系数（动态分析）
# 计算30日滚动相关系数
rolling_corr = returns_gyfl.rolling(window=30).corr(returns_nvida)

# 可视化
plt.figure(figsize=(12, 4))
rolling_corr.plot(title='30日滚动相关系数')
plt.axhline(correlation, color='r', linestyle='--', label='整体相关系数')
plt.legend()
plt.show()
