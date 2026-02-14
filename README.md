# 连连看桌面游戏

基于 Python + Pygame 的经典连连看桌面游戏，使用 `images` 文件夹中的图片作为游戏元素。

## 运行方式

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 运行游戏：
   ```bash
   python game.py
   ```

## 游戏规则

- 点击两张**相同**的图片，若能在**最多 3 条直线**内连通（不能斜连），即可消除
- 消除所有图片即获胜
- 点击「新游戏」重新开始

## 图片格式

- 支持 **JPEG**、**PNG**、**HEIC** 格式
- 将图片放入 `images` 文件夹即可，游戏会自动加载
你的仓库根目录/
├── index.html      ← web/index.html
└── images/         ← web/images/ 整个文件夹（含 8 张 PNG）
    ├── 008CDAAD-6C3C-4EAE-8046-62A322C3D3C3.png
    └── ... (其他 7 张 PNG 图片)
