# Tushare 在本项目的应用

> 事实基线：当前仓库 `data_provider/tushare_fetcher.py`、`DataFetcherManager`、配置项 `TUSHARE_TOKEN`。  
> 接口语义参见同目录 [Tushare 接口文档.md](./Tushare%20接口文档.md)。

## 1. 角色定位

Tushare 是本项目的**可选增强数据源**，不是硬依赖：

| 场景 | 行为 |
|------|------|
| 未配置 `TUSHARE_TOKEN` | Tushare 不可用；走 Efinance / AkShare / Baostock / YFinance 等免费源 |
| 已配置且初始化成功 | `TushareFetcher.priority` 提升为 **-1（最高）**，优先于默认 efinance |
| 单接口失败 / 配额不足 | 抛错或返回空后由 `DataFetcherManager` **fallback** 到下一源 |

配置：

```env
TUSHARE_TOKEN=你的token
# 可选：覆盖默认优先级数字（一般无需设置）
# TUSHARE_PRIORITY=2
```

入口说明亦见 `docs/data-source-stability.md`、`docs/full-guide.md`。

## 2. 实现要点

### 2.1 客户端

- 类：`TushareFetcher`（`data_provider/tushare_fetcher.py`）
- 内置 `_TushareHttpClient`：直接 POST `api.tushare.pro`，**启动不强制 `import tushare`**
- 统一包一层速率限制：`rate_limit_per_minute` + 超限休眠

### 2.2 本项目实际调用的 Pro 接口

| 能力 | 使用的接口 | 代码用途 |
|------|------------|----------|
| A 股日线 | `daily` | `get_daily_data` → 技术分析 K 线 |
| ETF 日线 | `fund_daily` | ETF 代码分支 |
| 港股日线 | `hk_daily` | 港股代码分支（单位不做 A 股式缩放） |
| 股票名称 | `stock_basic` / `hk_basic` / `fund_basic` | `get_stock_name` |
| A 股列表 | `stock_basic` | `get_stock_list`、补全索引相关脚本 |
| 实时行情 | `quotation`，失败降级旧版 `ts.get_realtime_quotes` | `get_realtime_quote` |
| 指数 | `index_daily` | `get_main_indices`（取近几日） |
| 市场统计 | `rt_k` / `daily` 等（见实现） | `get_market_stats`（门槛较高） |

**不支持**：美股（明确拒绝，交给 AkShare/YFinance）。

### 2.3 数据归一化（与官方字段差异）

`daily` / `fund_daily` 标准化时（A 股）：

- `trade_date` → `date`（`YYYY-MM-DD`）
- `vol`（手）→ `volume`（股，×100）
- `amount`（千元）→ `amount`（元，×1000）

港股 `hk_daily`：**不做**上述量纲缩放。

## 3. 在业务链路中的位置

```text
配置 TUSHARE_TOKEN
    → DataFetcherManager 注册 TushareFetcher（高优先级）
    → 个股分析 / 大盘复盘 / 持仓估值 请求日线或实时
    → 成功则用 Tushare 数据；失败则 fallback
    → 技术指标与 LLM 分析消费归一化后的 DataFrame / Quote
```

相关扩展：

- AlphaSift：有 Token 时快照优先级可含 `tushare`（见 `docs/alphasift-integration.md`）
- 列表工具：`scripts/fetch_tushare_stock_list.py`、`docs/TUSHARE_STOCK_LIST_GUIDE.md`

## 4. 课程侧用法（北科大 2026）

| 脚本 | 目的 |
|------|------|
| `examples/北科大2026/04_验证Tushare接口.py` | 最低门槛连通（`stock_basic` limit=1） |
| `examples/北科大2026/06_tushare的综合应用.py` | 基础信息 + 日线综合样例，输出 CSV |

Token 建议放在：

- 环境变量 `TUSHARE_TOKEN`，或  
- `examples/北科大2026/tushare_token.txt`（已 gitignore，禁止提交）

也可写入项目根 `.env` 的 `TUSHARE_TOKEN=`，供主程序 Web/分析使用。

## 5. 运维注意

1. **积分不足**：日志常见「权限/配额」；分析不会中断，会换源。  
2. **不要在日志打印完整 Token**。  
3. **Docker/桌面**：HTTP client 路径已降低对 SDK 包的依赖；仍需网络可达 `api.tushare.pro`。  
4. **高频批量**：优先按交易日拉取；遵守每分钟频次，避免触发限流休眠影响任务时长。

## 6. 相关文件索引

| 路径 | 说明 |
|------|------|
| `data_provider/tushare_fetcher.py` | 实现 |
| `data_provider/base.py` | 多源路由 |
| `src/config.py` | `tushare_token` 读取 |
| `.env.example` | `TUSHARE_TOKEN` 示例 |
| `docs/数据源/04-数据源说明/数据源能力矩阵.md` | 能力总表一行 |
| `docs/TUSHARE_STOCK_LIST_GUIDE.md` | 列表抓取工具 |
