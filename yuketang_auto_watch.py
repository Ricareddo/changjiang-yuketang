#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雨课堂自动观看视频脚本
基于Selenium和Edge浏览器
功能：
1. 自动启动Edge浏览器
2. 扫码登录雨课堂
3. 展开章节列表，获取所有视频链接
4. 按顺序播放每个视频
5. 检测视频播放进度，播放完成后自动返回列表
6. 继续播放下一个视频，直到所有视频播放完毕
"""

import time
import sys
import os
import re
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.microsoft import EdgeChromiumDriverManager


class YuketangAutoWatch:
    """雨课堂自动观看视频类"""

    def __init__(self, headless=False):
        """
        初始化
        :param headless: 是否无头模式，默认False（显示浏览器）
        """
        self.headless = headless
        self.driver = None
        self.wait = None
        self.video_links = []  # 存储视频信息字典列表
        self.current_video_index = 0  # 当前播放到的视频索引

    def setup_driver(self):
        """改进的Edge驱动设置方法"""
        print("正在设置Edge浏览器驱动...")

        # 配置Edge选项
        edge_options = Options()
        if self.headless:
            edge_options.add_argument("--headless")

        # 添加反检测参数
        edge_options.add_argument("--disable-blink-features=AutomationControlled")
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("--disable-dev-shm-usage")
        edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        edge_options.add_experimental_option('useAutomationExtension', False)

        # 策略1：尝试使用系统路径中的Edge驱动
        try:
            self.driver = webdriver.Edge(options=edge_options)
            print("✓ 使用系统路径中的Edge驱动成功")
        except Exception as e:
            print(f"❌ 系统路径驱动失败: {e}")
            print("诊断信息：")
            print("1. 检查Edge浏览器是否安装: C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe")
            print("2. 检查Edge驱动是否存在: C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedgedriver.exe")
            print("3. 常见问题:")
            print("   - Edge浏览器版本与驱动版本不匹配")
            print("   - 防病毒软件或防火墙阻止")
            print("   - 权限不足（尝试以管理员身份运行）")

            # 策略2：尝试使用webdriver-manager
            try:
                service = Service(EdgeChromiumDriverManager().install())
                self.driver = webdriver.Edge(service=service, options=edge_options)
                print("✓ 使用webdriver-manager安装驱动成功")
            except Exception as e2:
                print(f"❌ webdriver-manager失败: {e2}")
                print("诊断信息：")
                print("1. webdriver-manager可能因网络问题无法下载驱动")
                print("2. 尝试手动下载驱动: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
                print("3. 下载与Edge浏览器版本匹配的驱动")

                # 策略3：尝试指定常见驱动路径
                common_paths = [
                    "C:/Program Files (x86)/Microsoft/Edge/Application/msedgedriver.exe",
                    "C:/Program Files/Microsoft/Edge/Application/msedgedriver.exe",
                    os.path.expanduser("~/msedgedriver.exe"),
                    "./msedgedriver.exe"
                ]

                driver_found = False
                for path in common_paths:
                    try:
                        if os.path.exists(path):
                            service = Service(executable_path=path)
                            self.driver = webdriver.Edge(service=service, options=edge_options)
                            print(f"✓ 使用指定路径驱动成功: {path}")
                            driver_found = True
                            break
                    except Exception as e3:
                        continue

                if not driver_found:
                    print("❌ 所有驱动设置方法都失败")
                    print("=" * 60)
                    print("解决方案:")
                    print("1. 检查Edge浏览器版本:")
                    print("   - 打开Edge浏览器 → 设置 → 关于Microsoft Edge")
                    print("2. 下载匹配的Edge WebDriver:")
                    print("   - 访问: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
                    print("   - 下载与Edge浏览器版本匹配的驱动")
                    print("3. 将驱动放置在以下位置之一:")
                    for path in common_paths:
                        print(f"   - {path}")
                    print("4. 常见问题解决:")
                    print("   - 以管理员身份运行脚本")
                    print("   - 暂时禁用防病毒软件")
                    print("   - 检查Windows Defender防火墙设置")
                    print("   - 确保Edge浏览器已关闭")
                    print("=" * 60)
                    sys.exit(1)

        # 设置等待时间
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 20)
        print("Edge浏览器驱动设置完成")

    def check_login_status(self):
        """检查登录状态和页面结构变化"""
        try:
            # 多种登录成功和页面结构变化标志
            page_change_indicators = [
                # 用户相关元素
                "//img[contains(@class, 'avatar')]",
                "//div[contains(@class, 'user-name')]",
                "//span[contains(@class, 'user-name')]",
                "//a[contains(@href, 'profile')]",
                "//button[contains(text(), '退出登录')]",
                # 课程菜单元素（登录后显示）
                "//div[contains(text(), '我的课程')]",
                "//div[contains(text(), '我听的课')]",
                "//span[contains(text(), '我听的课')]",
                "//a[contains(text(), '我听的课')]",
                "//div[contains(@class, 'my-course')]",
                # 课程卡片元素（页面主要内容）
                "//div[contains(@class, 'course-card')]",
                "//div[contains(@class, 'course-item')]",
                "//div[contains(@class, 'el-card')]",
                "//h1[contains(@class, 'course-title')]",
                # 页面标题变化
                "//title[not(contains(text(), '登录'))]",
            ]

            for indicator in page_change_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, indicator)
                    if element and element.is_displayed():
                        print(f"✓ 检测到页面结构变化: {indicator}")
                        return True
                except:
                    continue

            # 检查URL是否变化（登录后通常重定向）
            current_url = self.driver.current_url
            if "login" not in current_url and "auth" not in current_url:
                print("✓ 检测到URL变化，可能已登录")
                return True

            # 检查页面标题是否包含课程相关关键词
            try:
                title = self.driver.title.lower()
                if "登录" not in title and "auth" not in title:
                    print("✓ 页面标题不包含登录关键词，可能已登录")
                    return True
            except:
                pass

            return False
        except:
            return False

    def login(self):
        """简化登录方法：用户自主登录，检测页面结构改变后进入下一步"""
        print("正在打开雨课堂登录页面...")
        self.driver.get("https://changjiang.yuketang.cn/")

        print("=" * 60)
        print("请使用雨课堂APP扫描页面上的二维码登录")
        print("登录成功后，脚本会自动检测页面结构变化并继续...")
        print("=" * 60)

        # 等待用户手动登录
        input("请在浏览器中扫码登录，登录完成后按回车键继续...")

        # 检测页面结构变化（登录成功标志）
        print("正在检测登录状态...")
        max_wait = 60  # 最大等待60秒
        for i in range(max_wait, 0, -1):
            if self.check_login_status():
                print("✓ 登录成功！检测到页面结构变化")
                return True
            print(f"等待登录状态检测... {i}秒")
            time.sleep(1)

        print("❌ 登录状态检测超时，尝试继续...")
        # 即使检测失败，也允许用户继续
        print("如果已登录成功，脚本将继续执行后续步骤")
        return True

    def navigate_to_course(self, course_url=None):
        """改进的课程导航方法"""
        if course_url:
            print(f"正在导航到课程页面: {course_url}")
            self.driver.get(course_url)
            time.sleep(3)
            return

        print("正在尝试从首页进入课程...")

        # 步骤1: 点击"我听的课"或"我的课程"
        try:
            course_menu_selectors = [
                "//div[contains(text(), '我听的课')]",
                "//span[contains(text(), '我听的课')]",
                "//a[contains(text(), '我听的课')]",
                "//div[contains(text(), '我的课程')]",
                "//a[contains(@href, 'course/list')]",
                "//div[contains(@class, 'my-course')]",
            ]

            for selector in course_menu_selectors:
                try:
                    course_menu = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    course_menu.click()
                    print(f"✓ 点击: {selector}")
                    time.sleep(2)
                    break
                except:
                    continue
        except Exception as e:
            print(f"❌ 无法找到课程菜单: {e}")
            print("请手动点击'我听的课'，然后按回车键继续...")
            input()

        # 步骤2: 选择课程（点击第一个课程）
        try:
            # CSS选择器列表（用户提供的具体选择器）
            css_course_selectors = [
                "#pane-student > div.TCardGroup > div > div > div:nth-child(1) > div > div.el-card.box-card.is-hover-shadow",  # 整个卡片（可能更可点击）
                "#pane-student > div.TCardGroup > div > div > div:nth-child(1) > div > div.el-card.box-card.is-hover-shadow > div > div.left > div.top > h1",  # 用户提供的具体选择器
            ]

            # XPath选择器列表（通用选择器）
            xpath_course_selectors = [
                "//div[contains(@class, 'course-card')]",
                "//div[contains(@class, 'course-item')]",
                "//a[contains(@href, 'course/')]",
                "//div[contains(@class, 'course-list-item')]",
            ]

            # 先尝试CSS选择器（用户提供的）
            for selector in css_course_selectors:
                try:
                    courses = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if courses:
                        print(f"找到 {len(courses)} 个课程 (CSS选择器: {selector})")
                        courses[0].click()
                        print(f"✓ 点击第一个课程")
                        time.sleep(3)
                        break
                except:
                    continue
            else:
                # 如果CSS选择器都失败，尝试XPath选择器
                for selector in xpath_course_selectors:
                    try:
                        courses = self.driver.find_elements(By.XPATH, selector)
                        if courses:
                            print(f"找到 {len(courses)} 个课程 (XPath选择器: {selector})")
                            courses[0].click()
                            print(f"✓ 点击第一个课程")
                            time.sleep(3)
                            break
                    except:
                        continue
        except Exception as e:
            print(f"❌ 无法选择课程: {e}")
            print("请手动选择课程，然后按回车键继续...")
            input()

        # 等待课程页面加载
        time.sleep(2)

    def expand_chapters(self):
        """改进的章节展开方法"""
        print("正在展开章节列表...")

        # CSS选择器列表（用户提供的具体选择器）
        css_expand_selectors = [
            "#pane--1 > div > section:nth-child(3) > div.activity-box > div.content-box > section.activity__wrap.el-tooltip > div.activity-info > div > div > span > span",  # 用户提供的具体选择器
        ]

        # XPath选择器列表（通用选择器）
        xpath_expand_selectors = [
            "//button[contains(@class, 'expand')]",
            "//div[contains(@class, 'chapter')]//button",
            "//div[contains(@class, 'section')]//button[contains(@class, 'expand')]",
            "//span[contains(@class, 'expand-icon')]",
            "//i[contains(@class, 'expand')]",
            "//div[contains(@class, 'chapter-header')]",
        ]

        expanded_count = 0

        # 先尝试CSS选择器（用户提供的）
        for selector in css_expand_selectors:
            try:
                expand_buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if expand_buttons:
                    print(f"使用CSS选择器找到 {len(expand_buttons)} 个展开按钮: {selector}")
                    for btn in expand_buttons:
                        try:
                            if btn.is_displayed() and btn.is_enabled():
                                btn.click()
                                expanded_count += 1
                                time.sleep(0.3)
                        except:
                            pass
                    if expanded_count > 0:
                        print(f"✓ 展开了 {expanded_count} 个章节")
                        time.sleep(1)
                        return
            except:
                continue

        # 如果CSS选择器失败，尝试XPath选择器
        for selector in xpath_expand_selectors:
            try:
                expand_buttons = self.driver.find_elements(By.XPATH, selector)
                if expand_buttons:
                    print(f"使用XPath选择器找到 {len(expand_buttons)} 个展开按钮: {selector}")
                    for btn in expand_buttons:
                        try:
                            if btn.is_displayed() and btn.is_enabled():
                                btn.click()
                                expanded_count += 1
                                time.sleep(0.3)
                        except:
                            pass
                    if expanded_count > 0:
                        print(f"✓ 展开了 {expanded_count} 个章节")
                        time.sleep(1)
                        return
            except:
                continue

        print("⚠ 无法自动展开章节，尝试备用方法...")

        # 备用方法: 使用JavaScript点击所有可点击的展开元素
        try:
            script = """
            var buttons = document.querySelectorAll('button, div[role="button"], span[role="button"]');
            var expanded = 0;
            for (var i = 0; i < buttons.length; i++) {
                var btn = buttons[i];
                var text = btn.textContent || btn.innerText || '';
                if (text.includes('展开') || text.includes('expand') ||
                    btn.className.includes('expand') ||
                    btn.getAttribute('aria-expanded') === 'false') {
                    try {
                        btn.click();
                        expanded++;
                        // 小延迟避免过快点击
                        await new Promise(resolve => setTimeout(resolve, 100));
                    } catch(e) {}
                }
            }
            return expanded;
            """
            expanded = self.driver.execute_script(script)
            print(f"✓ 使用JavaScript展开了 {expanded} 个章节")
        except Exception as e:
            print(f"❌ 展开章节失败: {e}")
            print("请手动展开所有章节，然后按回车键继续...")
            input()

    def _has_digit_prefix(self, text):
        """检查文本是否以数字开头（支持多种数字格式）"""
        if not text:
            return False

        # 去除首尾空格
        text = text.strip()
        if not text:
            return False

        # 检查第一个字符是否是数字（包括中文数字）
        first_char = text[0]
        if first_char.isdigit():
            return True

        # 检查常见数字模式：如 "1.", "01)", "一、" 等
        digit_patterns = [
            r'^\d+[\.\)\、\s]',      # 数字后跟点、括号、顿号、空格
            r'^[一二三四五六七八九十]+[\.\)\、\s]',  # 中文数字
            r'^[0-9]+[\s]',          # 数字后跟空格
        ]

        import re
        for pattern in digit_patterns:
            if re.match(pattern, text):
                return True

        return False

    def collect_video_links(self, clear_existing=True):
        """改进的视频链接收集方法

        Args:
            clear_existing: 是否清空已有视频列表，默认True
        """
        print("正在收集视频链接...")
        if clear_existing:
            self.video_links = []

        # 获取已存在的视频标题集合
        existing_titles = {v["title"] for v in self.video_links}

        # 精确的CSS选择器（直接匹配视频标题元素）
        precise_selectors = [
            # 用户提供的精确选择器
            "#pane--1 > div > section:nth-child(3) > div.activity-box > div.content-box.nopaddingb > section.leaf_list__wrap > div > div > div > div > section > div.el-tooltip.activity-info > div > h2",
            # 通用化版本（匹配所有章节中的视频标题）
            "section.leaf_list__wrap h2",
        ]

        for selector in precise_selectors:
            try:
                video_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if video_elements:
                    print(f"使用选择器找到 {len(video_elements)} 个候选元素")

                    for idx, element in enumerate(video_elements):
                        try:
                            # 获取视频标题
                            title = element.text.strip()
                            if not title:
                                continue

                            # 只保留以数字开头的标题（过滤非视频元素）
                            if not self._has_digit_prefix(title):
                                continue

                            # 如果视频已存在，跳过
                            if title[:50] in existing_titles:
                                continue

                            # 尝试获取可点击的父元素
                            href = None
                            try:
                                parent_link = element.find_element(By.XPATH, "./ancestor::a")
                                href = parent_link.get_attribute("href")
                            except:
                                pass

                            self.video_links.append({
                                "title": title[:50],
                                "href": href,
                                "selector": selector,
                                "index": idx
                            })
                            print(f"  [{len(self.video_links)}] {title}")

                        except Exception:
                            continue

                    if self.video_links:
                        print(f"✓ 共收集到 {len(self.video_links)} 个视频")
                        return

            except Exception as e:
                print(f"选择器查找失败: {e}")
                continue

        # 如果精确选择器失败，提示用户手动操作
        if not self.video_links:
            print("❌ 未找到视频链接")
            print("请手动点击第一个视频，然后按回车键继续...")
            input()
            self.video_links.append({
                "title": "当前视频",
                "href": self.driver.current_url,
                "selector": "manual",
                "index": 0
            })

    def check_video_player_exists(self):
        """检查视频播放器是否存在（通过进度条选择器检测）"""
        try:
            # 多种视频播放器指示器选择器
            player_indicators = [
                # 视频元素
                "//video",
                "//iframe[contains(@src, 'video')]",
                # 进度条相关元素
                "//div[contains(@class, 'progress')]",
                "//div[contains(@class, 'seek-bar')]",
                "//div[contains(@class, 'time')]",
                "//span[contains(@class, 'current')]",
                "//span[contains(@class, 'duration')]",
                "//div[contains(@role, 'progressbar')]",
                # 播放控制元素
                "//button[contains(@class, 'play')]",
                "//button[contains(@class, 'pause')]",
                "//div[contains(@class, 'player')]",
                # 时间显示（如 00:00 / 10:00）
                "//span[contains(text(), '/')]",
            ]

            for indicator in player_indicators:
                try:
                    elements = self.driver.find_elements(By.XPATH, indicator)
                    for elem in elements:
                        if elem.is_displayed():
                            print(f"✓ 检测到视频播放器元素: {indicator}")
                            return True
                except:
                    continue

            # 尝试通过JavaScript检测video元素
            script = """
            var videos = document.querySelectorAll('video');
            if (videos.length > 0) return true;
            var iframes = document.querySelectorAll('iframe');
            for (var i = 0; i < iframes.length; i++) {
                try {
                    var iframeDoc = iframes[i].contentDocument || iframes[i].contentWindow.document;
                    if (iframeDoc.querySelector('video')) return true;
                } catch(e) {}
            }
            return false;
            """
            result = self.driver.execute_script(script)
            if result:
                print("✓ 通过JavaScript检测到视频元素")
                return True

            return False
        except Exception as e:
            print(f"检查视频播放器时出错: {e}")
            return False

    def find_video_element_by_title(self, title):
        """根据标题重新查找视频元素"""
        try:
            # 使用精确的CSS选择器，与collect_video_links保持一致
            selectors = [
                "section.leaf_list__wrap h2",
                "#pane--1 h2",
            ]

            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.is_displayed() and title in elem.text:
                            # 找到匹配的元素，查找可点击的父级
                            try:
                                clickable = elem.find_element(By.XPATH, "./ancestor::a | ./ancestor::section[contains(@class, 'activity')]")
                                return clickable
                            except:
                                return elem
                except:
                    continue

            return None
        except Exception as e:
            print(f"查找视频元素时出错: {e}")
            return None

    def play_video(self, video_info, index, total):
        """
        播放单个视频
        :param video_info: 视频信息字典
        :param index: 当前视频索引
        :param total: 视频总数
        """
        title = video_info["title"]
        href = video_info["href"]

        print(f"\n[{index}/{total}] 正在播放视频: {title}")

        # 先尝试通过标题重新查找元素（页面可能已刷新）
        element = self.find_video_element_by_title(title)

        if element:
            try:
                # 滚动到元素可见位置
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.5)
                element.click()
                print("✓ 点击视频元素成功")
                time.sleep(3)
            except Exception as e:
                print(f"点击视频元素失败: {e}")
                # 尝试使用JavaScript点击
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                    print("✓ 使用JavaScript点击成功")
                    time.sleep(3)
                except:
                    # 如果点击失败，尝试通过URL导航
                    if href and href.startswith(('http://', 'https://')):
                        print(f"尝试直接访问链接...")
                        self.driver.get(href)
                        time.sleep(3)
                    else:
                        print(f"无法点击，请手动操作...")
                        input("请手动点击视频开始播放，然后按回车键继续...")
        else:
            # 如果找不到元素，尝试通过URL导航
            if href and href.startswith(('http://', 'https://')):
                print(f"通过URL访问视频...")
                self.driver.get(href)
                time.sleep(3)
            else:
                print(f"无法找到视频元素，请手动操作...")
                input("请手动点击视频开始播放，然后按回车键继续...")

        # 等待视频播放器加载
        print("等待视频播放器加载...")
        time.sleep(5)

        # 检测视频播放器是否存在
        if not self.check_video_player_exists():
            print(f"⚠ 未检测到视频播放器，跳过视频: {title}")
            print("这可能不是视频内容（如PDF、文档等）")
            return

        # 尝试查找并点击播放按钮
        try:
            play_button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'play')] | //div[contains(@class, 'play-button')]")
            if play_button:
                play_button.click()
                print("点击播放按钮")
                time.sleep(2)
        except:
            print("未找到播放按钮，视频可能自动播放")

        # 监控视频播放进度
        self.monitor_video_progress()

        print(f"视频播放完成: {title}")

    def get_video_progress_method1(self):
        """方法1: 通过时间元素获取进度"""
        try:
            # 多种时间元素选择器
            time_selectors = [
                ("current-time", "duration"),
                ("currentTime", "duration"),
                ("vjs-current-time", "vjs-duration"),
                ("time-current", "time-duration"),
                ("progress-current", "progress-duration"),
            ]

            for current_class, duration_class in time_selectors:
                try:
                    current_elem = self.driver.find_element(By.CLASS_NAME, current_class)
                    duration_elem = self.driver.find_element(By.CLASS_NAME, duration_class)

                    if current_elem and duration_elem:
                        current_time = self.parse_time(current_elem.text)
                        total_time = self.parse_time(duration_elem.text)

                        if total_time > 0:
                            progress = (current_time / total_time) * 100
                            return progress
                except:
                    continue

            # 尝试XPath选择器
            xpath_patterns = [
                "//span[contains(@class, 'current') and contains(@class, 'time')]",
                "//div[contains(@class, 'current') and contains(@class, 'time')]",
                "//span[contains(text(), '/')]",  # 类似 "1:30/10:00"
            ]

            for xpath in xpath_patterns:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for elem in elements:
                        text = elem.text.strip()
                        if '/' in text:
                            parts = text.split('/')
                            if len(parts) == 2:
                                current_time = self.parse_time(parts[0].strip())
                                total_time = self.parse_time(parts[1].strip())
                                if total_time > 0:
                                    progress = (current_time / total_time) * 100
                                    return progress
                except:
                    continue

            return None
        except:
            return None

    def get_video_progress_method2(self):
        """方法2: 通过JavaScript获取视频状态"""
        try:
            script = """
            // 尝试查找video元素
            var video = document.querySelector('video');
            if (video) {
                if (video.duration > 0) {
                    return (video.currentTime / video.duration) * 100;
                }
            }

            // 尝试查找iframe内的video
            var iframes = document.querySelectorAll('iframe');
            for (var i = 0; i < iframes.length; i++) {
                try {
                    var iframeDoc = iframes[i].contentDocument || iframes[i].contentWindow.document;
                    var iframeVideo = iframeDoc.querySelector('video');
                    if (iframeVideo && iframeVideo.duration > 0) {
                        return (iframeVideo.currentTime / iframeVideo.duration) * 100;
                    }
                } catch(e) {}
            }

            // 检查是否有进度条
            var progressBars = document.querySelectorAll('[role="progressbar"], .progress-bar, .seek-bar');
            for (var i = 0; i < progressBars.length; i++) {
                var bar = progressBars[i];
                var value = bar.getAttribute('aria-valuenow') || bar.style.width;
                if (value) {
                    var percent = parseFloat(value);
                    if (!isNaN(percent)) {
                        return percent;
                    }
                }
            }

            return null;
            """

            result = self.driver.execute_script(script)
            if result is not None:
                return float(result)
            return None
        except:
            return None

    def check_completion_indicators(self):
        """检查完成提示"""
        completion_texts = [
            "播放完成", "已完成", "观看完成", "恭喜你完成学习",
            "学习完成", "任务完成", "恭喜完成", "completed",
            "finish", "done", "恭喜您完成"
        ]

        for text in completion_texts:
            try:
                elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
                for elem in elements:
                    if elem.is_displayed():
                        return True
            except:
                continue

        return False

    def check_next_button(self):
        """检查下一步按钮"""
        next_button_texts = [
            "下一节", "下一个", "继续学习", "下一章",
            "next", "continue", "下一视频", "下一个视频"
        ]

        for text in next_button_texts:
            try:
                buttons = self.driver.find_elements(By.XPATH, f"//button[contains(text(), '{text}')]")
                for btn in buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        return True
            except:
                continue

        return False

    def handle_progress(self, progress, start_time, last_progress):
        """处理进度信息"""
        print(f"播放进度: {progress:.1f}%")

        # 检查是否卡住
        if abs(progress - last_progress) < 0.1:
            elapsed = time.time() - start_time
            if elapsed > 600:  # 10分钟无进展
                print("⚠ 视频可能卡住，尝试点击播放按钮...")
                try:
                    play_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'play')]")
                    for btn in play_buttons:
                        if btn.is_displayed():
                            btn.click()
                            print("✓ 点击播放按钮")
                            break
                except:
                    pass

    def monitor_video_progress(self):
        """改进的视频进度监控方法"""
        print("开始监控视频播放进度...")

        start_time = time.time()
        last_progress = 0
        no_progress_count = 0
        max_no_progress = 30  # 30次检查无进展视为卡住

        while True:
            try:
                # 方法1: 尝试获取视频时间元素
                progress = self.get_video_progress_method1()
                if progress is not None:
                    self.handle_progress(progress, start_time, last_progress)
                    last_progress = progress
                    if progress >= 98:
                        print("✓ 视频播放完成（方法1）")
                        time.sleep(3)
                        return
                    time.sleep(10)
                    continue

                # 方法2: 尝试通过JavaScript获取视频状态
                progress = self.get_video_progress_method2()
                if progress is not None:
                    self.handle_progress(progress, start_time, last_progress)
                    last_progress = progress
                    if progress >= 98:
                        print("✓ 视频播放完成（方法2）")
                        time.sleep(3)
                        return
                    time.sleep(10)
                    continue

                # 方法3: 检查完成提示
                if self.check_completion_indicators():
                    print("✓ 检测到播放完成提示")
                    time.sleep(3)
                    return

                # 方法4: 检查下一步按钮
                if self.check_next_button():
                    print("✓ 检测到下一节按钮")
                    time.sleep(3)
                    return

                # 无进展计数
                no_progress_count += 1
                if no_progress_count >= max_no_progress:
                    print("⚠ 长时间无进展，视频可能已播放完成或卡住")

                    # 检查总播放时间
                    elapsed = time.time() - start_time
                    if elapsed > 1800:  # 30分钟
                        print("✓ 已播放30分钟，假设视频播放完成")
                        return
                    else:
                        print("尝试刷新页面...")
                        self.driver.refresh()
                        time.sleep(5)
                        no_progress_count = 0
                        start_time = time.time()

                time.sleep(10)

            except Exception as e:
                print(f"进度监控出错: {e}")
                time.sleep(10)

    def parse_time(self, time_str):
        """解析时间字符串为秒数"""
        try:
            if ':' in time_str:
                parts = time_str.split(':')
                if len(parts) == 3:  # HH:MM:SS
                    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                elif len(parts) == 2:  # MM:SS
                    return int(parts[0]) * 60 + int(parts[1])
            return int(time_str)
        except:
            return 0

    def _click_all_logs_tab(self):
        """点击'全部日志'标签页，确保显示完整页面"""
        try:
            all_logs_tab = self.driver.find_element(By.CSS_SELECTOR, "#pane-log > div.radioTab > div.el-radio-group > label.el-radio-button.is-active > span")
            if all_logs_tab.is_displayed() and all_logs_tab.is_enabled():
                all_logs_tab.click()
                print("✓ 点击'全部日志'标签页")
                time.sleep(1)
                return True
        except Exception as e:
            print(f"⚠ 无法点击'全部日志'标签页: {e}")
            # 尝试其他可能的选择器
            alternative_selectors = [
                "//span[contains(text(), '全部日志')]",
                "//label[contains(@class, 'el-radio-button')]//span[contains(text(), '全部日志')]",
                "//div[contains(@class, 'radioTab')]//span[contains(text(), '全部日志')]",
            ]

            for selector in alternative_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed() and element.is_enabled():
                        element.click()
                        print(f"✓ 使用备用选择器点击'全部日志': {selector}")
                        time.sleep(1)
                        return True
                except:
                    continue

        print("⚠ 无法找到或点击'全部日志'标签页，页面可能已正确显示")
        return False

    def return_to_list(self):
        """返回到视频列表并确保显示完整页面"""
        print("返回视频列表...")
        success = False

        # 优先使用用户提供的CSS选择器
        try:
            back_btn = self.driver.find_element(By.CSS_SELECTOR, "#app > div.viewContainer > div > div.header-bar__wrap > div > div.f14.back.fl.flex-disaply > span")
            back_btn.click()
            print("✓ 使用指定返回选择器成功")
            time.sleep(3)
            success = True
        except:
            print("指定返回选择器未找到，尝试备用选择器...")

        if not success:
            # 备用方案1: 其他可能的返回按钮选择器（CSS）
            css_selectors = [
                ".back-button",
                "button.back",
                "a.back",
                "[class*='back']",
            ]

            for selector in css_selectors:
                try:
                    back_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if back_btn.is_displayed() and back_btn.is_enabled():
                        back_btn.click()
                        print(f"✓ 使用CSS选择器返回: {selector}")
                        time.sleep(3)
                        success = True
                        break
                except:
                    continue

        if not success:
            # 备用方案2: XPath选择器
            try:
                back_btn = self.driver.find_element(By.XPATH, "//button[contains(@class, 'back')] | //a[contains(@href, 'course')]")
                back_btn.click()
                print("✓ 使用XPath选择器返回")
                time.sleep(3)
                success = True
            except:
                print("所有返回选择器都失败，尝试浏览器后退...")

        if not success:
            # 最终方案: 浏览器后退
            try:
                self.driver.back()
                print("✓ 使用浏览器后退")
                time.sleep(3)
                success = True
            except:
                print("❌ 返回列表失败，请手动操作")
                input("请手动返回视频列表，然后按回车键继续...")

        # 如果成功返回列表，点击"全部日志"标签页确保显示完整页面，然后重新展开章节
        if success:
            self._click_all_logs_tab()
            # 返回列表后章节可能被折叠了，重新展开章节以确保显示视频列表
            print("重新展开章节以确保显示视频列表...")
            self.expand_chapters()
            # 等待页面稳定
            time.sleep(2)

    def run(self, course_url=None):
        """运行主程序"""
        print("=" * 50)
        print("雨课堂自动观看视频脚本")
        print("=" * 50)

        try:
            # 1. 设置浏览器驱动
            self.setup_driver()

            # 2. 登录
            if not self.login():
                print("登录失败，退出程序")
                return

            # 3. 进入课程页面
            self.navigate_to_course(course_url)

            # 4. 展开章节
            self.expand_chapters()

            # 5. 收集视频链接
            self.collect_video_links()

            if not self.video_links:
                print("没有找到视频，退出程序")
                return

            # 6. 按顺序播放视频
            total_videos = len(self.video_links)
            self.current_video_index = 0

            while self.current_video_index < total_videos:
                video = self.video_links[self.current_video_index]
                idx = self.current_video_index + 1

                self.play_video(video, idx, total_videos)

                # 如果不是最后一个视频，返回列表并准备播放下一个
                if idx < total_videos:
                    self.return_to_list()
                    # 返回列表后重新收集视频链接，确保元素引用有效
                    # 但不清空视频标题列表，只重新查找元素
                    print("重新查找视频元素...")
                    self.collect_video_links(clear_existing=False)
                    self.current_video_index += 1
                    time.sleep(1)
                else:
                    self.current_video_index += 1

            print("\n" + "=" * 50)
            print(f"所有视频播放完成！共播放了 {total_videos} 个视频")
            print("=" * 50)

            # 等待用户查看结果
            input("\n按回车键退出...")

        except KeyboardInterrupt:
            print("\n用户中断程序")
        except Exception as e:
            print(f"程序运行出错: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.driver:
                print("关闭浏览器...")
                self.driver.quit()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="雨课堂自动观看视频脚本")
    parser.add_argument("--url", help="课程URL，如果不提供则需要手动进入课程")
    parser.add_argument("--headless", action="store_true", help="无头模式（不显示浏览器窗口）")

    args = parser.parse_args()

    # 创建自动观看对象
    auto_watch = YuketangAutoWatch(headless=args.headless)

    # 运行
    auto_watch.run(course_url=args.url)


if __name__ == "__main__":
    main()