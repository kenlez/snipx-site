# SnipX 产品官网 PRD

> 版本：v0.1（框架阶段，所有图片为占位）
> 风格参考：https://fg.vkr.me/mac

## 1. 产品定位

**SnipX**：macOS 14+ 菜单栏截屏 + MP4 录屏原生应用。

**价值主张**：
- 浮于眼前，一触即达（菜单栏常驻）
- 物理像素输出，标注所见即所得
- 无网络、无账号、无上传、无远程配置、无第三方依赖

**目标用户**：macOS 14+ 用户、内容创作者、文档工程师、产品经理、设计师。

## 2. 页面结构（单页）

### 2.1 顶部导航（TopBar）
- 左侧：SnipX Logo（占位）
- 中间：锚点导航（特性 / 功能 / 下载 / 关于）
- 右侧：下载按钮（CTA）

### 2.2 Hero 区
- eyebrow：「macOS 14+ · 原生应用」
- 主标题：「SnipX」
- 副标题：「Mac 截屏与录屏，一触即达」
- 描述：「原生 AppKit + Swift + ScreenCaptureKit。物理像素输出、可编辑快捷键、长截图拼接、本地 MP4 录制。零网络、零账号、零上传。」
- 双 CTA：
  - 主：「下载 SnipX」（按钮）
  - 次：「查看功能」（锚点）
- 主视觉：大图（占位 → `hero.webp`）

### 2.3 Features 区（多行图文）

每行结构：标题 + 描述 + bullet 列表 + 大图，左右交替。

| # | 标题 | 描述 | bullet | 图位 | 占比 |
|---|---|---|---|---|---|
| F1 | 菜单栏常驻 | 浮于菜单栏，点击即开 | 截屏 / 录屏 / 标注 / 设置 全部直达 | feature-menu.webp | 左图右文 |
| F2 | 可编辑快捷键 | 全局快捷键可自由绑定 | 截屏、录屏、标注、长截图独立绑定 | feature-shortcut.webp | 左文右图 |
| F3 | 四类截屏模式 | 区域 / 窗口 / 全屏 / 长截图 | 物理像素输出、自动命名、PNG 直存 | feature-modes.webp | 左图右文 |
| F4 | 标注工具 | 矩形 / 箭头 / 文字 / 马赛克 | 可移动、可删除、撤销 / 重做、裁剪 | feature-annotation.webp | 左文右图 |
| F5 | 本地 MP4 录制 | 倒计时、状态指示、自动停止 | 磁盘保护、Recovery 保留、头尾裁剪导出 | feature-recording.webp | 左图右文 |
| F6 | 零数据外传 | 完全离线运行 | 无网络请求、无账号体系、无遥测 | feature-privacy.webp | 左文右图 |

### 2.4 安装与下载（Install）
- 标题：「立即开始」
- 三步：
  1. 下载 `.dmg`
  2. 拖入 Applications
  3. 授权截屏 / 录屏 / 麦克风权限
- 系统要求：macOS 14+、Apple Silicon / Intel

### 2.5 关于与隐私（About + Privacy）
- 关于 SnipX：原生开发、维护计划、版本号（占位 → 0.1.86）
- 隐私承诺：本地运行、数据不出本机

### 2.6 Footer
- 版权、联系方式（小红书 / 抖音 / QQ 群 / 邮箱）
- 备案号（待 ICP 备案后回填）

## 3. 文案大纲（占位文字）

- meta title：`SnipX - Mac 截屏与录屏，一触即达`
- meta description：`SnipX：macOS 14+ 菜单栏截屏与 MP4 录屏原生应用。物理像素输出、可编辑快捷键、长截图拼接、本地 MP4 录制。零网络、零账号、零上传。`
- OG image：品牌图标（占位 → `assets/brand/icon-snipx.png`）

## 4. 占位图清单

所有占位图存放于 `assets/images/placeholder/`，文件名与最终真实图保持一致。

| 文件名 | 尺寸建议 | 用途 | 状态 |
|---|---|---|---|
| `icon-snipx.png` | 256×256 | 品牌图标 / favicon | 占位（待用户提供） |
| `hero.webp` | 1920×1200 | Hero 主视觉 | 占位 |
| `feature-menu.webp` | 1280×800 | F1 菜单栏 | 占位 |
| `feature-shortcut.webp` | 1280×800 | F2 快捷键 | 占位 |
| `feature-modes.webp` | 1280×800 | F3 截屏模式 | 占位 |
| `feature-annotation.webp` | 1280×800 | F4 标注 | 占位 |
| `feature-recording.webp` | 1280×800 | F5 录屏 | 占位 |
| `feature-privacy.webp` | 1280×800 | F6 隐私 | 占位 |
| `platform-macos.png` | 128×128 | 平台标识 | 占位 |

## 5. 技术栈

- **HTML5 + CSS3 + 原生 JS（ES Modules）**，无框架、无构建
- **Canvas 星空动效**：`space-canvas.js`，纯原生，60fps
- **滚动 reveal**：IntersectionObserver
- **响应式**：CSS Grid + Flexbox + `clamp()` 流体字号
- **可访问性**：语义化 HTML + ARIA + 键盘焦点

## 6. 待补充

- [ ] 真实品牌图标（用户提供 PNG/SVG）
- [ ] 真实产品截图（用户提供 .webp）
- [ ] 域名确认（ICP 备案域名）
- [ ] 下载链接（dmg 静态托管地址）
- [ ] 联系信息（小红书 / 抖音 / QQ 群）
- [ ] 备案号（ICP 备案后回填到 Footer）

## 7. 版本历史

| 版本 | 日期 | 内容 |
|---|---|---|
| v0.1 | 2026-09-02 | 初版框架（占位图、占位文案） |
