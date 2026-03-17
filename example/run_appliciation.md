---
name: "运行应用程序"
description: "通过claw-desktop-control-skills运行应用程序"
---

## 示例 1：打开浏览器

- 截图并利用 `ui_detect_prompt.sh` 分析当前环境，发现是在桌面首页
- 发现左上角有Appliciations图标
- 利用 `mouse_control.py`点击Appliciations图标
- 等待浏览器打开
- 截图并通 `ui_detect_prompt.sh` 确认浏览器已经打开


## 示例 2：打开浏览器

- 截图并利用 `ui_detect_prompt.sh` 分析当前环境，发现已经身处浏览器窗口
- 直接告诉用户目前就在浏览器中

## 示例 2：打开终端

- 截图并利用 `ui_detect_prompt.sh` 分析当前环境，发现已经身处浏览器窗口
- 直接告诉用户目前就在浏览器中