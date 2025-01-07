import subprocess

def execute_curl_commands(file_path):
    results = {}
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    current_command = ""
    for line in lines:
        line = line.strip()
        if line.startswith("curl"):
            if current_command:
                # 执行上一条完整的 curl 命令
                results[current_command] = run_command(current_command)
            current_command = line
        elif current_command:
            current_command += f" {line}"  # 拼接命令

    # 执行最后一条命令
    if current_command:
        results[current_command] = run_command(current_command)

    return results

def run_command(command):
    try:
        # 添加 -w 参数来输出 HTTP 状态码
        command_with_status = command.replace("curl", 'curl -w "%{http_code}"')
        result = subprocess.run(command_with_status, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode().strip()
        # 提取最后的 HTTP 状态码
        return output[-3:] if output[-3:].isdigit() else "Unknown"
    except Exception as e:
        return f"Error: {e}"

def main():
    file_path = r"C:\Users\tkinkpad\Desktop\file\account.txt"  # 文件路径
    results = execute_curl_commands(file_path)
    for cmd, status in results.items():
        print(f"{cmd.split()[1]}: {status}")  # 打印 URL 和 HTTP 状态码
    end = input('Press Enter to exit the program')
if __name__ == "__main__":
    main()
