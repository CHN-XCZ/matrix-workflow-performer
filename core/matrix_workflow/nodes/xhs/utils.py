import threading
import time

from uiautomator2 import connect_usb


class SmoothScroller:
    def __init__(self, device, interval_ms=2000, step_px=0):
        self.device = device
        self.interval = interval_ms / 1000.0
        self.step = step_px
        self._running = False
        self._thread = None
        self.screen_width, self.screen_height = self.device.window_size()
        self.swipe_x = self.screen_width // 2
        self.current_y = int(self.screen_height * 0.5)

    def _scroll_loop(self):
        while self._running:
            try:
                start_y = self.current_y
                end_y = start_y - self.step
                try:
                    self._slide()
                except Exception as e:
                    print(f"[滑动异常] {e}")
                    break
                print(f"开始{start_y}--->结束{end_y}")
                # self.current_y = end_y
                # time.sleep(self.interval)
            except Exception as e:
                print(f"[滑动异常] {e}")
                break

    def _slide(self):
        start_y = self.current_y
        end_y = start_y - self.step
        # self.device.shell(f"input swipe {self.swipe_x} {start_y} {self.swipe_x} {end_y} {1}")
        self.device.swipe(self.swipe_x, start_y, self.swipe_x, end_y, duration=0)

    def start(self):
        if self._running:
            print("滑动已在运行中")
            return
        print("启动滑动")
        self._running = True
        self._thread = threading.Thread(target=self._scroll_loop)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        if not self._running:
            print("滑动未运行")
            return
        print("停止滑动")
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
            self._thread = None

    @property
    def is_running(self):
        return self._running






def scroll_until_element_and_scroll_distance(d,text=''):
    """
    滑动直到找到目标元素，并向上滑动它与另一个元素之间的垂直距离
    """
    # ddd = connect_usb()
    # ddd.scroll_to(text)

    width, height = d.window_size()
    start_x = width // 2
    swipe_y = int(height * 0.5)

    while not d(resourceId="com.xingin.xhs:id/jci",text=text).exists:
        # d.swipe(start_x, swipe_y+100, start_x, swipe_y-100,duration=0.1)
        d.shell(f"input swipe {start_x} { swipe_y+100} {start_x} {swipe_y-100} 200")


    time.sleep(1)
    el_it8 = d(resourceId="com.xingin.xhs:id/it8", className="android.widget.RelativeLayout")
    if not el_it8.exists:
        print("参照元素未找到，无法计算距离")
        return
    el_dk = d(resourceId="com.xingin.xhs:id/jci",text=text)

    dk_center_y = el_dk.center()[1]
    it8_center_y = el_it8.center()[1]
    # print(el_dk.center())
    # print(el_it8.center())

    distance = dk_center_y - it8_center_y
    if distance <= 0:
        print("无需滑动")
        return

    swipe_start_y = dk_center_y
    swipe_end_y = it8_center_y + 100

    # print(f"滑动: {swipe_start_y} -> {swipe_end_y}")
    # d.swipe(start_x, swipe_start_y, start_x, swipe_end_y, duration=0.8)
    timeee = abs(swipe_start_y - swipe_end_y)
    d.shell(f"input swipe {start_x} {swipe_start_y} {start_x} {swipe_end_y} {int(timeee)+500}")
    print("滑动完成")


def close_update_popup(d):
    while d(resourceId="com.xingin.xhs:id/hcq",text="知道了").exists:
        d(resourceId="com.xingin.xhs:id/hcq",text="知道了").click()
        time.sleep(1)