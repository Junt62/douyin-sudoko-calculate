from collections import defaultdict
import time
import AppKit
from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly,
    kCGNullWindowID,
    CGDisplayBounds,
    CGMainDisplayID,
    CGGetActiveDisplayList,
    CGGetOnlineDisplayList,
    CGDisplayBounds,
)
from AppKit import NSScreen
import ctypes

import re
from typing import List, Optional, Dict
import Quartz
import glfw
import OpenGL.GL as gl
import imgui
from imgui.integrations.glfw import GlfwRenderer

# PyObjC for Cocoa access
import objc
from Cocoa import NSApp, NSApplication, NSWindow
from Quartz import kCGColorClear

import Quartz
import AppKit
import numpy as np
from PIL import Image
import cv2
import pytesseract
import os
from typing import Tuple, Dict

import globals
import ocr
import util
import window
import solve


class ui:
    globals = None
    window = None
    ocr = None
    solve = None

    def __init__(self):
        self.globals = globals.Globals()
        self.window = window.Window()
        self.ocr = ocr.Ocr()
        self.solve = solve.Solve()

    def approx_equal(self, a, b, eps=1) -> int:
        return abs(a - b) <= eps

    def make_window_click_through(self, window):
        # 获取 macOS 原生 NSWindow 指针
        # glfw 的 cocoa 接口：glfw.get_cocoa_window(window) -> NSWindow*
        # Python glfw 没有直接暴露，需要通过 ctypes 或 PyObjC 辅助。
        # 简便做法：通过当前 App NSApp.windows[-1] 获取最近创建的窗口。
        app = NSApp()
        if app is None:
            app = NSApplication.sharedApplication()
        ns_windows = app.windows()
        if not ns_windows:
            return
        ns_window = ns_windows[-1]
        # 忽略鼠标事件（点击穿透）
        ns_window.setIgnoresMouseEvents_(True)
        # 允许透过窗口看到后面内容（已由透明帧缓冲提供），可确保没有背景视图绘制不透明内容
        ns_window.setOpaque_(False)
        # 可选：去除阴影
        ns_window.setHasShadow_(False)
        # 可选：禁用在 Exposé/Spaces 中作为普通窗口显示
        # ns_window.setCollectionBehavior_(256)  # NSWindowCollectionBehaviorCanJoinAllSpaces

    def imdraw_grid(self, ww, wh, dl, nonograms_result):
        if self.globals.APP_FILL_ALPHA > 0.0:
            dl.add_rect_filled(
                0,
                0,
                ww,
                wh,
                imgui.get_color_u32_rgba(
                    *self.globals.APP_FILL_COLOR, self.globals.APP_FILL_ALPHA
                ),
                0.0,
            )
            dl.add_rect(
                0,
                0,
                ww,
                wh,
                imgui.get_color_u32_rgba(
                    *self.globals.APP_BORDER_COLOR,
                    self.globals.APP_BORDER_ALPHA,
                ),
                0.0,
                0,
                thickness=self.globals.APP_BORDER_THICKNESS,
            )
        # 绘制棋盘范围
        if self.globals.CHESS_FILL_ALPHA > 0:
            dl.add_rect_filled(
                self.globals.chess_grid_pos["X"],
                self.globals.chess_grid_pos["Y"],
                self.globals.chess_grid_pos["W"],
                self.globals.chess_grid_pos["H"],
                imgui.get_color_u32_rgba(
                    *self.globals.CHESS_FILL_COLOR, self.globals.CHESS_FILL_ALPHA
                ),
            )
        if self.globals.CHESS_BORDER_ALPHA > 0:
            dl.add_rect(
                self.globals.chess_grid_pos["X"],
                self.globals.chess_grid_pos["Y"],
                self.globals.chess_grid_pos["W"],
                self.globals.chess_grid_pos["H"],
                imgui.get_color_u32_rgba(
                    *self.globals.CHESS_BORDER_COLOR, self.globals.CHESS_BORDER_ALPHA
                ),
                thickness=self.globals.CHESS_BORDER_THICKNESS,
            )

        # 绘制行数字提示范围
        dl.add_rect(
            self.globals.mark_row_pos["X"],
            self.globals.mark_row_pos["Y"],
            self.globals.mark_row_pos["W"],
            self.globals.mark_row_pos["H"],
            imgui.get_color_u32_rgba(
                *self.globals.MARK_BORDER_COLOR, self.globals.MARK_BORDER_ALPHA
            ),
            thickness=self.globals.MARK_BORDER_THICKNESS,
        )

        # 绘制列数字提示范围
        dl.add_rect(
            self.globals.mark_col_pos["X"],
            self.globals.mark_col_pos["Y"],
            self.globals.mark_col_pos["W"],
            self.globals.mark_col_pos["H"],
            imgui.get_color_u32_rgba(
                *self.globals.MARK_BORDER_COLOR, self.globals.MARK_BORDER_ALPHA
            ),
            thickness=self.globals.MARK_BORDER_THICKNESS,
        )

        # 绘制行数字提示范围格子
        for pos in self.globals.mark_row_pos_list:
            dl.add_rect(
                float(pos["X"] + 2),
                float(pos["Y"] + 2),
                float(pos["W"] - 2),
                float(pos["H"] - 2),
                imgui.get_color_u32_rgba(
                    *self.globals.MARK_BLOCK_BORDER_COLOR,
                    self.globals.MARK_BLOCK_BORDER_ALPHA,
                ),
                thickness=self.globals.MARK_BLOCK_BORDER_THICKNESS,
            )

        # 绘制列数字提示范围格子
        for pos in self.globals.mark_col_pos_list:
            dl.add_rect(
                float(pos["X"] + 2),
                float(pos["Y"] + 2),
                float(pos["W"] - 2),
                float(pos["H"] - 2),
                imgui.get_color_u32_rgba(
                    *self.globals.MARK_BLOCK_BORDER_COLOR,
                    self.globals.MARK_BLOCK_BORDER_ALPHA,
                ),
                thickness=self.globals.MARK_BLOCK_BORDER_THICKNESS,
            )

        # 绘制横盘内的格子
        for i, row in enumerate(self.globals.chess_block_pos):
            for j, pos in enumerate(row):

                color = None
                if len(nonograms_result) > 1:
                    if nonograms_result[i][j] == 1:
                        color = imgui.get_color_u32_rgba(
                            *self.globals.CHESS_BLOCK_BORDER_COLOR_TRUE,
                            self.globals.CHESS_BLOCK_BORDER_ALPHA,
                        )
                    elif nonograms_result[i][j] == 0:
                        color = imgui.get_color_u32_rgba(
                            *self.globals.CHESS_BLOCK_BORDER_COLOR_FALSE,
                            self.globals.CHESS_BLOCK_BORDER_ALPHA,
                        )
                    else:
                        color = imgui.get_color_u32_rgba(
                            *self.globals.CHESS_BLOCK_BORDER_COLOR,
                            self.globals.CHESS_BLOCK_BORDER_ALPHA,
                        )
                else:
                    color = imgui.get_color_u32_rgba(
                        *self.globals.CHESS_BLOCK_BORDER_COLOR,
                        self.globals.CHESS_BLOCK_BORDER_ALPHA,
                    )
                dl.add_rect(
                    float(pos["X"] + 1),
                    float(pos["Y"] + 1),
                    float(pos["W"] - 1),
                    float(pos["H"] - 1),
                    color,
                    thickness=self.globals.CHESS_BLOCK_BORDER_THICKNESS,
                )

    def imdraw_number(self, row_nums, col_nums):
        # 绘制行数字提示范围格子
        for i, pos in enumerate(self.globals.mark_row_pos_list):
            text = " ".join(str(num) for num in row_nums[i])
            imgui.set_cursor_pos((float(pos["X"] + 2), float(pos["Y"] + 4)))
            imgui.text(text)

        # 绘制列数字提示范围格子
        for i, pos in enumerate(self.globals.mark_col_pos_list):
            line_height = imgui.get_text_line_height()
            total_height = len(col_nums[i]) * line_height
            text = "\n".join(str(num) for num in col_nums[i])
            imgui.set_cursor_pos((float(pos["X"] + 7), float(pos["Y"] - total_height)))
            imgui.text(text)

    def init_window(self):
        """初始化窗口并自动检测 Retina 缩放"""
        if not glfw.init():
            raise RuntimeError("Failed to init GLFW")

        # 透明、无边框、置顶、MSAA可选
        glfw.window_hint(glfw.DECORATED, glfw.FALSE)
        glfw.window_hint(glfw.FLOATING, glfw.TRUE)
        glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
        glfw.window_hint(glfw.SAMPLES, 4)

        # macOS OpenGL 上下文要求
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)

        # 创建窗口
        self.im_window = glfw.create_window(1, 1, "Overlay", None, None)
        if not self.im_window:
            glfw.terminate()
            raise RuntimeError("Failed to create window")
        glfw.make_context_current(self.im_window)

        # 初始化imgui
        imgui.create_context()
        self.impl = GlfwRenderer(self.im_window)

        # 设置点击穿透（窗口已创建后调用）
        self.make_window_click_through(self.im_window)

    def run(self):
        self.init_window()

        imgui_update = 0
        ocr_update = 0
        nonograms_result: List[List[int]] = [[]]

        # target = {"X": 100, "Y": -1000, "W": 600, "H": 1000}
        # glfw.set_window_pos(im_window, target["X"], target["Y"])
        # glfw.set_window_size(im_window, target["W"], target["H"])

        while not glfw.window_should_close(self.im_window):
            glfw.poll_events()
            self.impl.process_inputs()

            now = time.time()

            if now - imgui_update >= self.globals.UPDATE_UI_FPS:
                imgui_update = now

                target = self.window.get_window_size(self.globals.APP_TITLE)
                if not target:
                    print("未找到 iphone镜像 窗口，程序已退出...")
                    return

                glfw.set_window_pos(self.im_window, target["X"], target["Y"])
                glfw.set_window_size(self.im_window, target["W"], target["H"])
                # print(window.get_mouse_pos_in_window(target))

                if now - ocr_update >= self.globals.UPDATE_OCR_FPS:
                    ocr_update = now

                    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: 更新ocr")

                    winID = self.window.get_window_id(self.globals.APP_TITLE)
                    image_capture = self.window.get_window_capture(winID)

                    row_nums = []
                    col_nums = []
                    for index, value in enumerate(self.globals.mark_row_pos_list):
                        numbers = self.ocr.match_numbers(image_capture, value)
                        num_sort = util.nums_sort(numbers, "x")
                        row_nums.append(num_sort)
                    for index, value in enumerate(self.globals.mark_col_pos_list):
                        numbers = self.ocr.match_numbers(image_capture, value)
                        num_sort = util.nums_sort(numbers, "y")
                        col_nums.append(num_sort)

                    grin_num = self.globals.chess_grid_num
                    if len(row_nums) >= grin_num & len(col_nums) >= grin_num:
                        rows_list = util.dict2list(row_nums, "name")
                        cols_list = util.dict2list(col_nums, "name")
                        nonograms_result = self.solve.solve_nonogram_partial(
                            rows_list, cols_list
                        )

            # if self.impl:
            #     self.impl.process_inputs()
            imgui.new_frame()

            ww, wh = glfw.get_window_size(self.im_window)
            ww = max(1, ww)
            wh = max(1, wh)

            # 使用无背景窗口在(0,0)-(cur_w,cur_h)范围内绘制
            # 注意：这里的 ImGui 坐标是当前 GLFW 窗口的局部坐标
            imgui.set_next_window_position(0, 0, condition=imgui.ALWAYS)
            imgui.set_next_window_size(ww, wh, condition=imgui.ALWAYS)
            flags = (
                imgui.WINDOW_NO_TITLE_BAR
                | imgui.WINDOW_NO_RESIZE
                | imgui.WINDOW_NO_MOVE
                | imgui.WINDOW_NO_SCROLLBAR
                | imgui.WINDOW_NO_SAVED_SETTINGS
                | imgui.WINDOW_NO_BRING_TO_FRONT_ON_FOCUS
                | imgui.WINDOW_NO_BACKGROUND
            )

            imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0, 0))
            opened, _ = imgui.begin("FollowWindowOverlay", True, flags)
            if opened:
                # 绘制app范围
                dl = imgui.get_window_draw_list()
                self.imdraw_grid(ww, wh, dl, nonograms_result)
                grin_num = self.globals.chess_grid_num
                if len(row_nums) >= grin_num & len(col_nums) >= grin_num:
                    self.imdraw_number(rows_list, cols_list)

            imgui.end()
            imgui.pop_style_var()

            # 提交渲染
            imgui.render()
            # 你的 OpenGL 绘制清屏为透明
            import OpenGL.GL as gl

            fbw, fbh = glfw.get_framebuffer_size(self.im_window)
            gl.glViewport(0, 0, fbw, fbh)
            gl.glClearColor(0.0, 0.0, 0.0, 0.0)  # 透明
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            if self.impl:
                self.impl.render(imgui.get_draw_data())

            glfw.swap_buffers(self.im_window)

        # 清理
        if self.impl:
            self.impl.shutdown()
            glfw.terminate()
