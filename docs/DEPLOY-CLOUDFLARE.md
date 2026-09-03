# Cloudflare Pages 部署指南（备案期临时方案）

> 适用：SnipX-site 静态站点
> 特点：**免备案、即开即用、无限流量、全球 CDN**，对国内访问延迟约 100–300ms（够用）

## 1. 准备

需要：
- GitHub 账号
- Cloudflare 账号（免费）
- Cloudflare API Token（权限：Account → Cloudflare Pages → Edit）
- Node.js 18+（用于 wrangler CLI）

## 2. 推送代码到 GitHub

```bash
cd /Users/brad/Documents/SnipX-site
git add -A
git commit -m "feat: 初始化 SnipX 官网骨架（占位图、占位文案）"
gh repo create SnipX-site --public --source=. --remote=origin --push
```

> ⚠️ GitHub 上传后建议进入 Settings → Pages → **关闭** GitHub Pages 避免冲突（我们用 Cloudflare Pages 托管）。

## 3. 创建 Cloudflare Pages 项目

### 方式 A：Dashboard 手动创建 + Git 集成（推荐用于长期维护）

1. 登录 https://dash.cloudflare.com/
2. 左侧菜单 → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**
3. 选择 GitHub 仓库 `SnipX-site`
4. **Build settings**：
   - Framework preset: **None**
   - Build command: *（留空）*
   - Build output directory: **/** （项目根目录就是产物）
   - Root directory: *（留空）*
5. 点 **Save and Deploy**

之后 `git push` 自动触发部署。

### 方式 B：Dashboard 手动创建 + Direct Upload（适合一次性部署）

1. 左侧菜单 → **Workers & Pages** → **Create** → **Pages** → **Drag and drop**
2. 输入项目名 `SnipX-site`
3. 将整个 `SnipX-site/` 目录拖入（或打包 zip 拖入）
4. 点 **Deploy site**

### 方式 C：API + wrangler CLI（已验证，可完全脚本化）

> 本项目首次部署采用此方式。GitHub 集成失败时（如 GitHub App 未授权），这是最佳替代。

#### 3.1 创建 API Token
参考主项目 README "获取 API Token" 章节，最小权限：**Account → Cloudflare Pages → Edit**。

#### 3.2 创建项目

```bash
curl -X POST \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/pages/projects" \
  -d '{"name": "snipx-site", "production_branch": "main"}'
```

#### 3.3 用 wrangler CLI 部署

```bash
cd /Users/brad/Documents/SnipX-site
CLOUDFLARE_API_TOKEN="$CF_TOKEN" \
CLOUDFLARE_ACCOUNT_ID="$CF_ACCOUNT_ID" \
npx --yes wrangler@latest pages deploy . \
  --project-name=snipx-site \
  --branch=main
```

> ⚠️ 不要尝试自己拼接 manifest + zip 上传：CF Pages 边缘节点会校验文件 SHA-256，手动构建 manifest 经常返回 500。wrangler CLI 会自动正确处理。

#### 3.4 添加自定义域（API 方式）

```bash
curl -X POST \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/pages/projects/snipx-site/domains" \
  -d '{"name": "snipx.tongkun.top"}'
```

CF Pages 会自动签发 SSL 证书（Let's Encrypt，1–5 分钟）。

## 4. 配置自定义域名

### 4.1 临时子域名
Cloudflare Pages 自动分配 `SnipX-site.pages.dev`，立即可访问。

### 4.2 绑定自有域名（DNS 留腾讯云 DNSPod，本项目当前方案）

1. Cloudflare Pages → 项目 → **Custom domains** → **Set up a custom domain**
2. 输入 `snipx.tongkun.top`
3. CF 会要求 DNS 验证
4. 到 https://console.dnspod.cn 添加 CNAME：
   - 主机记录：`snipx`
   - 记录类型：`CNAME`
   - 记录值：`snipx-site.pages.dev`
   - TTL：600
   - 解析线路：默认
5. 等待 DNS 生效（5–30 分钟）+ CF 签发 SSL 证书（5 分钟）

### 4.3 绑定自有域名（DNS 让 Cloudflare 接管）
1. Cloudflare 添加 `tongkun.top` 站点，自动扫描现有 DNS 记录
2. 在 Cloudflare 把 `snipx.tongkun.top` 添加为 Pages 项目的自定义域
3. 腾讯云 DNSPod 把 NS 记录改为 Cloudflare 分配的 NS

## 5. 部署后配置

### 5.1 每次更新内容

**如果用 Git 集成**：直接 `git push`，Cloudflare 自动部署。

**如果用 wrangler CLI / Direct Upload**：

```bash
cd /Users/brad/Documents/SnipX-site
CLOUDFLARE_API_TOKEN="$CF_TOKEN" \
CLOUDFLARE_ACCOUNT_ID="$CF_ACCOUNT_ID" \
npx wrangler@latest pages deploy . --project-name=snipx-site
```

### 5.2 占位图替换为真实图

1. 把真实图放到 `assets/images/{products,screenshots,brand}/` 对应位置，文件名保持一致（如 `hero.webp`）
2. 重新部署（同上）
3. 浏览器强制刷新（Cmd+Shift+R）查看效果

## 6. 验证清单

- [ ] 访问 `https://snipx-site.pages.dev/`，页面正常渲染
- [ ] 访问 `https://snipx.tongkun.top/`，页面正常渲染
- [ ] 星空 canvas 动效流畅
- [ ] TopBar 滚动收缩正常
- [ ] 6 个 Feature 区块交替布局
- [ ] 占位图正常显示（边框 + 渐变 + 标签）
- [ ] Install 步骤卡 hover 正常
- [ ] Footer 链接锚点跳转正常
- [ ] 移动端（< 720px）响应式正常
- [ ] Lighthouse 性能 ≥ 90

## 7. 常见问题

**Q: 部署后访问返回 500（content-length: 0）？**
A: manifest hash 校验失败。不要手动构造 manifest + zip 上传，直接用 wrangler CLI。

**Q: GitHub 集成时报 "internal issue with your Cloudflare Pages Git installation"？**
A: 首次使用需要先在 Dashboard 安装 GitHub App。也可改用 wrangler CLI（无需 GitHub App）。

**Q: Cloudflare Pages 国内访问速度？**
A: 平均 100–300ms，可用 https://www.webpagetest.org/ 自测。备案后切回腾讯云 CloudBase，国内延迟可降到 30–80ms。

**Q: 是否会被 Cloudflare 审查内容？**
A: 不会。Cloudflare Pages 只托管静态文件，不审查内容。

**Q: 自定义域名必须备案吗？**
A: 如果你的域名是 `.cn` 或服务器在国内，**必须 ICP 备案**。`.com / .app / .io / .top` 等境外注册域名可以免备案走 Cloudflare，但若有国内访问需求建议备案。

**Q: 是否收费？**
A: Cloudflare Pages 免费计划：
- 无限请求
- 无限带宽
- 每月 500 次构建
- 最多 100 个项目

对 SnipX 站点完全够用。

## 8. 本项目实际部署记录（2026-09-02）

- GitHub 仓库：https://github.com/kenlez/snipx-site
- Cloudflare Pages 项目：`snipx-site`
- 临时域名：https://snipx-site.pages.dev
- 自定义域：https://snipx.tongkun.top（active，SSL 已签发）
- DNSPod CNAME：`snipx.tongkun.top → snipx-site.pages.dev`
- 部署方式：API 创建项目 + wrangler CLI 上传 + API 添加自定义域 + DNSPod API 添加 CNAME
