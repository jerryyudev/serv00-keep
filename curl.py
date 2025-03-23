import subprocess
import asyncio
import datetime
import re
from telegram import Bot

# 直接在代码中设置 Telegram Bot Token 和 Chat ID
BOT_TOKEN = "8048960186:AAGFWPK3PqQmYNs475kjn8iUUZeA8_l_Tg4"  # Telegram Bot Token
CHAT_ID = "-1002152112193"  # Telegram Chat ID
bot = Bot(token=BOT_TOKEN)

def extract_username(command):
    """
    从 curl 命令中提取 username 参数的值，
    匹配 username= 后面到 & 或 ^ 的内容
    """
    match = re.search(r"username=([^&\^]+)", command)
    if match:
        return match.group(0)  # 返回 "username=xxx"
    else:
        return "未找到 username"

async def execute_curl_commands(file_path):
    """
    读取文件中所有的 curl 请求（以空行分隔），并依次执行
    """
    results = {}  # 存储 {完整命令: 状态码} 的字典
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    current_command = ""
    for line in lines:
        stripped_line = line.strip()
        # 遇到空行时认为是一条命令结束
        if not stripped_line:
            if current_command:
                results[current_command] = run_command(current_command)
                current_command = ""
            continue
        # 如果行以 curl 开头，视为新命令开始；之前的命令若存在则保存
        if stripped_line.startswith("curl"):
            if current_command:
                results[current_command] = run_command(current_command)
            current_command = stripped_line
        else:
            current_command += " " + stripped_line  # 拼接多行命令

    # 处理最后一条命令（文件末尾可能没有空行）
    if current_command:
        results[current_command] = run_command(current_command)

    return results

def run_command(command):
    """
    为传入的 curl 命令添加 -w 参数（用于输出 HTTP 状态码），
    并返回状态码（例如 "302"）
    """
    try:
        # 添加 -w 参数以输出 HTTP 状态码
        command_with_status = command.replace("curl", 'curl -w "%{http_code}"', 1)
        result = subprocess.run(command_with_status, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode().strip()
        # 提取输出最后3个字符作为状态码
        status_code = output[-3:] if output[-3:].isdigit() else "Unknown"
        return status_code
    except Exception as e:
        return f"Error: {e}"

async def send_to_telegram(message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

async def main():
    file_path = "account.txt"  # 假设你的 curl 请求文件名为 account.txt
    results = await execute_curl_commands(file_path)
    
    # 汇总所有命令的信息，提取 username 参数和对应状态码
    summary_lines = ["Curl 命令汇总摘要:"]
    for command, status in results.items():
        username_info = extract_username(command)
        summary_lines.append(f"{username_info} - Result: {status}")
    
    # 添加当前时间和时区信息
    now = datetime.datetime.now().astimezone()
    time_str = now.strftime("%Y-%m-%d %H:%M:%S %Z")
    summary_lines.append(f"\n执行时间：{time_str}")
    
    final_message = "\n".join(summary_lines)
    
    # 发送整条消息到 Telegram
    await send_to_telegram(final_message)
    
    # 同时在控制台输出日志
    print(final_message)

if __name__ == "__main__":
    asyncio.run(main())
