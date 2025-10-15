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
from typing import Optional, Dict
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

from globals import *
from ocr import *
from window import *
from solve import *


def approx_equal(a, b, eps=1):
    return abs(a - b) <= eps


def make_window_click_through(window):
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


def buildImgui():
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

    window = glfw.create_window(1, 1, "Overlay", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Failed to create window")
    glfw.make_context_current(window)

    imgui.create_context()
    impl = GlfwRenderer(window)

    # 设置点击穿透（窗口已创建后调用）
    make_window_click_through(window)

    def get_scale():
        sx, sy = glfw.get_window_content_scale(window)
        if sx <= 0:
            sx = 1.0
        if sy <= 0:
            sy = 1.0
        return sx, sy

    imgui_update = 0
    ocr_update = 0
    templates = load_digit_templates("templates")
    nonograms_result: List[List[int]] = [[]]

    while not glfw.window_should_close(window):
        glfw.poll_events()
        # 即使穿透，仍会收到一些窗口事件，这里简单处理
        impl.process_inputs()

        now = time.time()

        if now - imgui_update >= updateFramePerSecend:
            imgui_update = now

            target = get_window_size(appTitle)
            if target:
                glfw.set_window_pos(window, target["X"], target["Y"])
                glfw.set_window_size(window, target["W"], target["H"])
                # print(get_mouse_pos_in_window(target))

        if now - ocr_update >= updateOcrPerSecend:
            ocr_update = now

            target = get_window_size(appTitle)
            if target:
                print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: 更新ocr")

                image = get_window_capture_foreground(target)

                # image = get_window_capture(get_window_id(appTitle), target)

                rows = [
                    [2],
                    [2],
                    [1, 2],
                    [3, 1],
                    [1, 2, 2],
                    [2, 1],
                    [7],
                    [3, 3],
                    [7],
                    [3, 4, 1],
                    [7, 1, 2],
                    [2, 1, 6],
                    [1],
                    [1],
                    [1],
                    [1],
                    [1],
                ]
                cols = [
                    [2],
                    [3],
                    [2, 5],
                    [2, 5],
                    [6, 2],
                    [3, 3],
                    [6],
                    [4, 1],
                    [8],
                    [3, 1],
                    [3, 2],
                    [2, 3],
                    [1],
                    [1],
                    [1],
                    [1],
                    [1],
                ]
                nonograms_result = solve_nonogram_partial(rows, cols)

        if impl:
            impl.process_inputs()
        imgui.new_frame()

        ww, wh = glfw.get_window_size(window)
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

            # 绘制app范围
            if appRangeFillAlpha > 0.0:
                fill_col = imgui.get_color_u32_rgba(
                    *appRangeFillColor, appRangeFillAlpha
                )
                dl.add_rect_filled(0, 0, ww, wh, fill_col, 0.0)
            border_col = imgui.get_color_u32_rgba(
                *appRangeBorderColor, appRangeBorderAlpha
            )
            dl.add_rect(
                0, 0, ww, wh, border_col, 0.0, 0, thickness=appRangeBorderThickness
            )

            # 绘制棋盘范围
            fill_col = imgui.get_color_u32_rgba(
                *chessRangeFillColor, chessRangeFillAlpha
            )
            dl.add_rect_filled(
                chessPos["X1"], chessPos["Y1"], chessPos["X2"], chessPos["Y2"], fill_col
            )
            border_col = imgui.get_color_u32_rgba(
                *chessRangeBorderColor, chessRangeBorderAlpha
            )
            dl.add_rect(
                chessPos["X1"],
                chessPos["Y1"],
                chessPos["X2"],
                chessPos["Y2"],
                border_col,
                thickness=chessRangeBorderThickness,
            )

            # 绘制行数字提示范围
            dl.add_rect(
                chessPosNumTintRow["X1"],
                chessPosNumTintRow["Y1"],
                chessPosNumTintRow["X2"],
                chessPosNumTintRow["Y2"],
                imgui.get_color_u32_rgba(
                    *chessPosNumTintRangeBorderColor, chessPosNumTintRangeBorderAlpha
                ),
                thickness=chessPosNumTintRangeBorderThickness,
            )

            # 绘制列数字提示范围
            dl.add_rect(
                chessPosNumTintCol["X1"],
                chessPosNumTintCol["Y1"],
                chessPosNumTintCol["X2"],
                chessPosNumTintCol["Y2"],
                imgui.get_color_u32_rgba(
                    *chessPosNumTintRangeBorderColor, chessPosNumTintRangeBorderAlpha
                ),
                thickness=chessPosNumTintRangeBorderThickness,
            )

            # 绘制行数字提示范围格子
            for pos in chessPosNumTintRowList:
                dl.add_rect(
                    float(pos["X1"] + 2),
                    float(pos["Y1"] + 2),
                    float(pos["X2"] - 2),
                    float(pos["Y2"] - 2),
                    imgui.get_color_u32_rgba(
                        *chessPosNumTintEveryRangeBorderColor,
                        chessPosNumTintEveryRangeBorderAlpha,
                    ),
                    thickness=chessPosNumTintEveryRangeBorderThickness,
                )

            # 绘制列数字提示范围格子
            for pos in chessPosNumTintColList:
                dl.add_rect(
                    float(pos["X1"] + 2),
                    float(pos["Y1"] + 2),
                    float(pos["X2"] - 2),
                    float(pos["Y2"] - 2),
                    imgui.get_color_u32_rgba(
                        *chessPosNumTintEveryRangeBorderColor,
                        chessPosNumTintEveryRangeBorderAlpha,
                    ),
                    thickness=chessPosNumTintEveryRangeBorderThickness,
                )

            # 绘制横盘内的格子
            for i, row in enumerate(chessPosEveryBlockGrid):
                for j, pos in enumerate(row):

                    color = None
                    if len(nonograms_result) > 1:
                        if nonograms_result[i][j] == 1:
                            color = imgui.get_color_u32_rgba(
                                *chessPosEveryBlockGridRangeBorderColorTrue,
                                chessPosEveryBlockGridRangeBorderAlpha,
                            )
                        elif nonograms_result[i][j] == 0:
                            color = imgui.get_color_u32_rgba(
                                *chessPosEveryBlockGridRangeBorderColorFalse,
                                chessPosEveryBlockGridRangeBorderAlpha,
                            )
                        else:
                            color = imgui.get_color_u32_rgba(
                                *chessPosEveryBlockGridRangeBorderColor,
                                chessPosEveryBlockGridRangeBorderAlpha,
                            )
                    else:
                        color = imgui.get_color_u32_rgba(
                            *chessPosEveryBlockGridRangeBorderColor,
                            chessPosEveryBlockGridRangeBorderAlpha,
                        )
                    dl.add_rect(
                        float(pos["X1"] + 1),
                        float(pos["Y1"] + 1),
                        float(pos["X2"] - 1),
                        float(pos["Y2"] - 1),
                        color,
                        thickness=chessPosEveryBlockGridRangeBorderThickness,
                    )
                    # if chessPosEveryBlockGridRangeFillAlpha > 0.0:
                    #     dl.add_rect_filled(
                    #         float(pos["X1"] + 2),
                    #         float(pos["Y1"] - 2),
                    #         float(pos["X2"] - 2),
                    #         float(pos["Y2"] + 2),
                    #         imgui.get_color_u32_rgba(
                    #             *chessPosEveryBlockGridRangeFillColor, chessPosEveryBlockGridRangeFillAlpha
                    #         ),
                    #     )

        imgui.end()
        imgui.pop_style_var()

        # 提交渲染
        imgui.render()
        # 你的 OpenGL 绘制清屏为透明
        import OpenGL.GL as gl

        fbw, fbh = glfw.get_framebuffer_size(window)
        gl.glViewport(0, 0, fbw, fbh)
        gl.glClearColor(0.0, 0.0, 0.0, 0.0)  # 透明
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        if impl:
            impl.render(imgui.get_draw_data())

        glfw.swap_buffers(window)

    # 清理
    if impl:
        impl.shutdown()
        imgui.destroy_context()
        glfw.terminate()


if __name__ == "__main__":
    buildImgui()
