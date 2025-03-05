import time

from loguru import logger


def click_element_id(d, element_id, element_text=None):
    """
    检查指定ID的元素是否存在，如果存在则点击该元素。

    :param element_text:
    :param d: uiautomator2连接的设备对象
    :param element_id: 要查找并点击的元素的resourceId
    """
    try:
        if element_text is not None:
            element = d(resourceId=element_id, text=element_text)
        else:
            element = d(resourceId=element_id)
        if element.exists:
            element.click()
            # logger.info(f"已点击元素: {element_id}")
        else:
            logger.warning(f"元素 {element_id} 不存在，未执行点击")
    except Exception as e:
        logger.exception(f"点击元素 {element_id} 时发生错误: {e}")


def click_desc_element(d, element_desc):
    """
    检查指定ID的元素是否存在，如果存在则点击该元素。

    :param element_desc: 要查找并点击的元素的desc
    :param d: uiautomator2连接的设备对象
    """
    try:

        # element = d(descriptionContains=element_desc)
        element = d(description=element_desc)
        if element.exists:
            element.click()
            # logger.info(f"已点击元素: {element_id}")
        else:
            logger.warning(f"元素 {element_desc} 不存在，未执行点击")
    except Exception as e:
        logger.exception(f"点击元素 {element_desc} 时发生错误: {e}")


def click_text_element(device, text):
    """
    点击页面上指定 text 的元素

    :param device: uiautomator2 连接的设备对象
    :param text: 要点击的元素的文本内容
    :return: 是否成功点击 (True/False)
    """
    try:
        # 查找具有指定 text 的元素
        element = device(text=text)
        if element.exists:
            element.click()
            return True
        else:
            logger.warning(f"未找到文本为 '{text}' 的元素")
            return False
    except Exception as e:
        logger.exception(f"点击文本为 '{text}' 的元素时发生错误: {e}")
        return False


def click_right_half_of_element(d, element_id, element_text=None):
    """
    查找页面上 id 为 'com.twitter.android:id/detail_text' 且 text 为 '已有账号？登录' 的元素，
    然后点击元素的右半部分。

    参数:
    - d: uiautomator2 的设备实例
    """
    try:
        # 查找目标元素
        element = d(resourceId=element_id, text=element_text)
        if element.exists:
            # 获取元素的位置信息
            bounds = element.info['bounds']
            x_center = (bounds['left'] + bounds['right']) // 2  # 元素中心x坐标
            y_center = (bounds['top'] + bounds['bottom']) // 2  # 元素中心y坐标
            x_right = (bounds['right'] + x_center) // 2  # 元素右半部分中心x坐标

            # 点击右半部分
            d.click(x_right, y_center)
            print("成功点击 '已有账号？登录' 元素的右半部分")
        else:
            print("未找到 '已有账号？登录' 元素")
    except Exception as e:
        print(f"点击过程中出错: {e}")


def click_desc_button(d, desc):
    """
    查找 content-desc 为 'Switch accounts' 且 className 为 'android.view.View' 的按钮，
    然后点击与其同级的 className 为 'android.widget.Button' 的按钮。

    :param desc: content-desc
    :param d: uiautomator2 连接的设备对象
    """
    try:
        # 查找 content-desc 为 'Switch accounts' 且 className 为 'android.view.View' 的按钮
        # switch_account_view = d(className="android.view.View", description=desc)
        switch_account_view = d(className="android.view.View", descriptionContains=desc)

        # 判断该元素是否存在
        if switch_account_view.exists:
            # 获取同级的 android.widget.Button 元素
            sibling_button = switch_account_view.sibling(className="android.widget.Button")
            # sibling_button = d.xpath(
            #     "//android.widget.TextView[@text='Add an existing account']/following-sibling::android.widget.Button"
            # )
            if sibling_button.exists:
                sibling_button.click()
                # logger.info("已点击同级的按钮")
            else:
                logger.warning("未找到同级的 class 为 'android.widget.Button' 的按钮")
        else:
            logger.warning(f"未找到 {desc} 按钮")
    except Exception as e:
        logger.exception(f"点击同级按钮时发生错误: {e}")


def click_desc_timeout_button(d, desc, timeout=10):
    """
    查找 content-desc 为 'Switch accounts' 且 className 为 'android.view.View' 的按钮，
    然后点击与其同级的 className 为 'android.widget.Button' 的按钮。

    :param desc: content-desc
    :param d: uiautomator2 连接的设备对象
    :param timeout: 超时时间
    """
    try:
        # 查找 content-desc 为 'Switch accounts' 且 className 为 'android.view.View' 的按钮
        # switch_account_view = d(className="android.view.View", description=desc)
        switch_account_view = d(className="android.view.View", descriptionContains=desc)

        # 判断该元素是否存在
        if switch_account_view.wait(timeout=timeout):
            switch_account_view.click()
            # # 获取同级的 android.widget.Button 元素
            # sibling_button = switch_account_view.sibling(className="android.widget.Button")
            # # sibling_button = d.xpath(
            # #     "//android.widget.TextView[@text='Add an existing account']/following-sibling::android.widget.Button"
            # # )
            # if sibling_button.wait(timeout=timeout):
            #     sibling_button.click()
            #     logger.info(F"已点击{desc}按钮")
            # else:
            #     logger.warning("未找到同级的 class 为 'android.widget.Button' 的按钮")
        else:
            logger.warning(f"未找到 {desc} 按钮")
    except Exception as e:
        logger.exception(f"点击同级按钮时发生错误: {e}")


def click_text_button(device, btn_text):
    """
    查找 content-desc 为 'Switch accounts' 且 className 为 'android.view.View' 的按钮，
    然后点击与其同级的 className 为 'android.widget.Button' 的按钮。

    :param btn_text: text
    :param device: uiautomator2 连接的设备对象
    """
    try:
        text_button = device.xpath(
            f"//android.widget.TextView[@text='{btn_text}']/following-sibling::android.widget.Button"
        )
        # 判断该元素是否存在
        if text_button.exists:
            text_button.click()
            logger.info(f"已点击{btn_text}按钮")
        else:
            logger.warning(f"未找到 {btn_text} 按钮")
    except Exception as e:
        logger.exception(f"点击按钮时发生错误: {e}")


def click_text_timeout_button(device, btn_text, cn_text=None, timeout=5):
    """
    查找 content-desc 为 'Switch accounts' 且 className 为 'android.view.View' 的按钮，
    然后点击与其同级的 className 为 'android.widget.Button' 的按钮。

    :param btn_text: text
    :param device: uiautomator2 连接的设备对象
    :param cn_text 中文内容
    :param timeout 等待时间
    """
    try:
        text_button = device(className="android.widget.TextView", text=btn_text)
        # 判断该元素是否存在
        if text_button.wait(timeout=timeout):
            text_button.click()
            logger.info(f"已点击{btn_text}按钮")
            return True
        else:
            if cn_text is not None:
                text_button = device(className="android.widget.TextView", text=cn_text)
                if text_button.wait(timeout=timeout):
                    text_button.click()
                    logger.info(f"已点击{cn_text}按钮")
                    return True
                else:
                    logger.warning(f"未找到 {cn_text} 按钮")
            logger.warning(f"未找到 {btn_text} 按钮")
            return False
    except Exception as e:
        logger.exception(f"点击按钮时发生错误: {e}")


def click_resource_timeout_button(device, resource_id, class_name, btn_text=None, timeout=5):
    """
    查找 content-desc 为 'Switch accounts' 且 className 为 'android.view.View' 的按钮，
    然后点击与其同级的 className 为 'android.widget.Button' 的按钮。

    :param btn_text: text
    :param device: uiautomator2 连接的设备对象
    :param resource_id id
    :param class_name: className
    :param timeout 等待时间
    """
    try:
        if btn_text is not None:
            text_button = device(resourceId=resource_id, className=class_name, text=btn_text)
        else:
            text_button = device(resourceId=resource_id, className=class_name)
        # 判断该元素是否存在
        if text_button.wait(timeout=timeout):
            text_button.click()
            logger.info(f"已点击{btn_text}按钮")
        else:
            logger.warning(f"未找到 {btn_text} 按钮")
    except Exception as e:
        logger.exception(f"点击按钮时发生错误: {e}")


def click_contains_text_button(device, btn_text):
    """
    查找 content-desc 为 'Switch accounts' 且 className 为 'android.view.View' 的按钮，
    然后点击与其同级的 className 为 'android.widget.Button' 的按钮。

    :param btn_text: text
    :param device: uiautomator2 连接的设备对象
    """
    try:
        text_button = device.xpath(
            f"//android.widget.TextView[contains(@text, '{btn_text}')]"
        )
        # 判断该元素是否存在
        if text_button.exists:
            text_button.click()
            logger.info(f"已点击{btn_text}按钮")
        else:
            logger.warning(f"未找到 {btn_text} 按钮")
    except Exception as e:
        logger.exception(f"点击按钮时发生错误: {e}")


def click_text_element(device, btn_text):
    """
    查找 content-desc 为 btn_text 且 className 为 'android.view.View' 的按钮。

    :param btn_text: text
    :param device: uiautomator2 连接的设备对象
    """
    try:
        text_button = device.xpath(
            f"//android.widget.TextView[@text='{btn_text}']"
        )
        # 判断该元素是否存在
        if text_button.exists:
            text_button.click()
            # logger.info(f"已点击{btn_text}按钮")
        else:
            logger.warning(f"未找到 {btn_text} 按钮")
    except Exception as e:
        logger.exception(f"点击按钮时发生错误: {e}")


def click_caret_ignore_button(d):
    """
    查找页面上 id 为 com.twitter.android:id/caret 且 content-desc 为 'Timeline message prompt option' 的按钮，并点击它。

    :param d: uiautomator2 连接的设备对象
    """
    try:
        # 查找指定的按钮
        caret_button = d(resourceId="com.twitter.android:id/caret", description="Timeline message prompt option")

        # 检查该按钮是否存在
        if caret_button.exists:
            caret_button.click()
            # 等待新按钮出现（可根据需要调整等待时间）
            time.sleep(1)  # 等待1秒以确保新按钮加载
            logger.info("已点击 Timeline message prompt option 按钮")
        else:
            logger.warning("未找到 Timeline message prompt option 按钮")
    except Exception as e:
        logger.exception(f"点击按钮时发生错误: {e}")


def click_ignore_button(d, resource_id=None, ignore_texts=None):
    """
    查找页面上 id 为 com.twitter.android:id/caret 且 content-desc 为 'Timeline message prompt option' 的按钮，并点击它。

    :param d: uiautomator2 连接的设备对象
    :param ignore_texts: 按钮文字
    :param resource_id:
    """
    if ignore_texts is None:
        ignore_texts = ["忽略", "减少看到的频率"]  # 默认文本列表
    try:
        if resource_id is not None:
            # 查找指定的按钮
            button = d(resourceId=resource_id, description="Timeline message prompt option")
            if not button.exists:
                button = d(resourceId=resource_id, description="Dismiss")
            # 检查该按钮是否存在
            if button.exists:
                button.click()
                # 等待新按钮出现（可根据需要调整等待时间）
                time.sleep(1)  # 等待1秒以确保新按钮加载
                for ig_text in ignore_texts:
                    ignore_button = d(resourceId="com.twitter.android:id/action_sheet_item_title", text=ig_text)
                    if ignore_button.exists:
                        ignore_button.click()
                        break
                    else:
                        logger.warning(f"未找到 '{ig_text}' 按钮")
    except Exception as e:
        logger.exception(f"点击按钮时发生错误: {e}")


def get_ui_element(d, resource_id=None, description=None, text=None, class_name=None):
    """
    获取 UI 元素的通用方法，根据提供的属性选择元素。

    :param d: uiautomator2 连接的设备对象
    :param resource_id: 元素的 resource ID
    :param description: 元素的内容描述
    :param text: 元素的文本内容
    :param class_name: 元素的类名
    :return: 找到的元素或 None
    """
    try:
        element = d(resourceId=resource_id, description=description, text=text, className=class_name)

        if element.exists:
            return element
        else:
            logger.warning("未找到满足条件的 UI 元素")
            return None
    except Exception as e:
        logger.exception(f"获取 UI 元素时发生错误: {e}")
        return None


def is_point_in_area(x, y, area):
    """
    检查点 (x, y) 是否在排除区域内。
    :param x: 点的 x 坐标
    :param y: 点的 y 坐标
    :param area: 排除区域，格式为 (left, top, right, bottom)
    :return: 如果点在排除区域内，返回 True，否则返回 False
    """
    left, top, right, bottom = area
    return left <= x <= right and top <= y <= bottom


def click_without_overlap(d, element, exclusion_area):
    """
    点击元素，但避免点击排除区域。

    :param d: uiautomator2 的设备对象。
    :param element: 需要点击的元素。
    :param exclusion_area: 排除区域，格式为 (left, top, right, bottom)
    :return: 无返回值。
    """
    # 获取元素的位置
    element_bounds = element.info['bounds']
    element_left = element_bounds['left']
    element_top = element_bounds['top']
    element_right = element_bounds['right']
    element_bottom = element_bounds['bottom']
    # 在元素的范围内寻找一个合适的点击位置，避免点击排除区域
    # 先从元素的中心开始
    click_x = (element_left + element_right) // 2
    click_y = (element_top + element_bottom) // 2
    if exclusion_area:
        left, top, right, bottom = exclusion_area

        # 检查中心点是否在排除区域内
        if is_point_in_area(click_x, click_y, exclusion_area):
            # 如果中心点在排除区域，尝试点击其他位置
            # 可以选择元素的顶部、底部、左侧或右侧，避免排除区域
            if click_y >= top:
                click_y = element_top
            elif click_y <= bottom:
                click_y = element_bottom
            elif click_x >= left:
                click_x = element_left
            elif click_x <= right:
                click_x = element_right

        # 点击调整后的坐标
    d.click(click_x, click_y)


def click_button_id_text(device, button_text, button_id):
    """
    点击指定 text 和 resourceId 的 android.widget.Button

    :param device: uiautomator2 设备对象
    :param button_text: 按钮的文本内容
    :param button_id: 按钮的 resourceId
    :return: 是否成功点击 (True/False)
    """
    try:
        # 定位按钮
        button = device(className="android.widget.Button", text=button_text, resourceId=button_id)
        if button.exists:
            print(f"找到按钮: text='{button_text}', id='{button_id}'")
            button.click()
            print("成功点击按钮")
            return True
        else:
            print(f"未找到按钮: text='{button_text}', id='{button_id}'")
            return False
    except Exception as e:
        print(f"点击按钮时发生错误: {e}")
        return False


def click_element_class_id(device, element_class, element_id):
    try:
        element = device(className=element_class, resourceId=element_id)
        if element.exists:
            element.click()
            return True
        else:
            return False
    except Exception as e:
        print(f"点击按钮时发生错误: {e}")
        return False


def click_element_class_desc(device, element_class, content_desc):
    try:
        element = device(className=element_class, description=content_desc)
        if element.exists:
            element.click()
            return True
        else:
            return False
    except Exception as e:
        print(f"点击按钮时发生错误: {e}")
        return False
