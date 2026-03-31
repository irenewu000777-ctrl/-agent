"""
chart.py — 生成汇率走势图（实际走势 + 线性预测 + 变化率柱状图）
返回 PNG 图片的 bytes
"""
import io
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

matplotlib.use("Agg")  # 非交互模式，适合服务器/Actions
matplotlib.rcParams["font.family"] = ["DejaVu Sans", "Arial Unicode MS", "sans-serif"]


def build_chart(history: list[dict], forecast: dict) -> bytes:
    """
    生成双子图：
    上图 — 实际汇率折线（蓝）+ MA5（橙虚）+ MA10（绿虚）+ 预测（红虚）
    下图 — 每次变化率柱状图（绿涨/红跌）
    返回 PNG bytes
    """
    rates = [r["rate"] for r in history]
    timestamps = [r["timestamp"] for r in history]

    # 转换为 datetime 对象
    dates = []
    for ts in timestamps:
        try:
            dates.append(datetime.strptime(ts, "%Y-%m-%d %H:%M"))
        except ValueError:
            dates.append(datetime.strptime(ts, "%Y-%m-%d"))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8),
                                    gridspec_kw={"height_ratios": [3, 1]})
    fig.patch.set_facecolor("#0d1117")
    for ax in (ax1, ax2):
        ax.set_facecolor("#161b22")
        ax.tick_params(colors="#c9d1d9")
        ax.xaxis.label.set_color("#c9d1d9")
        ax.yaxis.label.set_color("#c9d1d9")
        for spine in ax.spines.values():
            spine.set_edgecolor("#30363d")

    # ---- 上图：汇率走势 ----
    ax1.plot(dates, rates, color="#58a6ff", linewidth=2, marker="o",
             markersize=4, label="CNY/SGD", zorder=5)

    # MA5
    if len(rates) >= 5:
        ma5 = [float(np.mean(rates[max(0, i-4):i+1])) for i in range(len(rates))]
        ax1.plot(dates, ma5, color="#f0883e", linewidth=1.2,
                 linestyle="--", label="MA5", alpha=0.85)

    # MA10
    if len(rates) >= 10:
        ma10 = [float(np.mean(rates[max(0, i-9):i+1])) for i in range(len(rates))]
        ax1.plot(dates, ma10, color="#3fb950", linewidth=1.2,
                 linestyle="--", label="MA10", alpha=0.85)

    # 预测走势（红虚线）
    if forecast and forecast["dates"]:
        from datetime import timedelta
        last_date = dates[-1]
        pred_dates = [last_date + timedelta(days=i+1) for i in range(len(forecast["dates"]))]
        pred_rates = forecast["rates"]
        # 从最后一个实际点连线到预测
        conn_dates = [dates[-1]] + pred_dates
        conn_rates = [rates[-1]] + pred_rates
        ax1.plot(conn_dates, conn_rates, color="#f85149", linewidth=1.5,
                 linestyle="--", marker="x", markersize=4,
                 label="7-day Forecast", alpha=0.9)
        ax1.axvline(x=dates[-1], color="#30363d", linewidth=1, linestyle=":")

    ax1.set_title("CNY / SGD Exchange Rate", color="#e6edf3",
                  fontsize=14, fontweight="bold", pad=12)
    ax1.set_ylabel("Rate (1 CNY = ? SGD)", color="#c9d1d9")
    ax1.legend(loc="upper left", facecolor="#21262d",
               labelcolor="#c9d1d9", edgecolor="#30363d", fontsize=9)
    ax1.grid(color="#21262d", linewidth=0.6)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=8)

    # ---- 下图：变化率柱状图 ----
    if len(rates) >= 2:
        changes = [((rates[i] - rates[i-1]) / rates[i-1]) * 100 for i in range(1, len(rates))]
        bar_dates = dates[1:]
        colors = ["#3fb950" if c >= 0 else "#f85149" for c in changes]
        ax2.bar(bar_dates, changes, color=colors, width=0.03, alpha=0.85)
        ax2.axhline(0, color="#30363d", linewidth=0.8)
        ax2.set_ylabel("Change %", color="#c9d1d9", fontsize=9)
        ax2.grid(color="#21262d", linewidth=0.4, axis="y")
        ax2.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=7)

    plt.tight_layout(pad=2.0)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()
