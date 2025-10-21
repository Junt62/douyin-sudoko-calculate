# 不同配置下的速度对比
import pyautogui
import time


class ClickSpeedTest:
    """点击速度测试类"""

    @staticmethod
    def test_basic_click(count=1000):
        """测试基础点击速度"""
        pyautogui.PAUSE = 0

        start = time.time()
        for _ in range(count):
            pyautogui.click()
        elapsed = time.time() - start

        print(f"基础点击 {count} 次")
        print(f"耗时: {elapsed:.3f} 秒")
        print(f"速度: {count/elapsed:.2f} 次/秒")
        print(f"间隔: {elapsed/count*1000:.2f} 毫秒\n")

        return count / elapsed

    @staticmethod
    def test_click_with_coordinates(count=1000):
        """测试带坐标的点击速度"""
        pyautogui.PAUSE = 0

        start = time.time()
        for _ in range(count):
            pyautogui.click(100, 100)
        elapsed = time.time() - start

        print(f"带坐标点击 {count} 次")
        print(f"耗时: {elapsed:.3f} 秒")
        print(f"速度: {count/elapsed:.2f} 次/秒")
        print(f"间隔: {elapsed/count*1000:.2f} 毫秒\n")

        return count / elapsed

    @staticmethod
    def test_mousedown_mouseup(count=1000):
        """测试分离的按下/释放速度"""
        pyautogui.PAUSE = 0

        start = time.time()
        for _ in range(count):
            pyautogui.mouseDown()
            pyautogui.mouseUp()
        elapsed = time.time() - start

        print(f"mouseDown/mouseUp {count} 次")
        print(f"耗时: {elapsed:.3f} 秒")
        print(f"速度: {count/elapsed:.2f} 次/秒")
        print(f"间隔: {elapsed/count*1000:.2f} 毫秒\n")

        return count / elapsed

    @staticmethod
    def test_with_custom_delay(count=1000, delay=0.001):
        """测试自定义延迟"""
        pyautogui.PAUSE = 0

        start = time.time()
        for _ in range(count):
            pyautogui.click()
            time.sleep(delay)
        elapsed = time.time() - start

        print(f"自定义延迟 {delay*1000}ms，点击 {count} 次")
        print(f"耗时: {elapsed:.3f} 秒")
        print(f"速度: {count/elapsed:.2f} 次/秒")
        print(f"间隔: {elapsed/count*1000:.2f} 毫秒\n")

        return count / elapsed


# 运行测试
if __name__ == "__main__":
    tester = ClickSpeedTest()

    print("=" * 50)
    print("PyAutoGUI 点击速度测试")
    print("=" * 50 + "\n")

    # 测试不同方式
    speed1 = tester.test_basic_click(1000)
    speed2 = tester.test_click_with_coordinates(1000)
    speed3 = tester.test_mousedown_mouseup(1000)
    speed4 = tester.test_with_custom_delay(1000, 0.001)

    print("=" * 50)
    print("总结:")
    print(f"基础点击最快: {speed1:.2f} 次/秒")
    print(f"带坐标点击: {speed2:.2f} 次/秒")
    print(f"分离按下/释放: {speed3:.2f} 次/秒")
    print(f"1ms延迟: {speed4:.2f} 次/秒")
