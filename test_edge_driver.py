#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edge驱动诊断脚本
用于检查Edge浏览器和驱动是否正常工作
"""

import os
import sys
import subprocess

def check_edge_installation():
    """检查Edge浏览器是否安装"""
    print("=" * 60)
    print("Edge浏览器安装检查")
    print("=" * 60)

    edge_paths = [
        "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
    ]

    found = False
    for path in edge_paths:
        if os.path.exists(path):
            print(f"✓ Edge浏览器已安装: {path}")
            found = True

            # 尝试获取版本
            try:
                result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"  Edge版本: {result.stdout.strip()}")
                else:
                    print(f"  无法获取版本信息")
            except:
                print(f"  无法运行Edge获取版本")

    if not found:
        print("❌ Edge浏览器未安装")
        print("请安装Microsoft Edge浏览器")
        return False

    return True

def check_edge_driver():
    """检查Edge驱动是否安装"""
    print("\n" + "=" * 60)
    print("Edge WebDriver检查")
    print("=" * 60)

    driver_paths = [
        "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedgedriver.exe",
        "C:\\Program Files\\Microsoft\\Edge\\Application\\msedgedriver.exe",
        os.path.expanduser("~\\msedgedriver.exe"),
        ".\\msedgedriver.exe",
    ]

    found = False
    for path in driver_paths:
        if os.path.exists(path):
            print(f"✓ Edge驱动存在: {path}")

            # 检查文件大小
            size = os.path.getsize(path)
            print(f"  文件大小: {size:,} 字节 ({size/1024/1024:.2f} MB)")

            # 检查文件修改时间
            mtime = os.path.getmtime(path)
            from datetime import datetime
            print(f"  修改时间: {datetime.fromtimestamp(mtime)}")

            found = True

    if not found:
        print("❌ Edge驱动未找到")
        print("请下载Edge WebDriver并放置在以下位置之一:")
        for path in driver_paths:
            print(f"  - {path}")
        return False

    return True

def check_python_packages():
    """检查Python包是否安装"""
    print("\n" + "=" * 60)
    print("Python包检查")
    print("=" * 60)

    packages = ["selenium", "webdriver-manager"]

    for package in packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            print(f"  安装命令: pip install {package}")
            return False

    return True

def test_selenium_edge():
    """测试Selenium是否能打开Edge"""
    print("\n" + "=" * 60)
    print("Selenium Edge测试")
    print("=" * 60)

    try:
        from selenium import webdriver
        from selenium.webdriver.edge.service import Service
        from selenium.webdriver.edge.options import Options

        print("正在尝试打开Edge浏览器...")

        # 配置选项
        edge_options = Options()
        edge_options.add_argument("--disable-blink-features=AutomationControlled")

        # 尝试多个驱动路径
        driver_paths = [
            "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedgedriver.exe",
            "C:\\Program Files\\Microsoft\\Edge\\Application\\msedgedriver.exe",
            os.path.expanduser("~\\msedgedriver.exe"),
            ".\\msedgedriver.exe",
        ]

        success = False
        for path in driver_paths:
            if os.path.exists(path):
                try:
                    print(f"尝试使用驱动: {path}")
                    service = Service(executable_path=path)
                    driver = webdriver.Edge(service=service, options=edge_options)

                    print("✓ Edge浏览器成功打开!")
                    print(f"  当前URL: {driver.current_url}")
                    print(f"  浏览器标题: {driver.title}")

                    # 关闭浏览器
                    driver.quit()
                    success = True
                    break

                except Exception as e:
                    print(f"  驱动测试失败: {e}")

        if not success:
            print("❌ 所有驱动路径测试失败")
            print("尝试使用系统路径中的驱动...")
            try:
                driver = webdriver.Edge(options=edge_options)
                print("✓ 使用系统路径驱动成功!")
                driver.quit()
                success = True
            except Exception as e:
                print(f"❌ 系统路径驱动也失败: {e}")

        return success

    except Exception as e:
        print(f"❌ Selenium测试失败: {e}")
        return False

def main():
    """主函数"""
    print("Edge驱动诊断工具")
    print("=" * 60)

    checks = [
        ("Edge浏览器安装", check_edge_installation),
        ("Edge驱动检查", check_edge_driver),
        ("Python包检查", check_python_packages),
        ("Selenium测试", test_selenium_edge),
    ]

    all_passed = True
    for check_name, check_func in checks:
        print(f"\n>>> 正在检查: {check_name}")
        try:
            if check_func():
                print(f"✓ {check_name} 通过")
            else:
                print(f"❌ {check_name} 失败")
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} 检查出错: {e}")
            all_passed = False

    print("\n" + "=" * 60)
    print("诊断结果总结")
    print("=" * 60)

    if all_passed:
        print("✓ 所有检查通过! Edge驱动应该能正常工作")
        print("现在可以运行雨课堂自动观看脚本了")
    else:
        print("❌ 发现问题! 请根据上面的提示解决问题")
        print("\n常见解决方案:")
        print("1. 下载匹配的Edge WebDriver:")
        print("   - 访问: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
        print("   - 下载与Edge浏览器版本匹配的驱动")
        print("2. 以管理员身份运行脚本")
        print("3. 暂时禁用防病毒软件")
        print("4. 确保Edge浏览器已关闭")

    print("\n按回车键退出...")
    input()

if __name__ == "__main__":
    main()