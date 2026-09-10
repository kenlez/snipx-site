# SnipX 应用 → 网站 同步锚点

> 本文档是 `SnipX-site` 与 `SnipX` app 仓库之间的**单向同步锚点**。
> 每次新 session 开始时，第一件事读这份文件即可知道网站文案/截图/功能是否需要跟随 app 更新。
>
> 维护时机：**SnipX 发版后**，把变更摘要粘贴到本文档对应版本的小节；同时把网站主页/内页相应更新。

---

## 当前应展示状态

> 以下是 **网站对外文案应反映** 的 SnipX 最新事实。如与 `../SnipX/README.md`、`../SnipX/RELEASE-NOTES.md` 不一致，以本文档为准（本文档是网站真值源，app 仓库是代码真值源）。

| 字段 | 当前值 |
|---|---|
| 产品名 | **SnipX**（首字母大写） |
| 当前版本 | **1.0.0** |
| 系统要求 | **macOS 14.0+**（Sonoma 及以上） |
| 架构 | **Universal 2**：arm64 + x86_64（Apple Silicon + Intel） |
| 体积 | 仅 3 MB |
| 价格模型 | 基础截屏永久免费；SnipX Pro ¥12 一次性买断（首发优惠 ¥6） |
| 内购解锁范围 | MP4 录屏（区域 / 窗口 / 显示器）、GIF 录制、声音录制、摄像头画中画、异常恢复、头尾裁剪导出 |
| Bundle ID | `com.brad.SnipX` |
| 内购产品 ID | `com.brad.SnipX.pro.unlock` |
| 客服邮箱 | `snipx@tongkun.top` |
| 隐私政策 URL | https://snipx.tongkun.top/privacy.html |
| 支持 URL | https://snipx.tongkun.top/support.html |
| 营销 URL | https://snipx.tongkun.top/ |
| 营销域名 | https://snipx.tongkun.top（Cloudflare Pages 托管，长期方案） |
| 备用托管 | https://snipx-site.pages.dev |

---

## 已上网站版本（SnipX 发布说明对照）

| SnipX 版本 | 网站版本 | 上线日期 | 关键更新 | 状态 |
|---|---|---|---|---|
| 1.0.0 | v0.3 | 2026-09-10 | App Store 上架版本；接入真实图片（hero + feature 截图 + 图标）、移除 ICP 备案占位、版本号 0.1.99 → 1.0.0 | ⏳ 本次 |
| 0.1.99 | v0.2 | 2026-09-05 | OCR MVP（本地 Vision 框架）+ Universal 2（arm64 + x86_64）+ SnipX Pro 付费墙 + 隐私政策/支持页 | ✅ 本次 PR |
| 0.1.86 | v0.1 | 2026-09-02 | 初版框架（占位图、占位文案） | ✅ |

---

## 0.1.99 → 网站文案要点

### Hero 区
- 标题：`SnipX`
- 副标题：`Mac 截屏与录屏，一触即达`
- 描述要点：
  - 原生 AppKit + Swift + ScreenCaptureKit
  - 物理像素输出
  - **本地 OCR**（1.0.0 新增）
  - 可编辑快捷键
  - 长截图拼接
  - 本地 MP4 录制
  - 零网络、零账号、零上传
- Hero tags：`macOS 14+` / `Universal 2 · Apple Silicon + Intel` / `本地 OCR` / `SnipX Pro 录屏/GIF`

### Features 区
- F1 菜单栏常驻
- F2 可编辑快捷键
- F3 四类截屏（区域 / 窗口 / 全屏 / 长截图）
- **F4 本地 OCR（新增）** — Vision 框架、中英混排、完全本地
- F5 标注工具
- F6 MP4 录屏（标注 SnipX Pro、说明系统声+麦克风、Recovery）
- F7 零数据外传

### Install 区
- 分发渠道：**Mac App Store**（不再提供 .dmg 直装；App Store 版内购走 Apple IAP）
- 下载按钮：`#appstore-download` 为占位（`href="#"`、`data-appstore-url=""`），待 App Store 应用页上线后回填
- 系统要求：`macOS 14+ · Universal 2（Apple Silicon + Intel）· 仅 3 MB`
- 附注：`基础截屏永久免费 · 录屏与 GIF 录制需 SnipX Pro（¥12 / 首发 ¥6）`

### About 区
- 原生开发
- 隐私优先（含 `privacy.html` 链接）
- **SnipX Pro（新增卡片）**
- 持续维护（含 `support.html` 链接、版本号 1.0.0）

### Footer
- 增加：`支持` / `隐私政策` 内链
- 版本号：1.0.0

### Meta
- `og:image`: `assets/brand/icon-snipx.png`（占位）
- description 含 OCR + Universal 2

---

## 待 app 端核实（每次 PR 前对照 `SnipX/RELEASE-NOTES.md`）

- [ ] 是否新增了录屏相关功能（影响 Pro 卡片）
- [ ] 是否新增了 OCR/标注/快捷键（影响 Features 区）
- [ ] 是否新增了系统权限（影响 Support 页权限引导 + Privacy Policy）
- [ ] 内购价格 / 优惠是否变动（影响 Install + About + Support FAQ）
- [ ] Bundle ID / 内购产品 ID 是否变动（影响 Support 页元数据表）
- [ ] OCR 支持语言是否扩展（影响 Features + Support FAQ）

---

## 待办

- [ ] 联系信息（小红书 / 抖音 / QQ 群）补全到 footer
- [ ] 真实品牌图标（用户提供 PNG/SVG）
- [x] 真实产品截图（已接入 `assets/screenshots/`：`hero.jpg` + `feature-*.webp`）
- [ ] App Store 审核通过后：回填 `index.html` 的 `#appstore-download`（`href` + `data-appstore-url`），移除 `.install-pending` 占位提示，并把营销 URL 切换为 App Store 应用页
