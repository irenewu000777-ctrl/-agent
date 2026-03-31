"""
main.py — 主入口，串联所有步骤
"""
import sys
import os

# 确保 src 目录在路径中
sys.path.insert(0, os.path.dirname(__file__))

from fetch_rate import fetch_cny_sgd, load_history, append_record
from analyze import compute_change, compute_moving_averages, linear_forecast, generate_analysis_text
from chart import build_chart
from email_report import run as send_report


def main():
    print("=== CNY/SGD 汇率监测开始 ===")

    # 1. 获取汇率
    print("正在获取汇率...")
    rate = fetch_cny_sgd()
    ts = append_record(rate)
    print(f"[{ts}] 1 CNY = {rate:.6f} SGD")

    # 2. 加载历史数据
    history = load_history()
    print(f"历史记录共 {len(history)} 条")

    # 3. 分析
    change = compute_change(history)
    ma = compute_moving_averages(history)
    forecast = linear_forecast(history, days=7)
    analysis_text = generate_analysis_text(change, ma, forecast)
    print("分析完成：")
    print(analysis_text)

    # 4. 生成图表
    print("正在生成图表...")
    chart_png = build_chart(history, forecast)
    print(f"图表生成完成（{len(chart_png)} bytes）")

    # 5. 发送邮件
    print("正在发送邮件...")
    send_report(change, ma, forecast, analysis_text, chart_png)

    print("=== 完成 ===")


if __name__ == "__main__":
    main()
