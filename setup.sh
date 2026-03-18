#!/bin/bash
mkdir -p ~/.openclaw/workspace/linux-desktop-control/{images,json,md,temp}
if [ -z "$DISPLAY" ]; then
  echo "⚠️  DISPLAY 环境变量缺失！请先设置（例如 export DISPLAY=:0）并重试。"
  exit 1
fi
echo "✅ linux-desktop-control 工作空间已准备就绪"