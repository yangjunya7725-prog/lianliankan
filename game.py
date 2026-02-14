#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连连看桌面游戏
使用 Pygame 实现，支持 JPEG、PNG、HEIC 格式图片
"""
import math
import os
import random
import sys
import time
from pathlib import Path

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

from PIL import Image
import pygame


# 游戏配置：8×8 网格，每种图片出现 8 次
GRID_ROWS = 8
GRID_COLS = 8
TILE_SIZE = 80
MARGIN = 10
BG_COLOR = (45, 45, 45)
BORDER_COLOR = (85, 85, 85)
SELECT_COLOR = (255, 105, 180)  # 粉色选中边框
VICTORY_MSG = "Happy Valentine's Day, meine kleine Rose!"


def pil_to_surface(pil_image):
    """将 PIL Image 转为 Pygame Surface"""
    mode = pil_image.mode
    size = pil_image.size
    data = pil_image.tobytes()
    loader = getattr(pygame.image, "frombytes", pygame.image.fromstring)
    if mode == "RGBA":
        return loader(data, size, mode).convert_alpha()
    return loader(data, size, mode).convert()


class LianLianKan:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("连连看")

        screen_w = GRID_COLS * TILE_SIZE + MARGIN * 2
        screen_h = GRID_ROWS * TILE_SIZE + MARGIN * 2 + 50
        self.screen = pygame.display.set_mode((screen_w, screen_h))

        self.images_dir = Path(__file__).parent / "images"
        self.tile_surfaces = self._load_images()

        if len(self.tile_surfaces) < 2:
            print("错误：请在 images 文件夹中放置至少 2 张图片")
            print("支持格式: JPEG, PNG, HEIC")
            sys.exit(1)
        self.clock = pygame.time.Clock()

        self.grid = []
        self.selected = None
        self.elimination_line = None
        self.victory = False
        self.victory_start_time = 0
        self.victory_particles = []
        self.victory_burst_count = 0
        self._new_game()

    def _load_images(self):
        """从 images 文件夹加载图片"""
        supported = {".jpg", ".jpeg", ".png", ".heic"}
        images = []
        for f in sorted(self.images_dir.iterdir()):
            if f.suffix.lower() in supported:
                try:
                    img = Image.open(f)
                    if img.mode == "RGBA":
                        bg = Image.new("RGB", img.size, (255, 255, 255))
                        bg.paste(img, mask=img.split()[3])
                        img = bg
                    elif img.mode != "RGB":
                        img = img.convert("RGB")
                    img = img.resize((TILE_SIZE - 4, TILE_SIZE - 4), Image.Resampling.LANCZOS)
                    surface = pil_to_surface(img)
                    images.append(surface)
                except Exception as e:
                    print(f"跳过 {f.name}: {e}")
        return images

    def _new_game(self):
        """开始新游戏"""
        total = GRID_ROWS * GRID_COLS
        pairs = total // 2
        n_types = len(self.tile_surfaces)

        indices = []
        for i in range(pairs):
            indices.append(i % n_types)
            indices.append(i % n_types)
        random.shuffle(indices)

        self.grid = [indices[i : i + GRID_COLS] for i in range(0, total, GRID_COLS)]
        self.selected = None
        self.elimination_line = None
        self.victory = False
        self.victory_particles = []
        self.victory_burst_count = 0

    def _spawn_firework(self, cx, cy):
        """在指定位置生成一束烟花粒子"""
        colors = [(227, 54, 107), (255, 105, 180), (255, 20, 147), (199, 21, 133)]
        for _ in range(25):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            life = random.uniform(0.6, 1.0)
            self.victory_particles.append({
                "x": cx, "y": cy,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": life,
                "color": random.choice(colors),
            })

    def _draw_victory_screen(self):
        """绘制胜利庆祝界面：动态烟花 + 祝福文字"""
        self.screen.fill((232, 232, 232))  # 背景 #E8E8E8

        cx = self.screen.get_width() // 2
        cy = self.screen.get_height() // 2 - 60
        t = time.time() - self.victory_start_time

        # 每隔约 0.4 秒在屏幕不同位置绽放烟花
        expected_bursts = int(t / 0.4) + 1
        while self.victory_burst_count < expected_bursts:
            bx = cx + random.randint(-120, 120)
            by = cy - 80 + random.randint(-40, 40)
            self._spawn_firework(bx, by)
            self.victory_burst_count += 1

        # 更新并绘制烟花粒子
        alive = []
        for p in self.victory_particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.15  # 重力
            p["life"] -= 0.02
            if p["life"] > 0:
                alive.append(p)
                alpha = int(255 * p["life"])
                color = p["color"]
                r = max(1, int(3 * p["life"]))
                s = pygame.Surface((r * 4, r * 4))
                s.set_alpha(alpha)
                pygame.draw.circle(s, color, (r * 2, r * 2), r)
                self.screen.blit(s, (int(p["x"]) - r * 2, int(p["y"]) - r * 2))
        self.victory_particles = alive

        # 祝福文字 颜色 #E3366B
        font_size = 26
        try:
            font = pygame.font.SysFont("arial", font_size, bold=True)
        except Exception:
            font = pygame.font.SysFont(None, 28)
        text_color = (227, 54, 107)  # #E3366B
        text = font.render(VICTORY_MSG, True, text_color)
        text_rect = text.get_rect(center=(cx, cy + 100))
        shadow_color = (180, 40, 70)
        for dx, dy in [(-1,-1),(-1,1),(1,-1),(1,1),(0,-1),(0,1),(-1,0),(1,0)]:
            shadow = font.render(VICTORY_MSG, True, shadow_color)
            self.screen.blit(shadow, (text_rect.x + dx, text_rect.y + dy))
        self.screen.blit(text, text_rect)

        # 点击继续提示
        hint_font = pygame.font.SysFont(None, 20)
        hint = hint_font.render("点击任意位置开始新游戏", True, (150, 80, 100))
        self.screen.blit(hint, (cx - hint.get_width() // 2, cy + 140))

    def _grid_to_pixel(self, row, col):
        """将网格坐标转为像素中心坐标"""
        x = MARGIN + col * TILE_SIZE + TILE_SIZE // 2
        y = MARGIN + row * TILE_SIZE + TILE_SIZE // 2
        return (x, y)

    def _get_connection_path(self, r1, c1, r2, c2):
        """获取两格之间的连接路径（拐点列表），不可连接则返回 None"""
        if r1 == r2 and c1 == c2:
            return None
        if self._path_clear_straight(r1, c1, r2, c2):
            return [(r1, c1), (r2, c2)]
        if self.grid[r1][c2] < 0:
            if self._path_clear_straight(r1, c1, r1, c2) and self._path_clear_straight(r1, c2, r2, c2):
                return [(r1, c1), (r1, c2), (r2, c2)]
        if self.grid[r2][c1] < 0:
            if self._path_clear_straight(r1, c1, r2, c1) and self._path_clear_straight(r2, c1, r2, c2):
                return [(r1, c1), (r2, c1), (r2, c2)]
        for c in range(GRID_COLS):
            if c == c1 or c == c2:
                continue
            if self.grid[r1][c] < 0 and self.grid[r2][c] < 0:
                if (
                    self._path_clear_straight(r1, c1, r1, c)
                    and self._path_clear_straight(r1, c, r2, c)
                    and self._path_clear_straight(r2, c, r2, c2)
                ):
                    return [(r1, c1), (r1, c), (r2, c), (r2, c2)]
        for r in range(GRID_ROWS):
            if r == r1 or r == r2:
                continue
            if self.grid[r][c1] < 0 and self.grid[r][c2] < 0:
                if (
                    self._path_clear_straight(r1, c1, r, c1)
                    and self._path_clear_straight(r, c1, r, c2)
                    and self._path_clear_straight(r, c2, r2, c2)
                ):
                    return [(r1, c1), (r, c1), (r, c2), (r2, c2)]
        return None

    def _draw(self):
        """绘制界面"""
        if self.victory:
            self._draw_victory_screen()
            pygame.display.flip()
            return
        self.screen.fill(BG_COLOR)

        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x = MARGIN + col * TILE_SIZE
                y = MARGIN + row * TILE_SIZE

                idx = self.grid[row][col]
                if idx >= 0:
                    surface = self.tile_surfaces[idx]
                    rect = surface.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
                    self.screen.blit(surface, rect)

                    pygame.draw.rect(self.screen, BORDER_COLOR, (x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4), 1)

                    # 选中时显示粉色外框（消除动画期间不显示选中框）
                    if self.selected == (row, col) and self.elimination_line is None:
                        pygame.draw.rect(self.screen, SELECT_COLOR, (x, y, TILE_SIZE, TILE_SIZE), 4)

        # 绘制消除连线（粉色）
        if self.elimination_line is not None:
            path = self.elimination_line["path"]
            points = [self._grid_to_pixel(r, c) for r, c in path]
            if len(points) >= 2:
                pygame.draw.lines(self.screen, SELECT_COLOR, False, points, 4)

        # 新游戏按钮
        btn_rect = pygame.Rect(GRID_COLS * TILE_SIZE // 2 - 50, GRID_ROWS * TILE_SIZE + MARGIN * 2, 100, 35)
        pygame.draw.rect(self.screen, (70, 70, 70), btn_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), btn_rect, 2)
        font = pygame.font.SysFont(None, 24)
        text = font.render("新游戏", True, (255, 255, 255))
        text_rect = text.get_rect(center=btn_rect.center)
        self.screen.blit(text, text_rect)
        self.new_game_rect = btn_rect

        pygame.display.flip()

    def _get_cell_at(self, pos):
        """获取点击位置对应的格子"""
        x, y = pos
        col = (x - MARGIN) // TILE_SIZE
        row = (y - MARGIN) // TILE_SIZE
        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            return (row, col)
        return None

    def _can_connect(self, r1, c1, r2, c2):
        """检查两个格子能否通过最多3折线连接"""
        if r1 == r2 and c1 == c2:
            return False

        if self._path_clear_straight(r1, c1, r2, c2):
            return True

        if self.grid[r1][c2] < 0:
            if self._path_clear_straight(r1, c1, r1, c2) and self._path_clear_straight(r1, c2, r2, c2):
                return True
        if self.grid[r2][c1] < 0:
            if self._path_clear_straight(r1, c1, r2, c1) and self._path_clear_straight(r2, c1, r2, c2):
                return True

        for c in range(GRID_COLS):
            if c == c1 or c == c2:
                continue
            if self.grid[r1][c] < 0 and self.grid[r2][c] < 0:
                if (
                    self._path_clear_straight(r1, c1, r1, c)
                    and self._path_clear_straight(r1, c, r2, c)
                    and self._path_clear_straight(r2, c, r2, c2)
                ):
                    return True
        for r in range(GRID_ROWS):
            if r == r1 or r == r2:
                continue
            if self.grid[r][c1] < 0 and self.grid[r][c2] < 0:
                if (
                    self._path_clear_straight(r1, c1, r, c1)
                    and self._path_clear_straight(r, c1, r, c2)
                    and self._path_clear_straight(r, c2, r2, c2)
                ):
                    return True
        return False

    def _path_clear_straight(self, r1, c1, r2, c2):
        """检查直线路径是否畅通"""
        if r1 == r2:
            for c in range(min(c1, c2) + 1, max(c1, c2)):
                if self.grid[r1][c] >= 0:
                    return False
        elif c1 == c2:
            for r in range(min(r1, r2) + 1, max(r1, r2)):
                if self.grid[r][c1] >= 0:
                    return False
        else:
            return False
        return True

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.victory:
                        self._new_game()
                        continue
                    pos = event.pos

                    if hasattr(self, "new_game_rect") and self.new_game_rect.collidepoint(pos):
                        self._new_game()
                        continue

                    cell = self._get_cell_at(pos)
                    if cell is None:
                        continue
                    row, col = cell
                    if self.grid[row][col] < 0:
                        continue

                    # 点击选中或取消选中
                    if self.selected is None:
                        self.selected = (row, col)
                    elif self.selected == (row, col):
                        self.selected = None  # 再次点击同一张图，取消选中
                    else:
                        # 两张图都已选中，判断能否消除
                        r1, c1 = self.selected
                        r2, c2 = row, col
                        can_eliminate = (
                            self.grid[r1][c1] == self.grid[r2][c2]  # 图片相同
                            and self._can_connect(r1, c1, r2, c2)   # 拐弯不超过2个且连线不经过其他图片
                        )
                        if can_eliminate:
                            path = self._get_connection_path(r1, c1, r2, c2)
                            if path:
                                self.selected = None
                                self.elimination_line = {
                                    "path": path,
                                    "cells": (r1, c1, r2, c2),
                                    "start_time": time.time(),
                                }
                        else:
                            # 不能消除，两张图都取消选中
                            self.selected = None

            # 消除动画：连线显示 100ms 后移除图片
            if self.elimination_line is not None:
                elapsed = (time.time() - self.elimination_line["start_time"]) * 1000
                if elapsed >= 100:
                    r1, c1, r2, c2 = self.elimination_line["cells"]
                    self.grid[r1][c1] = -1
                    self.grid[r2][c2] = -1
                    self.elimination_line = None

                    if all(self.grid[r][c] < 0 for r in range(GRID_ROWS) for c in range(GRID_COLS)):
                        self.victory = True
                        self.victory_start_time = time.time()

            self._draw()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    app = LianLianKan()
    app.run()
