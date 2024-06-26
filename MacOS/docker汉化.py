import os
import json
import subprocess
import time

# 一些调试用的 mac 终端命令
# sudo pkill docker&rm app.asar&npx asar pack app.asar.unpacked app.asar&sleep 10&&open -a "Docker Desktop"
# sudo pkill "docker"&pkill "Docker"&pkill "Docker"
# sudo cd "/Applications/Docker.app/Contents/MacOS/Docker\ Desktop.app/Contents/Resources/"&rm app.asar&npx asar pack app.asar.unpacked app.asar&sudo pkill "docker"&pkill "Docker"&pkill "Docker"&sleep 5&&open -a "Docker Desktop"
# open -a "Docker Desktop"

# 替换对应表文件路径
REPLACE_TABLE = "docker_replace_table.json"
# 目标文件夹路径
# TARGET_FOLDER = "/Users/king/Desktop/测试目录"
TARGET_FOLDER = "/Applications/Docker.app/Contents/MacOS/Docker Desktop.app/Contents/Resources/app.asar.unpacked"
# 备份文件夹路径
BACKUP_FOLDER = f"{TARGET_FOLDER}_backup"
# 提示命令（在macos13 可能不能完全杀死 docker desktop 进程，macos14 大部分时候可以，不知道原因，脚本里杀死进程的方法并不能完全杀死，还是要用户用终端执行。）
TIPSCOMMAND = '请在终端执行 sudo cd "/Applications/Docker.app/Contents/MacOS/Docker\ Desktop.app/Contents/Resources/"&rm app.asar&npx asar pack app.asar.unpacked app.asar&sudo pkill "docker"&pkill "Docker"&pkill "Docker"&sleep 5&&open -a "Docker Desktop" 观察是否白屏'
# 是否启用调试（0不启用，1启用），调试则每次替换比如50个js文件（"替换1:50"），看有没有问题，没问题再加50个（"替换1:100"），直到找到问题文件范围
# 比如 140—— 145 个中其中一个或多个文件有问题，则 用 DEBUGFILE 控制调试 ，1的话就是每替换一个文件就暂停，2的话，每替换2个文件就暂停让用户测试是否白屏。
# 注意每次都必须结束docker desktop 的全部进程（可以用活动监视器确认），再打开应用测试才有效。
DEBUG = 0
# 调试第几个文件到第几个文件
debug_input = "替换1:50"
# 每次替换几个文件暂停，当大范围测试时这个数字写大就可以了
DEBUGFILE = 1000000

# 处理目录路径中的空格
TARGET_FOLDER2 = TARGET_FOLDER.replace(" ", "\ ")
TARGET_FOLDER2 = TARGET_FOLDER2 + "/"
BACKUP_FOLDER2 = BACKUP_FOLDER.replace(" ", "\ ")

print("开始脚本执行...")
# 检查备份目录是否存在
if not os.path.exists(BACKUP_FOLDER):
    print("备份文件夹不存在。正在创建备份...")
    os.makedirs(BACKUP_FOLDER)
    os.system(f"cp -r {TARGET_FOLDER2} {BACKUP_FOLDER2}")
    print("备份已创建在", BACKUP_FOLDER)
else:
    print("备份文件夹已存在。正在恢复原始文件...")
    os.system(f"rm -rf '{TARGET_FOLDER}'")
    print(f"BACKUP_FOLDER:{BACKUP_FOLDER}")
    print(f"TARGET_FOLDER:{TARGET_FOLDER}")
    os.system(f"cp -r '{BACKUP_FOLDER}' '{TARGET_FOLDER}'")
    if os.path.exists(TARGET_FOLDER):
        backup_subdir = os.path.join(TARGET_FOLDER, "app.asar.unpacked_backup")
        if os.path.exists(backup_subdir):
            os.system(f"rm -rf '{backup_subdir}'")
            print(f"删除了目录: {backup_subdir}")
        else:
            print(f"目录不存在: {backup_subdir}")
    print("已从备份中恢复原始文件.")


# 统计目标目录下所有.js文件并返回文件列表
def count_js_files(directory):
    js_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".js"):
                js_files.append(os.path.join(root, file))
    return js_files


# 定义函数用于替换文件中的内容
def replace_content(file, replace_table):
    with open(replace_table) as f:
        replacements = json.load(f)["replacements"]
        content = open(file).read()
        print(f"处理文件: {file}")
        replaced = 0
        for replacement in replacements:
            original = replacement["original"]
            replacement_text = replacement["replacement"]
            if original in content:
                print(f"正在替换: {original} -> {replacement_text}")
                content = content.replace(original, replacement_text)
                replaced += 1
        with open(file, "w") as f:
            f.write(content)
        print(f"替换完成. 当前文件替换了 {replaced} 处.")
        return replaced


# 搜索包含"docker"的进程并终止
def kill_docker_processes():
    p = subprocess.Popen(["pgrep", "-f", "docker"], stdout=subprocess.PIPE)
    out, _ = p.communicate()
    pids = out.decode().splitlines()
    for pid in pids:
        subprocess.run(["kill", "-9", pid])
    for pid in pids:
        p = subprocess.Popen(["ps", "-p", pid], stdout=subprocess.PIPE)
        out, _ = p.communicate()
        if "docker" in out.decode():
            print(f"进程 {pid} 未成功终止.")


# 启动Docker Desktop
def start_docker_desktop():
    os.system("open -a 'Docker Desktop'")


# 获取所有.js文件列表
all_js_files = count_js_files(TARGET_FOLDER)
total_js_files = len(all_js_files)
print(f"目标目录下共有 {total_js_files} 个 .js 文件.")

# 如果调试模式下指定了范围
if DEBUG == 1:
    if debug_input.startswith("替换"):
        try:
            start, end = map(int, debug_input[2:].split(":"))
            if end > total_js_files:
                end = total_js_files
            debug_js_files = all_js_files[start - 1:end]
        except ValueError:
            print("输入格式错误，退出程序。")
            exit()

processed_files = []
files_replaced_count = 0
files_to_restore = []

if DEBUG == 0:
    debug_js_files = all_js_files

for file_path in debug_js_files:
    try:
        replaced_count = replace_content(file_path, REPLACE_TABLE)
        files_replaced_count += 1
        processed_files.append(file_path)
        print(f"文件 {file_path} 替换完成.")

        # 是否调试
        if DEBUG == 1:
            # 每处理完n个文件后，暂停并确认是否继续
            if files_replaced_count % int(DEBUGFILE) == 0:
                # 打印替换的文件列表
                print("已替换的文件列表:")
                for processed_file in processed_files[-int(DEBUGFILE):]:
                    print(processed_file)
                # 搜索并终止包含"docker"的进程
                kill_docker_processes()
                # 提示命令
                print(f"{TIPSCOMMAND}")
                user_input = input(
                    "已处理n个文件，是否继续？(输入 'y' 回车继续，其他任意键后回车取消): "
                )
                if user_input.lower() != "y":
                    print("处理已取消。恢复替换的文件...")
                    files_to_restore = processed_files[-int(DEBUGFILE):]
                    for file_path in files_to_restore:
                        backup_file_path = file_path.replace(TARGET_FOLDER, BACKUP_FOLDER)
                        backup_file_path_escaped = backup_file_path.replace(" ", "\ ")
                        file_path_escaped = file_path.replace(" ", "\ ")
                        os.system(f'cp -p {backup_file_path_escaped} {file_path_escaped}')
                        # print(f'cp -p {backup_file_path_escaped} {file_path_escaped}')
                    print(f"已恢复刚才替换的 {len(files_to_restore)} 个文件。")
                    exit()
    except Exception as e:
        print(f"替换文件 {file_path} 出错:")
        print(f"错误信息: {e}")
        print("替换内容:")
        for replacement in json.load(open(REPLACE_TABLE))["replacements"]:
            print(f"{replacement['original']} -> {replacement['replacement']}")

print(f"脚本执行完成. 总共替换了 {files_replaced_count} 个文件.")

print("被处理的文件列表:")
for file_path in processed_files:
    print(file_path)

# 获取所有.js文件列表
all_js_files = count_js_files(TARGET_FOLDER)
total_js_files = len(all_js_files)
print(f"目标目录下共有 {total_js_files} 个 .js 文件.")
if DEBUG == 1:
    # 此次调试多少个
    debug_js_files = len(debug_js_files)
    print(f"此次调试替换 {debug_js_files} 个 .js 文件.在 {total_js_files} 中的 {debug_input} 个")
    # 成功替换了多少个
    print(f"脚本执行完成. 总共替换了 {files_replaced_count} 个js文件.")
print(f"{TIPSCOMMAND}")