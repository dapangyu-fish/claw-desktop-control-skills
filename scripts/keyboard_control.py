import pyautogui
import argparse
import time
import sys
from typing import List, Literal

# ====================== 配置 ======================
pyautogui.FAILSAFE = True          # 滑鼠移到左上角可緊急停止
pyautogui.PAUSE = 0.08             # 操作間隔，更穩定
pyautogui.KEYBOARD_KEYS = pyautogui.KEYBOARD_KEYS  # 讓 IDE 提示所有合法按鍵

# ====================== 核心函數 ======================
def do_press_key(key: str, presses: int = 1, interval: float = 0.12):
    """單個按鍵或重複按鍵"""
    pyautogui.press(key, presses=presses, interval=interval)
    print(f"✅ 按鍵完成 → '{key}' × {presses}")


def do_hotkey(*keys: str, interval: float = 0.08):
    """同時按下多個按鍵（快捷鍵組合）"""
    pyautogui.hotkey(*keys, interval=interval)
    print(f"✅ 組合鍵完成 → {' + '.join(keys)}")


def do_type_text(text: str, interval: float = 0.04, enter: bool = False):
    """
    輸入一段文字（支援中文、日文、emoji、特殊符號、長文本）
    interval 越小越快，但太小可能在遠端桌面丟字
    """
    if not text:
        print("⚠️  沒有輸入文字，跳過")
        return

    # pyautogui 不會自動切換輸入法，因此假設遠端已處於正確輸入法
    pyautogui.write(text, interval=interval)

    if enter:
        pyautogui.press("enter")
        extra = " + Enter"
    else:
        extra = ""

    # 顯示前後截斷，避免 console 太長
    display_text = (text[:60] + "...") if len(text) > 60 else text
    print(f"✅ 輸入文字完成 → {display_text}{extra} (interval={interval}s)")


def do_type_lines(lines: List[str], line_interval: float = 0.5, char_interval: float = 0.04):
    """逐行輸入（適合貼上多行程式碼、對話等）"""
    for i, line in enumerate(lines, 1):
        do_type_text(line, interval=char_interval, enter=True)
        if i < len(lines):
            time.sleep(line_interval)
    print(f"✅ 已完成 {len(lines)} 行文字輸入")


# ====================== 命令行入口 ======================
def main():
    parser = argparse.ArgumentParser(description="noVNC / 遠端桌面 鍵盤控制工具 - 命令行版")
    subparsers = parser.add_subparsers(dest='action', required=True, help="操作類型")

    # ------------------ 模式1：單鍵 / 重複按鍵 ------------------
    p_press = subparsers.add_parser('press', help='按單個鍵（可重複）')
    p_press.add_argument('key', type=str, help='按鍵名稱，例如: enter, space, a, F5, esc')
    p_press.add_argument('--presses', type=int, default=1, help='重複次數')
    p_press.add_argument('--interval', type=float, default=0.12, help='連續按之間隔')

    # ------------------ 模式2：組合快捷鍵 ------------------
    p_hotkey = subparsers.add_parser('hotkey', help='按組合鍵，例如 Ctrl+Alt+Delete')
    p_hotkey.add_argument('keys', nargs='+', type=str, help='按鍵列表，例如: ctrl alt delete')
    p_hotkey.add_argument('--interval', type=float, default=0.08, help='按鍵間隔')

    # ------------------ 模式3：輸入文字 ------------------
    p_type = subparsers.add_parser('type', help='輸入一段文字（支援中文/日文/emoji等）')
    p_type.add_argument('text', type=str, help='要輸入的文字')
    p_type.add_argument('--interval', type=float, default=0.04, help='每個字元間隔（秒）')
    p_type.add_argument('--enter', action='store_true', help='輸入完按 Enter')

    # ------------------ 進階：多行輸入（適合貼程式碼、對話） ------------------
    p_lines = subparsers.add_parser('lines', help='逐行輸入多行文字（每行自動 Enter）')
    p_lines.add_argument('--file', type=str, help='從檔案讀取多行文字（優先）')
    p_lines.add_argument('--text', type=str, help='直接傳入文字（用\\n分行）')
    p_lines.add_argument('--line-interval', type=float, default=0.6, help='每行之間等待時間')
    p_lines.add_argument('--char-interval', type=float, default=0.04, help='每個字元間隔')

    args = parser.parse_args()

    # 執行對應操作
    if args.action == 'press':
        do_press_key(args.key, args.presses, args.interval)

    elif args.action == 'hotkey':
        do_hotkey(*args.keys, interval=args.interval)

    elif args.action == 'type':
        do_type_text(args.text, interval=args.interval, enter=args.enter)

    elif args.action == 'lines':
        if args.file:
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    lines = [line.rstrip('\n') for line in f]
            except Exception as e:
                print(f"讀取檔案失敗：{e}", file=sys.stderr)
                sys.exit(1)
        elif args.text:
            lines = args.text.split('\\n')
        else:
            print("錯誤：lines 模式必須提供 --file 或 --text", file=sys.stderr)
            sys.exit(1)

        if not lines:
            print("沒有內容可輸入")
            return

        do_type_lines(lines, args.line_interval, args.char_interval)


if __name__ == "__main__":
    main()