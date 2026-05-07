import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量（如果存在）
load_dotenv()

# ==========================================
# 配置部分 (从环境变量获取)
# ==========================================
# 邮件服务器配置 (以 SMTP 为例)
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.example.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465")) # 通常使用 SSL 端口 465
SMTP_USER = os.environ.get("SMTP_USER", "your_email@example.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "your_email_password")
# 接收通知的邮箱
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "notify@example.com")

# 需要监控的 URL 列表，从环境变量读取，格式为 JSON 字符串，例如：'["https://example.com", "https://api.example.com"]'
try:
    URL_LIST = json.loads(os.environ.get("URL_LIST", "[]"))
except json.JSONDecodeError:
    URL_LIST = []
    print("错误：URL_LIST 环境变量格式不正确，应为 JSON 数组字符串。")

# 运行模式：'true' 为测试阶段，'false' 为正式阶段
TEST_MODE = os.environ.get("TEST_MODE", "false").lower() == "true"


def send_email(subject, body):
    """
    发送邮件的工具函数
    """
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = NOTIFY_EMAIL
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        # 使用 SMTP_SSL，如果您的邮件服务器不支持 SSL，可能需要改用 smtplib.SMTP
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"成功发送邮件到 {NOTIFY_EMAIL}，主题：{subject}")
    except Exception as e:
        print(f"发送邮件失败: {e}")

def check_url(url):
    """
    检查单个 URL 的状态
    返回: (布尔值是否成功, 详细信息字符串)
    """
    try:
        # 设置超时时间为 10 秒
        response = requests.get(url, timeout=10)
        
        # 检查状态码是否为 200 OK
        if response.status_code == 200:
            return True, f"[{url}] 访问成功 (状态码: {response.status_code})"
        else:
            return False, f"[{url}] 访问异常 (状态码: {response.status_code})"
            
    except requests.exceptions.Timeout:
        return False, f"[{url}] 访问超时 (超过 10 秒)"
    except requests.exceptions.ConnectionError:
        return False, f"[{url}] 连接错误 (无法连接到服务器)"
    except requests.exceptions.RequestException as e:
        return False, f"[{url}] 发生请求异常: {e}"

def main():
    if not URL_LIST:
        print("未配置 URL_LIST，没有需要监控的网站。")
        return

    print(f"--- 监控任务开始运行于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    print(f"当前模式: {'测试阶段' if TEST_MODE else '正式阶段'}")
    
    results = []
    has_failure = False

    # 遍历列表检查每个 URL
    for url in URL_LIST:
        print(f"正在检查: {url}")
        success, message = check_url(url)
        results.append(message)
        print(message)
        
        if not success:
            has_failure = True

    # 汇总报告
    report_body = "\n".join(results)
    report_body += f"\n\n检查完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # 判断是否需要发送邮件
    should_send_email = False
    subject = ""

    if TEST_MODE:
        # 测试阶段：无论成功失败都发送
        should_send_email = True
        status_text = "发现异常" if has_failure else "全部正常"
        subject = f"[监控-测试阶段] 网站监控报告 - {status_text}"
    else:
        # 正式阶段：仅在有失败时发送
        if has_failure:
            should_send_email = True
            subject = "[警告] 网站监控发现异常！"
        else:
             print("正式阶段：所有网站访问正常，无需发送邮件。")

    # 发送邮件
    if should_send_email:
        print("准备发送报告邮件...")
        send_email(subject, report_body)

    print("--- 监控任务执行完毕 ---")

if __name__ == "__main__":
    main()
