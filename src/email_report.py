"""
email_report.py — 通过 Gmail SMTP 发送 HTML 汇率报告（内嵌图表）
"""
import base64
import os
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def build_html(change: dict, ma: dict, forecast: dict, analysis_text: str) -> str:
    direction_color = "#3fb950" if change.get("change", 0) > 0 else (
        "#f85149" if change.get("change", 0) < 0 else "#8b949e"
    )
    prev_info = ""
    if change.get("previous") is not None:
        prev_info = f"""
        <tr>
          <td>上次汇率</td>
          <td>{change['previous']:.6f} SGD <span style="color:#8b949e;font-size:12px">
              @ {change.get('prev_timestamp','')}</span></td>
        </tr>
        <tr>
          <td>变动幅度</td>
          <td style="color:{direction_color};font-weight:bold;">
            {change['direction']} {abs(change['change']):.6f}
            （{abs(change['change_pct']):.4f}%）
          </td>
        </tr>"""

    ma5_row = f"<tr><td>MA5 均值</td><td>{ma['ma5']:.6f} SGD</td></tr>" if ma.get("ma5") else ""
    ma10_row = f"<tr><td>MA10 均值</td><td>{ma['ma10']:.6f} SGD</td></tr>" if ma.get("ma10") else ""

    forecast_trend = forecast.get("trend", "数据不足")

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background:#0d1117; color:#c9d1d9; margin:0; padding:20px; }}
  .card {{ background:#161b22; border:1px solid #30363d; border-radius:8px;
           padding:20px; max-width:680px; margin:0 auto; }}
  h2 {{ color:#58a6ff; margin-top:0; }}
  table {{ width:100%; border-collapse:collapse; margin:16px 0; }}
  td {{ padding:8px 12px; border-bottom:1px solid #21262d; font-size:14px; }}
  td:first-child {{ color:#8b949e; width:130px; }}
  .rate {{ font-size:28px; font-weight:bold; color:#e6edf3; }}
  .forecast {{ background:#21262d; border-radius:6px; padding:12px;
               font-size:13px; line-height:1.8; color:#c9d1d9; margin-top:12px; }}
  .footer {{ color:#484f58; font-size:11px; margin-top:16px; text-align:center; }}
</style>
</head>
<body>
<div class="card">
  <h2>🔄 CNY/SGD 汇率监测报告</h2>
  <div class="rate">1 CNY = {change['current']:.6f} SGD</div>
  <table>
    <tr><td>查验时间</td><td>{change.get('timestamp','')}</td></tr>
    {prev_info}
    {ma5_row}
    {ma10_row}
  </table>
  <div class="forecast">
    <strong>📊 趋势分析 &amp; 预测</strong><br><br>
    {forecast_trend}<br><br>
    <pre style="margin:0;font-size:12px;white-space:pre-wrap;">{analysis_text}</pre>
  </div>
  <br>
  <img src="cid:rate_chart" style="width:100%;border-radius:6px;" alt="汇率走势图">
  <div class="footer">
    数据来源：Frankfurter.app · 由 GitHub Actions 自动发送
  </div>
</div>
</body>
</html>"""


def send_email(
    sender: str,
    app_password: str,
    receiver: str,
    subject: str,
    html_body: str,
    chart_png: bytes,
) -> None:
    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    alt = MIMEMultipart("alternative")
    msg.attach(alt)
    alt.attach(MIMEText(html_body, "html", "utf-8"))

    img = MIMEImage(chart_png, "png")
    img.add_header("Content-ID", "<rate_chart>")
    img.add_header("Content-Disposition", "inline", filename="rate_chart.png")
    msg.attach(img)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, app_password)
        smtp.sendmail(sender, receiver, msg.as_string())


def run(change: dict, ma: dict, forecast: dict, analysis_text: str, chart_png: bytes) -> None:
    sender = os.environ["EMAIL_SENDER"]
    app_password = os.environ["EMAIL_APP_PASSWORD"]
    receiver = os.environ["EMAIL_RECEIVER"]

    current = change.get("current", 0)
    direction = change.get("direction", "—")
    subject = f"[汇率监测] 1 CNY = {current:.6f} SGD  {direction}"

    html = build_html(change, ma, forecast, analysis_text)
    send_email(sender, app_password, receiver, subject, html, chart_png)
    print(f"邮件已发送至 {receiver}")
