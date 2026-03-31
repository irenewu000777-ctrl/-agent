"""
fetch_rate.py — 从 frankfurter.app 获取 CNY/SGD 汇率，追加写入 history.csv
"""
import csv
import os
import requests
from datetime import datetime, timezone, timedelta

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "history.csv")
CSV_HEADERS = ["timestamp", "rate"]

# 中国标准时间 UTC+8
CST = timezone(timedelta(hours=8))


def fetch_cny_sgd() -> float:
    """从 frankfurter.app 获取 1 CNY = ? SGD"""
    url = "https://api.frankfurter.app/latest?from=CNY&to=SGD"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return float(data["rates"]["SGD"])


def load_history() -> list[dict]:
    """读取历史 CSV，返回 [{timestamp, rate}, ...] 列表"""
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            rows.append({"timestamp": row["timestamp"], "rate": float(row["rate"])})
        return rows


def append_record(rate: float) -> str:
    """将本次汇率追加到 CSV，返回时间戳字符串"""
    now = datetime.now(CST).strftime("%Y-%m-%d %H:%M")
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    file_exists = os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({"timestamp": now, "rate": rate})
    return now


if __name__ == "__main__":
    rate = fetch_cny_sgd()
    ts = append_record(rate)
    print(f"[{ts}] 1 CNY = {rate:.6f} SGD")
