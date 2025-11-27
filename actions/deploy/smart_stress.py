import os


def run(context, **kwargs):
    """
    智能压测 V6：全指令集 + 蓝牙/WiFi + 【应用保活/防误触】
    """
    task_list = kwargs.get("tasks", [])
    duration = kwargs.get("duration", 3600)
    target_pkg = kwargs.get("package_name")
    # 启动页面 (用于挂掉后自动拉起)
    start_uri = kwargs.get("start_uri", f"{target_pkg}/.MainActivity")

    if not target_pkg:
        return {"status": False, "msg": "❌ 必须提供 package_name"}

    logger = context.logger
    adb = context.adb

    shell_content = f"""#!/system/bin/sh
LOG_DIR="/sdcard/dognoise_stress"
mkdir -p $LOG_DIR
EVENT_LOG="$LOG_DIR/event.log"
CRASH_LOG="$LOG_DIR/crash_stack.log"

echo "=== [$(date)] 压测开始: {target_pkg} ===" > $EVENT_LOG

# 启动日志抓取...
logcat -c
nohup logcat -v time *:E -f $CRASH_LOG -r 10240 -n 5 & 
LOGCAT_PID=$!

start_time=$(date +%s)
loop_count=0

# --- 【新增】保活函数：确保 App 在前台 ---
function ensure_app_foreground() {{
    # 1. 检查当前前台窗口是谁
    # dumpsys window | grep mCurrentFocus 通常会输出 "u0 com.package.name/..."
    current_focus=$(dumpsys window | grep mCurrentFocus)

    # 2. 如果前台不是我们的目标 App
    # grep -q -v 表示“如果不包含”
    if ! echo "$current_focus" | grep -q "{target_pkg}"; then
        echo "[🚨 RECOVER] $(date) 发现应用不在前台！(当前: $current_focus)" >> $EVENT_LOG

        # 3. 尝试救活：强行拉起
        echo "[🚑 RECOVER] 正在重新拉起: {start_uri} ..." >> $EVENT_LOG
        am start -n {start_uri}

        # 4. 【关键】强制等待加载，防止还没起这就乱点
        # 这里硬等待 10 秒，保证 App 缓过气来
        sleep 10

        # 5. 再次检查，如果还没起来，可能死机了
        current_focus_2=$(dumpsys window | grep mCurrentFocus)
        if ! echo "$current_focus_2" | grep -q "{target_pkg}"; then
             echo "[☠️ FATAL] 拉起失败，可能设备已死机或应用彻底损坏" >> $EVENT_LOG
        else
             echo "[✅ RECOVER] 拉起成功，继续测试" >> $EVENT_LOG
        fi
    fi
}}

# ... (check_wifi / run_wifi_cycle / run_bt_toggle 函数保持 V5 不变) ...
# 为了节省篇幅，这里假设之前的 wifi/bt 函数还在

# --- 主循环 ---
while [ $(($(date +%s) - start_time)) -lt {duration} ]; do

    # ... (死亡监控逻辑保持不变) ...

    # --- 翻译逻辑 ---
"""

    for task in task_list:
        action = task.get('action')
        indent = "    "

        # 【关键修改】在执行 UI 操作前，先检查应用是否活着！
        # 只有 CLICK, SWIPE, KEY, TEXT 这种操作怕点错，所以加检查
        # SHELL, WIFI 等操作不需要检查
        needs_guard = action in ["CLICK", "SWIPE", "KEY", "TEXT"]

        if needs_guard:
            shell_content += f'{indent}ensure_app_foreground\n'

        # ... (动作翻译逻辑保持 V5 不变) ...
        if action == "CLICK":
            shell_content += f'{indent}input tap {task.get("x")} {task.get("y")}\n'
        # ... (其他 case 如 KEY, SWIPE, WAIT 等) ...
        # 请确保把 v5 里的翻译代码拷过来

    # --- 尾部收尾 ---
    shell_content += """
    loop_count=$((loop_count + 1))
    sleep 1
done
# ... (收尾代码同前) ...
"""

    # ... (下发逻辑同前) ...
    try:
        local_path = os.path.join(context.root_dir, "outputs", "stress_runner_v6.sh")
        with open(local_path, "w", encoding="utf-8", newline='\\n') as f:
            f.write(shell_content)
        # ... Push & Run ...
        return {"status": True, "msg": "V6 脚本(带自愈能力)已部署"}
    except Exception as e:
        return {"status": False, "msg": str(e)}