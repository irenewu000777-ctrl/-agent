# CNY/SGD 汇率监测工作流

全自动、零成本的人民币兑新加坡元汇率监测系统。每日 4 次自动查验汇率，生成走势图表并发送邮件报告，完全运行在 GitHub Actions 上。

## 功能

- 每日 08:00 / 12:00 / 16:00 / 20:00（北京时间）自动获取汇率
- 显示与上次相比的涨跌幅度及方向
- 技术指标分析（MA5、MA10、线性回归趋势预测）
- 生成折线图（实际走势 + 7 日预测 + 变化率柱状图）
- 通过 Gmail 发送 HTML 邮件报告（内嵌图表）
- 历史数据自动持久化到仓库（`data/history.csv`）

## 费用

**$0/月** — 数据来源、图表生成、定时运行、邮件发送均完全免费。

## 快速开始

### 1. Fork 本仓库

点击页面右上角 **Fork** 按钮，将仓库复制到你的 GitHub 账号。

### 2. 获取 Gmail 应用专用密码

1. 登录 Google 账号 → [myaccount.google.com](https://myaccount.google.com)
2. 安全 → 两步验证（需先开启）
3. 应用专用密码 → 生成一个新密码（选择"邮件"+"Windows 计算机"）
4. 复制生成的 16 位密码

### 3. 配置 GitHub Secrets

在你 Fork 的仓库页面：**Settings → Secrets and variables → Actions → New repository secret**

| Secret 名称 | 值 |
|-------------|-----|
| `EMAIL_SENDER` | 你的 Gmail 地址（如 `yourname@gmail.com`） |
| `EMAIL_APP_PASSWORD` | 上一步获取的 16 位应用专用密码 |
| `EMAIL_RECEIVER` | 收件人邮箱（可以和发件人相同） |

### 4. 启用 GitHub Actions

进入仓库的 **Actions** 标签页，点击 **"I understand my workflows, go ahead and enable them"**。

### 5. 手动测试

在 Actions 页面选择 **CNY/SGD Rate Monitor** → **Run workflow** → **Run workflow**，观察运行结果并检查邮件。

## 项目结构

```
├── .github/workflows/monitor.yml  # GitHub Actions 定时任务
├── src/
│   ├── main.py           # 主入口
│   ├── fetch_rate.py     # 获取汇率（frankfurter.app）
│   ├── analyze.py        # 技术分析 + 趋势预测
│   ├── chart.py          # 生成图表（matplotlib）
│   └── email_report.py   # 发送邮件（Gmail SMTP）
├── data/
│   └── history.csv       # 历史汇率记录（自动更新）
└── requirements.txt
```

## 本地运行（调试）

```bash
pip install -r requirements.txt

export EMAIL_SENDER="yourname@gmail.com"
export EMAIL_APP_PASSWORD="your-app-password"
export EMAIL_RECEIVER="receiver@example.com"

python src/main.py
```

Windows（PowerShell）：

```powershell
$env:EMAIL_SENDER="yourname@gmail.com"
$env:EMAIL_APP_PASSWORD="your-app-password"
$env:EMAIL_RECEIVER="receiver@example.com"

python src/main.py
```

## 数据来源

汇率数据来自 [Frankfurter.app](https://www.frankfurter.app)，该服务基于欧洲中央银行数据，完全免费，无需注册。

## License

MIT
