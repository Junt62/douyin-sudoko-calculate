from email.mime import image
import AppKit
import Quartz
import re
from PIL import Image
from AppKit import NSScreen
from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly,
    kCGWindowListOptionIncludingWindow,
    kCGNullWindowID,
    CGDisplayBounds,
    CGMainDisplayID,
    CGGetActiveDisplayList,
    CGGetOnlineDisplayList,
    CGDisplayBounds,
)
from typing import Tuple, Dict, Optional
from Cocoa import NSApp, NSApplication, NSWindow, NSScreen
import subprocess
import os
import time

import mss


class Window:

    def get_main_screen_height(self):
        # NSScreen 使用左下为原点，但我们只需要总高度来翻转 y
        main = AppKit.NSScreen.mainScreen()
        frame = main.frame()  # NSRect, origin at bottom-left
        return int(frame.size.height)

    def get_mouse_pos_screen_top_left(self):
        # CGEventGetLocation 返回的是全局坐标，原点在左下，y 向上
        loc = Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))
        x_bl = loc.x
        y_bl = loc.y
        H = self.get_main_screen_height()
        # 转为“屏幕左上为原点，y 向下”
        x_tl = int(round(x_bl))
        y_tl = int(round(y_bl))
        return x_tl, y_tl

    def get_mouse_pos_in_window(self, window_bounds):
        mx_tl, my_tl = self.get_mouse_pos_screen_top_left()
        wx_tl = int(round(window_bounds["X"]))
        wy_tl = int(round(window_bounds["Y"]))
        # 窗口内坐标（以窗口左上为原点，y 向下）
        local_x = mx_tl - wx_tl
        local_y = my_tl - wy_tl
        return local_x, local_y

    def get_window_size(self, app_name: str = None) -> Optional[Dict]:
        windows = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly, kCGNullWindowID
        )
        for w in windows:
            title = w.get("kCGWindowName") or ""
            if re.search(app_name, title, re.I):
                b = w.get("kCGWindowBounds") or {}
                size = {
                    "X": int(b.get("X", 0)),
                    "Y": int(b.get("Y", 0)),
                    "W": int(b.get("Width", 0)),
                    "H": int(b.get("Height", 0)),
                }
                return size
        return None

    def get_window_id(self, app_name: str = None) -> Optional[Dict]:
        windows = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly, kCGNullWindowID
        )
        for w in windows:
            title = w.get("kCGWindowName") or ""
            if re.search(app_name, title, re.I):
                b = w.get("kCGWindowBounds") or {}
                return w.get("kCGWindowNumber", 0)
        return None

    def get_window_capture(self, window_id):
        image_ref = Quartz.CGWindowListCreateImage(
            Quartz.CGRectNull,
            kCGWindowListOptionIncludingWindow,
            window_id,
            Quartz.kCGWindowImageBoundsIgnoreFraming,
        )

        if not image_ref:
            print(f"无法获取窗口ID {window_id} 的图像。")
            return False

        width = Quartz.CGImageGetWidth(image_ref)
        height = Quartz.CGImageGetHeight(image_ref)
        bits_per_component = Quartz.CGImageGetBitsPerComponent(image_ref)
        bits_per_pixel = Quartz.CGImageGetBitsPerPixel(image_ref)
        bytes_per_row = Quartz.CGImageGetBytesPerRow(image_ref)  # 关键：获取每行字节数
        color_space = Quartz.CGImageGetColorSpace(image_ref)
        bitmap_info = Quartz.CGImageGetBitmapInfo(image_ref)
        provider = Quartz.CGImageGetDataProvider(image_ref)
        data = Quartz.CGDataProviderCopyData(provider)

        data_ptr = data.bytes()
        image = Image.frombytes(
            "RGBA", (width, height), data_ptr, "raw", "BGRA", bytes_per_row, 1
        )

        # 以下代码会删除macOS窗口截图的边框和阴影，
        # 如果在默认flag下截图的话，
        # 但是截图时使用kCGWindowImageBoundsIgnoreFraming这个flag后，
        # 不再需要以下代码
        # scale_factor = NSScreen.mainScreen().backingScaleFactor()
        # win_w = window_size["W"] * scale_factor
        # win_h = window_size["H"] * scale_factor
        # cropL = int((width - win_w) / 2)
        # cropR = win_w + cropL
        # cropT = int((height - win_h) / 2) - 16
        # cropB = win_h + cropT
        # image = image.crop((cropL, cropT, cropR, cropB))

        return image

    def get_window_capture_foreground(self, win_size) -> Image:
        with mss.mss() as sct:
            image = sct.grab(
                {
                    "left": win_size["X"],
                    "top": win_size["Y"],
                    "width": win_size["W"],
                    "height": win_size["H"],
                }
            )
            image = Image.frombytes("RGB", image.size, image.rgb)
            return image
