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

import globals as g
import ocr
import window
import solve


class ui:
    window = None
    ocr = None
    solve = None

    def __init__(self):
        self.window = window.window()
        self.ocr = ocr.ocr()
        self.solve = solve.solve()

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

    def element_draw(self, dl, ww, wh, nonograms_result):
        # 绘制app范围
        if g.appRangeFillAlpha > 0.0:
            fill_col = imgui.get_color_u32_rgba(
                *g.appRangeFillColor, g.appRangeFillAlpha
            )
            dl.add_rect_filled(0, 0, ww, wh, fill_col, 0.0)
        border_col = imgui.get_color_u32_rgba(
            *g.appRangeBorderColor, g.appRangeBorderAlpha
        )
        dl.add_rect(
            0, 0, ww, wh, border_col, 0.0, 0, thickness=g.appRangeBorderThickness
        )

        # 绘制棋盘范围
        fill_col = imgui.get_color_u32_rgba(
            *g.chessRangeFillColor, g.chessRangeFillAlpha
        )
        dl.add_rect_filled(
            g.chessPos["X"], g.chessPos["Y"], g.chessPos["W"], g.chessPos["H"], fill_col
        )
        border_col = imgui.get_color_u32_rgba(
            *g.chessRangeBorderColor, g.chessRangeBorderAlpha
        )
        dl.add_rect(
            g.chessPos["X"],
            g.chessPos["Y"],
            g.chessPos["W"],
            g.chessPos["H"],
            border_col,
            thickness=g.chessRangeBorderThickness,
        )

        # 绘制行数字提示范围
        dl.add_rect(
            g.chessPosNumTintRow["X"],
            g.chessPosNumTintRow["Y"],
            g.chessPosNumTintRow["W"],
            g.chessPosNumTintRow["H"],
            imgui.get_color_u32_rgba(
                *g.chessPosNumTintRangeBorderColor, g.chessPosNumTintRangeBorderAlpha
            ),
            thickness=g.chessPosNumTintRangeBorderThickness,
        )

        # 绘制列数字提示范围
        dl.add_rect(
            g.chessPosNumTintCol["X"],
            g.chessPosNumTintCol["Y"],
            g.chessPosNumTintCol["W"],
            g.chessPosNumTintCol["H"],
            imgui.get_color_u32_rgba(
                *g.chessPosNumTintRangeBorderColor, g.chessPosNumTintRangeBorderAlpha
            ),
            thickness=g.chessPosNumTintRangeBorderThickness,
        )

        # 绘制行数字提示范围格子
        for pos in g.chessPosNumTintRowList:
            dl.add_rect(
                float(pos["X"] + 2),
                float(pos["Y"] + 2),
                float(pos["W"] - 2),
                float(pos["H"] - 2),
                imgui.get_color_u32_rgba(
                    *g.chessPosNumTintEveryRangeBorderColor,
                    g.chessPosNumTintEveryRangeBorderAlpha,
                ),
                thickness=g.chessPosNumTintEveryRangeBorderThickness,
            )

        # 绘制列数字提示范围格子
        for pos in g.chessPosNumTintColList:
            dl.add_rect(
                float(pos["X"] + 2),
                float(pos["Y"] + 2),
                float(pos["W"] - 2),
                float(pos["H"] - 2),
                imgui.get_color_u32_rgba(
                    *g.chessPosNumTintEveryRangeBorderColor,
                    g.chessPosNumTintEveryRangeBorderAlpha,
                ),
                thickness=g.chessPosNumTintEveryRangeBorderThickness,
            )

        # 绘制横盘内的格子
        for i, row in enumerate(g.chessPosEveryBlockGrid):
            for j, pos in enumerate(row):

                color = None
                if len(nonograms_result) > 1:
                    if nonograms_result[i][j] == 1:
                        color = imgui.get_color_u32_rgba(
                            *g.chessPosEveryBlockGridRangeBorderColorTrue,
                            g.chessPosEveryBlockGridRangeBorderAlpha,
                        )
                    elif nonograms_result[i][j] == 0:
                        color = imgui.get_color_u32_rgba(
                            *g.chessPosEveryBlockGridRangeBorderColorFalse,
                            g.chessPosEveryBlockGridRangeBorderAlpha,
                        )
                    else:
                        color = imgui.get_color_u32_rgba(
                            *g.chessPosEveryBlockGridRangeBorderColor,
                            g.chessPosEveryBlockGridRangeBorderAlpha,
                        )
                else:
                    color = imgui.get_color_u32_rgba(
                        *g.chessPosEveryBlockGridRangeBorderColor,
                        g.chessPosEveryBlockGridRangeBorderAlpha,
                    )
                dl.add_rect(
                    float(pos["X"] + 1),
                    float(pos["Y"] + 1),
                    float(pos["W"] - 1),
                    float(pos["H"] - 1),
                    color,
                    thickness=g.chessPosEveryBlockGridRangeBorderThickness,
                )

    def build(self):
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

        im_window = glfw.create_window(1, 1, "Overlay", None, None)
        if not im_window:
            glfw.terminate()
            raise RuntimeError("Failed to create window")
        glfw.make_context_current(im_window)

        imgui.create_context()
        impl = GlfwRenderer(im_window)

        # 设置点击穿透（窗口已创建后调用）
        self.make_window_click_through(im_window)

        imgui_update = 0
        ocr_update = 0
        nonograms_result: List[List[int]] = [[]]

        while not glfw.window_should_close(im_window):
            glfw.poll_events()
            impl.process_inputs()

            now = time.time()

            if now - imgui_update >= g.updateFramePerSecend:
                imgui_update = now

                target = self.window.get_window_size(g.appTitle)
                if not target:
                    print("未找到 iphone镜像 窗口，程序已退出...")
                    return

                glfw.set_window_pos(im_window, target["X"], target["Y"])
                glfw.set_window_size(im_window, target["W"], target["H"])
                # print(window.get_mouse_pos_in_window(target))

                if now - ocr_update >= g.updateOcrPerSecend:
                    ocr_update = now

                    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: 更新ocr")

                    # image = get_window_capture_foreground(target)

                    winID = self.window.get_window_id(g.appTitle)
                    image_capture = self.window.get_window_capture(winID)
                    scale_factor = NSScreen.mainScreen().backingScaleFactor()

                    rows = []
                    cols = []
                    for i, row in enumerate(g.chessPosNumTintRowList):
                        cropL = g.chessPosNumTintRowList[i]["X"] * scale_factor
                        cropR = g.chessPosNumTintRowList[i]["W"] * scale_factor
                        cropT = g.chessPosNumTintRowList[i]["Y"] * scale_factor
                        cropB = g.chessPosNumTintRowList[i]["H"] * scale_factor
                        image_croped = image_capture.crop((cropL, cropT, cropR, cropB))
                        numbers = self.ocr.find_numbers_in_region(image_croped, row)
                        rows.append(numbers)
                    for i, col in enumerate(g.chessPosNumTintColList):
                        cropL = g.chessPosNumTintColList[i]["X"] * scale_factor
                        cropR = g.chessPosNumTintColList[i]["W"] * scale_factor
                        cropT = g.chessPosNumTintColList[i]["Y"] * scale_factor
                        cropB = g.chessPosNumTintColList[i]["H"] * scale_factor
                        image_croped = image_capture.crop((cropL, cropT, cropR, cropB))
                        numbers = self.ocr.find_numbers_in_region(image_croped, col)
                        cols.append(numbers)

                    nonograms_result = self.solve.solve_nonogram_partial(rows, cols)

            if impl:
                impl.process_inputs()
            imgui.new_frame()

            ww, wh = glfw.get_window_size(im_window)
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
                dl = imgui.get_window_draw_list()

                self.element_draw(dl, ww, wh, nonograms_result)

            imgui.end()
            imgui.pop_style_var()

            # 提交渲染
            imgui.render()
            # 你的 OpenGL 绘制清屏为透明
            import OpenGL.GL as gl

            fbw, fbh = glfw.get_framebuffer_size(im_window)
            gl.glViewport(0, 0, fbw, fbh)
            gl.glClearColor(0.0, 0.0, 0.0, 0.0)  # 透明
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            if impl:
                impl.render(imgui.get_draw_data())

            glfw.swap_buffers(im_window)

        # 清理
        if impl:
            impl.shutdown()
            imgui.destroy_context()
            glfw.terminate()
