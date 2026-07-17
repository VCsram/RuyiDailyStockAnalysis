# Tushare 接口文档（课程精简版）

> 整理依据：Tushare Pro 官方文档与权限说明（检索日期 2026-07-17）。  
> 积分门槛会随平台调整，**以官网实时页面为准**：  
> - 文档首页：https://tushare.pro/document/2  
> - 积分权限表：https://tushare.pro/document/1?doc_id=108  
> - 积分说明：https://tushare.pro/document/1?doc_id=230

## 1. 是什么

Tushare Pro 是面向量化/投研的金融数据平台，通过 HTTP / Python SDK 提供 A 股、港股、基金、指数、财务等数据。

- 官网：https://tushare.pro  
- HTTP 入口：`http://api.tushare.pro` 或 `https://api.tushare.pro`  
- Python：`pip install tushare`（建议 `>=1.2.10`）

## 2. 接入方式

### 2.1 Python SDK

```python
import tushare as ts

ts.set_token("YOUR_TOKEN")          # 或 pro_api(token) 直接传入
pro = ts.pro_api()

df = pro.stock_basic(
    exchange="SSE",
    list_status="L",
    fields="ts_code,symbol,name,area,industry,list_date",
)
```

### 2.2 HTTP JSON

```bash
curl -X POST https://api.tushare.pro \
  -H "Content-Type: application/json" \
  -d '{
    "api_name": "daily",
    "token": "YOUR_TOKEN",
    "params": {"ts_code": "000001.SZ", "start_date": "20260101", "end_date": "20260110"},
    "fields": "ts_code,trade_date,open,high,low,close,vol"
  }'
```

本仓库运行时主路径使用内置 HTTP client（见 `data_provider/tushare_fetcher.py`），不强制依赖 SDK 包。

## 3. 代码规范：`ts_code`

| 市场 | 后缀 | 示例 |
|------|------|------|
| 上交所 | `.SH` | `600519.SH` |
| 深交所 | `.SZ` | `000001.SZ` |
| 北交所 | `.BJ` | `920000.BJ`（以官网为准） |
| 港交所 | `.HK` | `00700.HK` |

日期参数统一 `YYYYMMDD`。

## 4. 常用接口速查

> 下表「常见门槛」综合官方权限页与社区实践；个别接口详情页标注可能与权限总表不一致，以 [doc_id=108](https://tushare.pro/document/1?doc_id=108) 为准。  
> **积分是门槛，不是每次调用扣分**；积分越高，每分钟可调用频次通常越高。

### 4.1 基础数据

| 接口 | 用途 | 常见门槛 | 关键参数 | 文档 |
|------|------|----------|----------|------|
| `stock_basic` | 股票列表/基础信息 | 约 120～2000（页面标注不一） | `exchange` / `list_status` / `ts_code` / `fields` | [doc_id=25](https://tushare.pro/document/2?doc_id=25) |
| `trade_cal` | 交易日历 | 约 2000 | `exchange` / `start_date` / `end_date` / `is_open` | [交易日历](https://tushare.pro/document/2?doc_id=26) |
| `stock_company` | 上市公司信息 | 视权限表 | `ts_code` | 官网「上市公司」目录 |
| `new_share` | IPO 新股 | 约 120 | 日期区间 | 权限表 |

### 4.2 行情数据

| 接口 | 用途 | 常见门槛 | 关键参数 | 备注 |
|------|------|----------|----------|------|
| `daily` | A 股日线 | **120 起** | `ts_code` / `trade_date` / `start_date` / `end_date` | 未复权；收盘后约 15–17 点更新 |
| `weekly` / `monthly` | 周/月线 | 约 2000 | 同上 | |
| `adj_factor` | 复权因子 | 约 2000 | `ts_code` / 日期 | 与 `daily` 合并可算前/后复权 |
| `daily_basic` | 每日指标 PE/PB/市值等 | 约 2000 | `ts_code` / `trade_date` | |
| `hk_daily` | 港股日线 | 视权限 | `ts_code` | |
| `fund_daily` | ETF/基金日线 | 视权限 | `ts_code` | |
| `index_daily` | 指数日线 | 视权限 | `ts_code` | |

**批量拉取建议**（官方实践）：

- 要全市场历史：按 `trade_date` 循环，而不是对 5000+ 只股票按 `ts_code` 循环。  
- 要单票历史：用 `ts_code + start_date + end_date`。

### 4.3 财务与资金（高门槛，课程慎用）

| 接口 | 用途 | 常见门槛 |
|------|------|----------|
| `income` / `balancesheet` / `cashflow` | 三大表 | 约 2000～5000 |
| `fina_indicator` | 财务指标 | 约 2000～5000 |
| `moneyflow` | 个股资金流向 | 约 2000 |
| `top_list` | 龙虎榜 | 约 2000 |
| `margin` / `margin_detail` | 两融 | 约 2000 |

## 5. `daily` 常用字段

| 字段 | 含义 | 单位注意 |
|------|------|----------|
| `ts_code` | 代码 | |
| `trade_date` | 交易日 | `YYYYMMDD` |
| `open/high/low/close` | OHLC | 元 |
| `pre_close` | 昨收 | 元 |
| `change` / `pct_chg` | 涨跌额/幅 | |
| `vol` | 成交量 | **手**（本项目归一化时 ×100 转股） |
| `amount` | 成交额 | **千元**（本项目归一化时 ×1000 转元） |

## 6. 积分与频次（要点）

1. 注册约 100 分，完善个人信息约 +20 分 → 凑齐 **120** 即可用 `daily` 等基础行情。  
2. 积分不够会返回类似：`抱歉，您没有接口(...)访问权限`。  
3. 频次与积分档位相关，详见权限页；本项目 `TushareFetcher` 内置每分钟调用计数与休眠。  
4. 省积分/省额度的写法：
   - 缩小 `fields`
   - 缩小日期区间
   - 加 `exchange` / `ts_code` / `limit`（若 SDK 支持）
   - 列表类接口拉一次后落盘复用（课程示例会写 CSV）

## 7. 错误与排障

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| Token 不正确 | 复制错误/已重置 | 在个人中心重新复制 |
| 没有接口访问权限 | 积分不足 | 完成资料/签到/贡献提升积分 |
| 空 DataFrame | 非交易日或代码错误 | 检查 `ts_code`、日期 |
| 超时/连接失败 | 网络或 DNS | 检查能否访问 `api.tushare.pro` |

本仓库课程验证脚本：

- `examples/北科大2026/04_验证Tushare接口.py`（最低门槛连通）
- `examples/北科大2026/06_tushare的综合应用.py`（基础信息 + 日线综合）

## 8. 参考链接

- 接口总览：https://tushare.pro/document/2  
- 权限积分：https://tushare.pro/document/1?doc_id=108  
- 调取说明：https://tushare.pro/document/1?doc_id=230 / https://tushare.pro/document/1?doc_id=131  
- 股票列表：https://tushare.pro/document/2?doc_id=25  
- 交易日历：https://tushare.pro/document/2?doc_id=26  
