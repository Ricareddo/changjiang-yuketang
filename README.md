# 🎓 Yuketang Auto Watch - 雨课堂自动观看视频脚本

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.x-green.svg)](https://selenium.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 基于 Selenium + Edge 浏览器的雨课堂自动化学习工具，支持自动登录、批量播放视频、进度监控等功能。

## ✨ 功能特性

- 🤖 **自动化流程**: 从登录到完成全部视频的全自动操作
- 🔐 **扫码登录**: 安全便捷的二维码登录方式
- 📚 **智能章节识别**: 自动展开并识别所有课程章节和视频
- ▶️ **批量视频播放**: 按顺序自动播放所有未看完的视频
- 📊 **实时进度监控**: 多种方式检测视频播放进度
- 🔄 **智能重试机制**: 卡顿自动恢复，确保视频完整播放
- 🛡️ **反检测优化**: 添加多种参数避免被检测为机器人
- 💡 **友好交互**: 关键步骤支持手动干预，灵活可控

## 📋 系统要求

- **操作系统**: Windows 10/11
- **浏览器**: Microsoft Edge (最新版本)
- **Python**: 3.8 及以上版本

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/yourusername/yuketang-auto-watch.git
cd yuketang-auto-watch

# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 检查环境（可选）

运行诊断脚本检查 Edge 浏览器和驱动是否正常：

```bash
python test_edge_driver.py
```

如果发现问题，请按照提示安装匹配版本的 [Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)。

### 3. 运行脚本

#### 基础用法

```bash
python yuketang_auto_watch.py
```

#### 高级用法

```bash
# 指定课程URL（跳过手动选择课程）
python yuketang_auto_watch.py --url "https://changjiang.yuketang.cn/course/xxxxx"

# 无头模式（不显示浏览器窗口）
python yuketang_auto_watch.py --headless
```

### 4. 使用流程

1. **启动脚本** → 自动打开 Edge 浏览器
2. **扫码登录** → 使用雨课堂 APP 扫描页面二维码
3. **选择课程** → 自动进入或手动指定课程
4. **自动播放** → 脚本自动展开章节、收集视频、依次播放
5. **完成提示** → 所有视频播放完成后显示统计信息

## 📖 详细说明

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--url` | 课程URL地址 | 无（需手动选择） |
| `--headless` | 启用无头模式 | False |

### 工作原理

```
┌─────────────┐    ┌─────────────┐    ┌──────────────┐
│  启动浏览器   │ → │  扫码登录     │ → │  进入课程页面  │
└─────────────┘    └─────────────┘    └──────────────┘
                                              ↓
┌─────────────┐    ┌─────────────┐    ┌──────────────┐
│  返回列表     │ ← │  监控进度     │ ← │  展开并收集   │
│  继续下一个   │    │  播放完成？   │    │  所有视频链接  │
└─────────────┘    └─────────────┘    └──────────────┘
```

### 视频进度检测方法

脚本使用多重策略检测视频播放状态：

1. **时间元素检测**: 解析页面上显示的当前时间/总时长
2. **JavaScript API**: 通过 video 元素的 currentTime/duration 属性获取
3. **UI 状态检测**: 检查"播放完成"、"下一节"等按钮或提示文字
4. **超时保护**: 超过30分钟无进展时自动视为完成

### 错误处理

- **驱动加载失败**: 自动尝试多种路径和安装方式
- **元素定位失败**: 提供多个备选选择器，支持手动干预
- **视频卡顿检测**: 10分钟无进展自动点击播放按钮
- **网络异常**: 自动刷新页面重试

## 📁 项目结构

```
yuketang-auto-watch/
├── yuketang_auto_watch.py   # 主程序脚本
├── test_edge_driver.py      # Edge驱动诊断工具
├── requirements.txt         # Python依赖
├── README.md               # 项目说明文档
└── .gitignore             # Git忽略配置
```

## ⚠️ 注意事项

1. **使用规范**
   - 本工具仅供个人学习使用
   - 请遵守学校/平台的使用规定
   - 建议在非高峰期使用以减少服务器压力

2. **使用建议**
   - 首次使用建议先运行 `test_edge_driver.py` 检查环境
   - 保持 Edge 浏览器为最新版本
   - 如遇问题，尝试关闭防病毒软件后重试
   - 建议使用虚拟环境隔离依赖

3. **常见问题**

<details>
<summary><b>❓ Edge驱动版本不匹配怎么办？</b></summary>

1. 打开 Edge 浏览器 → 设置 → 关于 Microsoft Edge，记录版本号
2. 访问 [Edge WebDriver 下载页](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)
3. 下载与浏览器版本完全一致的驱动
4. 将 `msedgedriver.exe` 放置在以下任一位置：
   - `C:\Program Files (x86)\Microsoft\Edge\Application\`
   - 当前项目目录
</details>

<details>
<summary><b>❓ 登录后没有反应？</b></summary>

- 脚本会自动检测页面变化，请耐心等待最多60秒
- 如果超时，可以按回车键继续执行
- 确保已成功登录（页面应显示课程列表而非登录界面）
</details>

<details>
<summary><b>❓ 视频无法自动播放？</b></summary>

- 某些视频可能需要手动点击一次才能启动
- 脚本会在控制台提示，按回车键后可继续
- 检查是否为特殊格式（如PDF文档、外部链接等）
</details>

<details>
<summary><b>❓ 如何停止脚本运行？</b></summary>

- 在命令行窗口按 `Ctrl + C` 即可安全退出
- 脚本会自动清理并关闭浏览器
</details>

## 🔧 开发与调试

### 日志输出

脚本会在控制台输出详细的运行日志：

```
==================================================
雨课堂自动观看视频脚本
==================================================
正在设置Edge浏览器驱动...
✓ 使用系统路径中的Edge驱动成功
正在打开雨课堂登录页面...
============================================================
请使用雨课堂APP扫描页面上的二维码登录...
============================================================
✓ 登录成功！检测到页面结构变化
正在展开章节列表...
✓ 展开了 12 个章节
正在收集视频链接...
  [1] 1.1 课程介绍
  [2] 1.2 第一章第一节
  ...
✓ 共收集到 24 个视频
[1/24] 正在播放视频: 1.1 课程介绍
播放进度: 0.0%
播放进度: 15.3%
...
✓ 视频播放完成
所有视频播放完成！共播放了 24 个视频
==================================================
```

### 自定义修改

如需适配其他在线教育平台，主要修改以下部分：

1. **登录逻辑**: 修改 `login()` 方法中的URL和登录检测逻辑
2. **课程导航**: 修改 `navigate_to_course()` 中的选择器
3. **视频收集**: 修改 `collect_video_links()` 和 `expand_chapters()` 的CSS/XPath选择器
4. **进度监控**: 根据目标平台的视频播放器调整检测方法

## 📊 技术栈

- **语言**: Python 3.8+
- **自动化框架**: Selenium 4.x
- **浏览器驱动**: Microsoft Edge WebDriver
- **驱动管理**: webdriver-manager
- **设计模式**: 面向对象编程 (OOP)

## 📄 License

本项目采用 MIT License 开源协议。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [Selenium](https://selenium.dev/) - 强大的Web自动化测试框架
- [Microsoft Edge](https://www.microsoft.com/edge) - 现代化的浏览器
- [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager) - 自动化驱动管理工具

## 📮 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给一个 Star 支持一下！⭐**

Made with ❤️ by [Your Name](https://github.com/yourusername)

</div>
