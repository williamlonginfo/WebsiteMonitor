# 网站监控服务 (UptimeRobot 替代方案)

这是一个基于 Python 和 GitHub Actions 实现的轻量级网站监控服务，可以作为 UptimeRobot 的简单替代品。它会定时（默认每 6 小时）检查您指定的网址列表，并在网站不可达或出现异常时向您发送邮件通知。

## 功能特点
- **免费且自动化**：利用 GitHub Actions 的免费额度执行定时任务。
- **自定义监控列表**：支持配置多个 URL 进行批量监控。
- **阶段模式切换**：
  - **测试阶段 (`TEST_MODE=true`)**：每次执行都会发送报告邮件，无论监控结果成功还是失败，方便验证配置是否正确。
  - **正式阶段 (`TEST_MODE=false`)**：只有在发现网站访问异常（非 200 状态码、超时、无法连接等）时，才会发送警告邮件，避免邮件打扰。
- **详细异常处理**：脚本中包含了对各种网络请求异常（超时、连接失败等）的捕获和中文记录。

## 部署与配置指南

要使此监控服务生效，您需要将代码推送到您自己的 GitHub 仓库，并配置相应的 Secrets 和 Variables。

### 1. 准备您的邮箱
为了发送通知邮件，您需要一个支持 SMTP 的邮箱账号。以 QQ 邮箱或网易邮箱为例，您通常需要去邮箱设置中开启 "SMTP 服务"，并获取一个 **授权码**（不要使用登录密码）。

### 2. 配置 GitHub Repository Secrets (用于敏感信息)
进入您的 GitHub 仓库页面，点击 `Settings` -> 左侧边栏的 `Secrets and variables` -> `Actions` -> `Secrets` 选项卡，点击 `New repository secret` 添加以下变量：

| Secret Name | 示例值 / 说明 |
| :--- | :--- |
| `SMTP_SERVER` | `smtp.qq.com` (QQ邮箱) 或 `smtp.163.com` (网易邮箱) |
| `SMTP_PORT` | `465` (通常 SSL 端口都是 465) |
| `SMTP_USER` | `your_email@qq.com` (您的发件邮箱地址) |
| `SMTP_PASSWORD` | `xxxxx` (您在邮箱设置中获取的 **SMTP 授权码**) |
| `NOTIFY_EMAIL` | `receive_email@gmail.com` (接收报警通知的邮箱地址，可以和发件邮箱相同) |

### 3. 配置 GitHub Repository Variables (用于非敏感配置)
在同一个设置页面下，切换到 `Variables` 选项卡，点击 `New repository variable` 添加以下变量：

| Variable Name | 示例值 / 说明 |
| :--- | :--- |
| `URL_LIST` | `["https://www.google.com", "https://your-website.com"]` <br>**注意：必须是严格的 JSON 数组格式，使用双引号包裹 URL！** |
| `TEST_MODE` | `true` 或 `false`。<br>- 设置为 `true`：每次运行必发邮件。<br>- 设置为 `false` 或不设置：仅失败时发邮件。|

### 4. 运行与测试

配置完成后：
1. 项目中的 `.github/workflows/monitor.yml` 已经配置为每 6 小时自动运行一次。
2. **手动测试**：您可以进入仓库的 `Actions` 页面，点击左侧的 `Website Monitor` 工作流，然后在右侧点击 `Run workflow` 手动触发一次运行。
3. 建议一开始将 `TEST_MODE` Variables 设置为 `true`，手动运行一次，检查您的邮箱是否能成功收到 "全部正常" 的测试报告。确认无误后，将 `TEST_MODE` 修改为 `false` 进入正式监控状态。
