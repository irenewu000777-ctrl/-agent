"""
analyze.py — 分析汇率变化、计算均线、线性回归预测
"""
import numpy as np
from datetime import datetime, timedelta


def compute_change(history: list[dict]) -> dict:
    """对比最新两条记录，返回变化信息"""
    if len(history) < 2:
        return {"current": history[-1]["rate"] if history else 0,
                "previous": None, "change": 0.0, "change_pct": 0.0,
                "direction": "—"}
    current = history[-1]["rate"]
    previous = history[-2]["rate"]
    change = current - previous
    change_pct = (change / previous) * 100 if previous else 0
    direction = "↑ 上涨" if change > 0 else ("↓ 下跌" if change < 0 else "— 持平")
    return {
        "current": current,
        "previous": previous,
        "change": change,
        "change_pct": change_pct,
        "direction": direction,
        "timestamp": history[-1]["timestamp"],
        "prev_timestamp": history[-2]["timestamp"],
    }


def compute_moving_averages(history: list[dict]) -> dict:
    """计算 MA5 / MA10（数据不足则返回 None）"""
    rates = [r["rate"] for r in history]
    ma5 = float(np.mean(rates[-5:])) if len(rates) >= 5 else None
    ma10 = float(np.mean(rates[-10:])) if len(rates) >= 10 else None
    return {"ma5": ma5, "ma10": ma10}


def linear_forecast(history: list[dict], days: int = 7) -> dict:
    """
    基于线性回归对未来 days 天做预测。
    返回 {"dates": [...], "rates": [...], "slope": float, "trend": str}
    """
    rates = [r["rate"] for r in history]
    n = len(rates)
    if n < 4:
        return {"dates": [], "rates": [], "slope": 0.0, "trend": "数据不足，暂无预测"}

    x = np.arange(n, dtype=float)
    coeffs = np.polyfit(x, rates, 1)
    slope = float(coeffs[0])
    poly = np.poly1d(coeffs)

    # 生成未来日期（每天一个点）
    last_ts = datetime.strptime(history[-1]["timestamp"], "%Y-%m-%d %H:%M")
    future_x = np.arange(n, n + days, dtype=float)
    future_rates = [float(poly(xi)) for xi in future_x]
    future_dates = [(last_ts + timedelta(days=i + 1)).strftime("%m-%d") for i in range(days)]

    # 趋势判断（基于斜率相对于均值的比例）
    mean_rate = float(np.mean(rates))
    slope_pct = (slope / mean_rate) * 100 if mean_rate else 0
    if slope_pct > 0.01:
        trend = f"人民币对新加坡元呈 **升值** 趋势（每次变动约 +{slope:.6f}）"
    elif slope_pct < -0.01:
        trend = f"人民币对新加坡元呈 **贬值** 趋势（每次变动约 {slope:.6f}）"
    else:
        trend = "人民币对新加坡元汇率基本 **横盘震荡**，短期无明显方向"

    return {
        "dates": future_dates,
        "rates": future_rates,
        "slope": slope,
        "slope_pct": slope_pct,
        "trend": trend,
    }


def generate_analysis_text(change: dict, ma: dict, forecast: dict) -> str:
    """生成人类可读的分析摘要"""
    lines = []

    # 本次变化
    if change["previous"] is not None:
        lines.append(
            f"本次汇率：1 CNY = {change['current']:.6f} SGD（{change['direction']} "
            f"{abs(change['change']):.6f}，{abs(change['change_pct']):.4f}%）"
        )
    else:
        lines.append(f"首次记录：1 CNY = {change['current']:.6f} SGD")

    # 均线
    if ma["ma5"]:
        lines.append(f"MA5（近5次均值）：{ma['ma5']:.6f} SGD")
    if ma["ma10"]:
        lines.append(f"MA10（近10次均值）：{ma['ma10']:.6f} SGD")
        # 判断当前价与均线关系
        if change["current"] > ma["ma10"]:
            lines.append("当前汇率高于 MA10，短期偏强。")
        else:
            lines.append("当前汇率低于 MA10，短期偏弱。")

    # 趋势预测
    lines.append(f"趋势预测：{forecast['trend']}")

    return "\n".join(lines)
