from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve().parent
TOKEN_FILE = HERE / "tushare_token.txt"
OUT_BASIC = HERE / "tushare_综合_基础信息.csv"
OUT_DAILY = HERE / "tushare_综合_日线.csv"
OUT_REPORT = HERE / "tushare_综合_报告.txt"

# 课程演示标的：daily 约 120 积分起；短区间控制调用量
DEMO_TS_CODE = "600519.SH"


def mask_token(token: str) -> str:
    token = (token or "").strip()
    if len(token) <= 12:
        return "***"
    return f"{token[:4]}...{token[-4:]} (len={len(token)})"


def load_token() -> str:
    env = os.getenv("TUSHARE_TOKEN", "").strip()
    if env:
        return env
    if TOKEN_FILE.is_file():
        value = TOKEN_FILE.read_text(encoding="utf-8").strip()
        if value:
            return value
    raise FileNotFoundError(
        "未找到 Token：请设置 TUSHARE_TOKEN 或创建 tushare_token.txt"
    )


def get_pro(token: str):
    import tushare as ts

    ts.set_token(token)
    return ts.pro_api()


def fetch_daily(pro) -> pd.DataFrame:
    """日线：单票 + 近 14 自然日，省积分/频次。"""
    end = datetime.now()
    start = end - timedelta(days=14)
    df = pro.daily(
        ts_code=DEMO_TS_CODE,
        start_date=start.strftime("%Y%m%d"),
        end_date=end.strftime("%Y%m%d"),
        fields="ts_code,trade_date,open,high,low,close,pre_close,pct_chg,vol,amount",
    )
    if df is None or df.empty:
        raise RuntimeError(f"daily 返回空数据：{DEMO_TS_CODE}")
    return df.sort_values("trade_date").reset_index(drop=True)


def fetch_basic_one(pro) -> pd.DataFrame:
    """只查一只股票基础信息，避免全市场拉取。"""
    df = pro.stock_basic(
        ts_code=DEMO_TS_CODE,
        fields="ts_code,symbol,name,area,industry,list_date,market",
    )
    if df is None or df.empty:
        raise RuntimeError("stock_basic 返回空数据")
    return df.reset_index(drop=True)


def soft_call(name: str, fn) -> tuple[str, pd.DataFrame | None]:
    try:
        df = fn()
        if df is None or (hasattr(df, "empty") and df.empty):
            return f"{name}: 空结果", None
        return f"{name}: OK rows={len(df)}", df
    except Exception as exc:  # noqa: BLE001
        return f"{name}: SKIP ({exc})", None


def main() -> int:
    lines: list[str] = []
    try:
        token = load_token()
        print(f"Token 指纹：{mask_token(token)}")
        pro = get_pro(token)

        # 先跑低门槛、高成功率的 daily，避免被 stock_basic 小时级限频卡住整课
        print(f"1/3 拉取日线 daily ({DEMO_TS_CODE}) ...")
        daily = fetch_daily(pro)
        daily.to_csv(OUT_DAILY, index=False, encoding="utf-8-sig")
        lines.append(f"daily({DEMO_TS_CODE}): OK rows={len(daily)} -> {OUT_DAILY.name}")
        print(f"  OK rows={len(daily)}")

        print(f"2/3 拉取单票基础信息 stock_basic({DEMO_TS_CODE}) ...")
        basic_msg, basic = soft_call("stock_basic", lambda: fetch_basic_one(pro))
        lines.append(basic_msg)
        print(f"  {basic_msg}")
        if basic is not None:
            basic.to_csv(OUT_BASIC, index=False, encoding="utf-8-sig")
            lines.append(f"  saved -> {OUT_BASIC.name}")
        elif OUT_BASIC.is_file():
            lines.append(f"  复用本地缓存 -> {OUT_BASIC.name}")
            try:
                basic = pd.read_csv(OUT_BASIC)
            except Exception:  # noqa: BLE001
                basic = None

        print("3/3 可选高门槛接口（失败仅记录）...")
        cal_msg, _ = soft_call(
            "trade_cal",
            lambda: pro.trade_cal(
                exchange="SSE",
                start_date=datetime.now().strftime("%Y%m%d"),
                end_date=datetime.now().strftime("%Y%m%d"),
            ),
        )
        lines.append(cal_msg)
        print(f"  {cal_msg}")

        db_msg, _ = soft_call(
            "daily_basic",
            lambda: pro.daily_basic(
                ts_code=DEMO_TS_CODE,
                trade_date=str(daily.iloc[-1]["trade_date"]),
                fields="ts_code,trade_date,pe,pb,total_mv,circ_mv",
            ),
        )
        lines.append(db_msg)
        print(f"  {db_msg}")

        name = ""
        if basic is not None and not basic.empty:
            hit = basic[basic["ts_code"] == DEMO_TS_CODE]
            if not hit.empty:
                name = str(hit.iloc[0].get("name", ""))

        last = daily.iloc[-1]
        summary = [
            "=== Tushare 综合应用报告 ===",
            f"时间: {datetime.now().isoformat(timespec='seconds')}",
            f"Token: {mask_token(token)}",
            f"标的: {DEMO_TS_CODE} {name}".rstrip(),
            f"日线区间条数: {len(daily)}",
            f"最新交易日: {last['trade_date']} 收盘={last['close']} 涨跌幅%={last['pct_chg']}",
            "",
            "步骤结果:",
            *[f"  - {x}" for x in lines],
            "",
            "输出文件:",
            f"  - {OUT_DAILY}",
            f"  - {OUT_BASIC if OUT_BASIC.is_file() else '(基础信息未生成)'}",
            f"  - {OUT_REPORT}",
            "",
            "说明: 积分是权限门槛而非按次扣减；stock_basic 低积分账号可能有小时级频次限制。",
        ]
        report = "\n".join(summary) + "\n"
        OUT_REPORT.write_text(report, encoding="utf-8")
        print()
        print(report)
        return 0
    except Exception as exc:
        print(f"执行失败：{exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
