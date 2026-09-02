# Cloudflare Pages 部署指南（备案期临时方案）

> 适用：snipX-site 静态站点
> 特点：**免备案、即开即用、无限流量、全球 CDN**，对国内访问延迟约 100–300ms（够用）

## 1. 准备

需要：
- GitHub 账号
- Cloudflare 账号（免费）
- snipX-site 代码已推送到 GitHub 仓库

## 2. 推送代码到 GitHub

```bash
cd /Users/brad/Documents/snipX-site
git add -A
git commit -m "feat: 初始化 snipX 官网骨架（占位图、占位文案）"
gh repo create snipX-site --public --source=. --remote=origin --push
```

如果用 HTTPS 推送：

```bash
git remote add origin git@github.com:<你的用户名>/snipX-site.git
git push -u origin main
```

## 3. 在 Cloudflare 创建 Pages 项目

1. 登录 https://dash.cloudflare.com/
2. 左侧菜单 → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**
3. 选择 GitHub 仓库 `snipX-site`
4. **Build settings**：
   - Framework preset: **None**
   - Build command: *（留空）*
   - Build output directory: **/** （项目根目录就是产物）
   - Root directory: *（留空）*

> ⚠️ 关键：因为站点是纯静态 HTML，无需构建，输出目录直接指向仓库根目录。

5. 点 **Save and Deploy**，等待 1–2 分钟。

## 4. 配置自定义域名（备案后或临时子域名）

### 4.1 临时子域名
Cloudflare Pages 自动分配 `snipX-site.pages.dev`，立即可访问。

### 4.2 绑定自有域名（DNS 走 Cloudflare）
1. Cloudflare Pages → 项目 → **Custom domains** → **Set up a custom domain**
2. 输入 `www.snipx.app` 或 `snipx.app`
3. Cloudflare 会提示添加 CNAME 记录
4. 到域名注册商（腾讯云 DNSPod / Cloudflare Registrar）添加记录：
   - 主机记录：`www` 或 `@`
   - 记录类型：`CNAME`
   - 记录值：`<project-name>.pages.dev`
   - TTL：自动

> ⚠️ 如果域名在腾讯云 DNSPod，**先用 Cloudflare 接管 DNS**（添加站点 → 修改 NS 记录指向 Cloudflare 分配的 NS），再在 Cloudflare 里加 CNAME。

### 4.3 绑定自有域名（DNS 留腾讯云）
如果你不想让 Cloudflare 接管 DNS，只在腾讯云 DNSPod 操作：
1. 在 Cloudflare Pages 添加自定义域名，按提示得到目标地址（如 `<project>.pages.dev`）
2. 到腾讯云 DNSPod 控制台添加 CNAME：`www` → `<project>.pages.dev`
3. ⚠️ **国内备案**：腾讯云 DNSPod 添加 CNAME 时若使用国内解析线路，**仍需域名已完成 ICP 备案**。否则只能用境外解析（默认境外线路），访问可能不稳定。

## 5. 备案后切回腾讯云 CloudBase（可选）

备案完成后，参考 `DEPLOY-TENCENT.md`（待补充），把 CNAME 从 Cloudflare Pages 改到腾讯云 CloudBase 静态托管。

切换步骤：
1. 腾讯云 CloudBase 开通静态托管，上传 `snipX-site/` 内容
2. CloudBase 分配默认域名 `xxx.tcloudbaseapp.com`
3. 腾讯云 DNSPod 把 CNAME 从 `<project>.pages.dev` 改为 CloudBase 分配的 CNAME
4. Cloudflare Pages 项目保留（不回退），方便后续回滚

## 6. 验证清单

- [ ] 访问 `https://<project-name>.pages.dev`，页面正常渲染
- [ ] 星空 canvas 动效流畅
- [ ] TopBar 滚动收缩正常
- [ ] 6 个 Feature 区块交替布局
- [ ] 占位图正常显示（边框 + 渐变 + 标签）
- [ ] Install 步骤卡 hover 正常
- [ ] Footer 链接锚点跳转正常
- [ ] 移动端（< 720px）响应式正常
- [ ] Lighthouse 性能 ≥ 90

## 7. 常见问题

**Q: Cloudflare Pages 国内访问速度？**
A: 平均 100–300ms，可用 https://www.webpagetest.org/ 自测。备案后切回腾讯云 CloudBase，国内延迟可降到 30–80ms。

**Q: 是否会被 Cloudflare 审查内容？**
A: 不会。Cloudflare Pages 只托管静态文件，不审查内容。

**Q: 自定义域名必须备案吗？**
A: 如果你的域名是 `.cn` 或服务器在国内，**必须 ICP 备案**。`.com / .app / .io` 等境外注册域名可以免备案走 Cloudflare，但若有国内访问需求建议备案。

**Q: 是否收费？**
A: Cloudflare Pages 免费计划：
- 无限请求
- 无限带宽
- 每月 500 次构建
- 最多 100 个项目
对 snipX 站点完全够用。
