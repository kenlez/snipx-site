# snipX-site 项目约定

snipX 官方产品介绍站点（独立项目，与 `shotX` 应用源码分离）。

## 文档

- 所有任务生成的 Markdown 文档放入 `docs/`。
- 根目录只保留长期入口文档：`README.md`、`AGENTS.md`、`DEPLOY.md`，其他全进 `docs/`。
- 删除或移动文档时同步更新索引与引用；提交前使用 `git add -A`，确认删除也进入提交。

## 技术栈

- 纯静态站点：HTML + CSS + 原生 JS（ES Modules），不依赖任何框架或构建工具。
- 星空动效使用 `<canvas>` + `requestAnimationFrame`。
- 图片懒加载使用 `loading="lazy"` + IntersectionObserver。
- 不引入 npm 依赖、不打包，直接 `index.html` 即可预览。

## 本地预览

```bash
# 任选一种（必须 HTTP 服务，不能 file://）
python3 -m http.server 8080
# 或
npx --yes serve -l 8080 .
```

浏览器打开 http://localhost:8080

## Git 分支与合并

- 不直接在 `main` 上开发。从最新且干净的 `main` 创建短期分支。
- 分支命名：`codex/task-<简短描述>`（无 BRA 编号时）。
- 一个分支只解决一个问题，不夹带无关修改。
- 涉及 UI 视觉或交互、文案、域名、备案、部署的改动，必须在合并前等待用户手测确认。

## 占位图约定

- 所有图片占位存放在 `assets/images/placeholder/`，文件名与真实图一致（如 `hero.webp`、`feature-screenshot.webp`）。
- 占位图为纯 CSS 渐变 + 文字标签，不依赖外部资源。
- 真实图到位后覆盖同名文件即可，无需改 HTML/CSS。
- 占位图清单见 `docs/PRODUCT-SITE-PRD.md`。
