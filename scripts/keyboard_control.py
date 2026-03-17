import pyautogui
import argparse
import time
import sys
import pyperclip
from typing import List
from platform import system as get_platform

# ====================== 配置 ======================
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.08

# ====================== 核心函數 ======================
def do_press_key(key: str, presses: int = 1, interval: float = 0.12):
    """單個按鍵或重複按鍵"""
    pyautogui.press(key, presses=presses, interval=interval)
    print(f"✅ 按鍵完成 → '{key}' × {presses}")


def do_hotkey(*keys: str, interval: float = 0.08):
    """同時按下多個按鍵（快捷鍵組合）"""
    pyautogui.hotkey(*keys, interval=interval)
    print(f"✅ 組合鍵完成 → {' + '.join(keys)}")


def do_type_text(text: str, enter: bool = False):
    """
    【安全貼上模式】使用剪貼簿貼上文字
    完全不受輸入法、Caps Lock、中文/日文/emoji 影響
    你輸什麼，遠端就出現什麼（業界最穩解法）
    """
    if not text:
        print("⚠️ 沒有輸入文字，跳過")
        return

    pyperclip.copy(text)
    time.sleep(0.15)  # 重要緩衝時間

    # 自動判斷作業系統貼上熱鍵
    if get_platform() == "Darwin":  # macOS
        do_hotkey("command", "v")
    else:  # Windows / Linux
        do_hotkey("ctrl", "v")

    if enter:
        time.sleep(0.08)
        pyautogui.press("enter")
        extra = " + Enter"
    else:
        extra = ""

    display_text = (text[:65] + "...") if len(text) > 65 else text
    print(f"✅ [安全貼上] 完成 → {display_text}{extra}")


def do_type_lines(lines: List[str], line_interval: float = 0.5):
    """多行文字一次貼上（最穩、最快）"""
    if not lines:
        print("沒有內容可輸入")
        return

    full_text = "\n".join(lines)
    do_type_text(full_text, enter=False)
    print(f"✅ 已完成 {len(lines)} 行文字貼上（安全模式）")


# ====================== 命令行入口 ======================
def main():
    parser = argparse.ArgumentParser(description="noVNC / 遠端桌面 鍵盤控制工具 - 安全版（輸入法解耦）")
    subparsers = parser.add_subparsers(dest='action', required=True, help="操作類型")

    # 單鍵
    p_press = subparsers.add_parser('press', help='按單個鍵（可重複）')
    p_press.add_argument('key', type=str, help='按鍵名稱，例如: enter, space, a, F5, esc')
    p_press.add_argument('--presses', type=int, default=1)
    p_press.add_argument('--interval', type=float, default=0.12)

    # 組合鍵
    p_hotkey = subparsers.add_parser('hotkey', help='按組合鍵，例如 Ctrl+Alt+Delete')
    p_hotkey.add_argument('keys', nargs='+', type=str, help='例如: ctrl alt delete')
    p_hotkey.add_argument('--interval', type=float, default=0.08)

    # 輸入文字（安全模式）
    p_type = subparsers.add_parser('type', help='輸入一段文字（安全貼上，不受輸入法影響）')
    p_type.add_argument('text', type=str, help='要輸入的文字')
    p_type.add_argument('--enter', action='store_true', help='輸入完按 Enter')

    # 多行輸入（安全模式）
    p_lines = subparsers.add_parser('lines', help='逐行輸入多行文字（安全貼上）')
    p_lines.add_argument('--file', type=str, help='從檔案讀取多行文字（優先）')
    p_lines.add_argument('--text', type=str, help='直接傳入文字（用 \\n 分行）')
    p_lines.add_argument('--line-interval', type=float, default=0.6, help='每行之間等待時間（貼上模式下僅供參考）')

    args = parser.parse_args()

    if args.action == 'press':
        do_press_key(args.key, getattr(args, 'presses', 1), getattr(args, 'interval', 0.12))
    elif args.action == 'hotkey':
        do_hotkey(*args.keys, interval=getattr(args, 'interval', 0.08))
    elif args.action == 'type':
        do_type_text(args.text, enter=args.enter)
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
        do_type_lines(lines, getattr(args, 'line_interval', 0.5))


if __name__ == "__main__":
    main()