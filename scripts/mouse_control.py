import pyautogui
import argparse
import time
import sys
from typing import Literal

# ====================== 配置 ======================
pyautogui.FAILSAFE = True      # 滑鼠移到左上角可緊急停止
pyautogui.PAUSE = 0.08         # 操作間隔，更穩定

# ====================== 核心函數 ======================
def do_click(x: int, y: int, button: Literal['left','right','middle'] = 'left', clicks: int = 1, duration: float = 0.3):
    pyautogui.moveTo(x, y, duration=duration)
    pyautogui.click(clicks=clicks, button=button)
    print(f"✅ 單擊完成 → ({x}, {y}) | {button}鍵 | 次數: {clicks}")

def do_double(x: int, y: int, duration: float = 0.3):
    pyautogui.moveTo(x, y, duration=duration)
    pyautogui.doubleClick()
    print(f"✅ 雙擊完成 → ({x}, {y})")

def do_drag(x1: int, y1: int, x2: int, y2: int, duration: float = 1.0):
    pyautogui.moveTo(x1, y1, duration=0.3)
    pyautogui.mouseDown(button='left')
    pyautogui.moveTo(x2, y2, duration=duration)
    pyautogui.mouseUp(button='left')
    print(f"✅ 拖拽完成 → ({x1},{y1}) → ({x2},{y2}) | 耗時 {duration}s")

def do_right(x: int, y: int, duration: float = 0.3):
    do_click(x, y, button='right', clicks=1, duration=duration)

def do_scroll(x: int, y: int, amount: int = 100, duration: float = 0.3):
    pyautogui.moveTo(x, y, duration=duration)
    pyautogui.scroll(amount)
    print(f"✅ 滾輪完成 → 滾動 {amount} 單位")

# ====================== 命令行入口 ======================
def main():
    parser = argparse.ArgumentParser(description="noVNC 鼠標控制工具 - 命令行版")
    subparsers = parser.add_subparsers(dest='action', required=True, help="操作類型")

    # 單擊
    p_click = subparsers.add_parser('click', help='單擊')
    p_click.add_argument('x', type=int, help='X 座標')
    p_click.add_argument('y', type=int, help='Y 座標')
    p_click.add_argument('--button', choices=['left','right','middle'], default='left', help='按鍵')
    p_click.add_argument('--clicks', type=int, default=1, help='點擊次數')
    p_click.add_argument('--duration', type=float, default=0.3, help='移動時間')

    # 雙擊
    p_double = subparsers.add_parser('double', help='雙擊')
    p_double.add_argument('x', type=int)
    p_double.add_argument('y', type=int)
    p_double.add_argument('--duration', type=float, default=0.3)

    # 拖拽
    p_drag = subparsers.add_parser('drag', help='拖拽')
    p_drag.add_argument('x1', type=int)
    p_drag.add_argument('y1', type=int)
    p_drag.add_argument('x2', type=int)
    p_drag.add_argument('y2', type=int)
    p_drag.add_argument('--duration', type=float, default=1.0)

    # 右鍵
    p_right = subparsers.add_parser('right', help='右鍵單擊')
    p_right.add_argument('x', type=int)
    p_right.add_argument('y', type=int)
    p_right.add_argument('--duration', type=float, default=0.3)

    # 滾輪
    p_scroll = subparsers.add_parser('scroll', help='滾輪')
    p_scroll.add_argument('x', type=int)
    p_scroll.add_argument('y', type=int)
    p_scroll.add_argument('amount', type=int, help='滾動量 (正=上, 負=下)')
    p_scroll.add_argument('--duration', type=float, default=0.3)

    args = parser.parse_args()

    # 執行對應操作
    if args.action == 'click':
        do_click(args.x, args.y, args.button, args.clicks, args.duration)
    elif args.action == 'double':
        do_double(args.x, args.y, args.duration)
    elif args.action == 'drag':
        do_drag(args.x1, args.y1, args.x2, args.y2, args.duration)
    elif args.action == 'right':
        do_right(args.x, args.y, args.duration)
    elif args.action == 'scroll':
        do_scroll(args.x, args.y, args.amount, args.duration)

if __name__ == "__main__":
    main()