from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd


TOKEN_FILE = Path(__file__).resolve().parent / "tushare_token.txt"


def mask_token(token: str) -> str:
    token = (token or "").strip()
    if len(token) <= 12:
        return "***"
    return f"{token[:4]}...{token[-4:]} (len={len(token)})"


def resolve_token(cli_token: str | None) -> str:
    if cli_token and cli_token.strip():
        return cli_token.strip()
    env_token = os.getenv("TUSHARE_TOKEN", "").strip()
    if env_token:
        return env_token
    if TOKEN_FILE.is_file():
        file_token = TOKEN_FILE.read_text(encoding="utf-8").strip()
        if file_token:
            return file_token
    raise FileNotFoundError(
        "未找到 Tushare Token。请设置 TUSHARE_TOKEN，或创建 tushare_token.txt"
    )


def verify_with_min_points(token: str) -> pd.DataFrame:
    """只用最低门槛接口 stock_basic（约 120 积分），且只取 1 条。"""
    try:
        import tushare as ts
    except ImportError as exc:
        raise RuntimeError("未安装 tushare，请先：pip install tushare") from exc

    ts.set_token(token)
    pro = ts.pro_api()
    # stock_basic 是常用接口里门槛最低的之一；limit=1 尽量少占额度
    df = pro.stock_basic(
        exchange="SSE",
        list_status="L",
        fields="ts_code,symbol,name",
        limit=1,
    )
    if df is None or df.empty:
        raise RuntimeError("stock_basic 返回空数据")
    return df.head(1)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="用最少积分验证 Tushare Token")
    parser.add_argument("--token", default=None)
    args = parser.parse_args(argv)

    try:
        token = resolve_token(args.token)
        print(f"Token 指纹：{mask_token(token)}")
        print("调用最低门槛接口：stock_basic（limit=1）...")
        sample = verify_with_min_points(token)
    except Exception as exc:
        print(f"验证失败：{exc}")
        return 1

    print("验证成功：Token 可用")
    print(sample.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
