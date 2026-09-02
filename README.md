# snipX-site

snipX 官方产品介绍站点（独立静态站点）。

## 快速开始

```bash
python3 -m http.server 8080
# 浏览器打开 http://localhost:8080
```

## 目录结构

```
snipX-site/
├── index.html                # 站点入口（产品主页）
├── assets/
│   ├── css/
│   │   ├── styles.css         # 主样式
│   │   └── i18n.css           # i18n 文本尺寸补偿
│   ├── js/
│   │   ├── site.js            # 主脚本
│   │   ├── space-canvas.js    # 星空背景动画
│   │   └── i18n.js            # 语言切换
│   ├── images/
│   │   ├── brand/             # 品牌资源（logo、favicon）
│   │   ├── products/          # 产品截图（占位）
│   │   ├── screenshots/       # 功能截图（占位）
│   │   ├── platforms/         # 平台图标（macOS 等）
│   │   └── placeholder/       # 占位图源
│   └── ...
├── docs/                     # 项目文档
│   ├── PRODUCT-SITE-PRD.md   # 产品官网 PRD
│   └── DEPLOY-CLOUDFLARE.md  # Cloudflare Pages 部署文档
└── README.md
```

## 设计参考

参考 `fg.vkr.me/mac` 的风格：
- 深色太空主题（`#050505` 主背景 + 径向渐变蓝紫光晕）
- 玻璃拟态（毛玻璃）面板
- 大圆角（22px）
- 星空 canvas 动效
- 字体：Inter + PingFang SC

## 部署

- 备案期临时方案：Cloudflare Pages（详见 `docs/DEPLOY-CLOUDFLARE.md`）
- 备案后正式方案：腾讯云 CloudBase 静态托管（详见 `docs/DEPLOY-TENCENT.md`，待补充）
