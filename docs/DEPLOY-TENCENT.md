# 腾讯云 CloudBase 静态托管部署指南（备份参考）

> ⚠️ 本项目当前**不需要 ICP 备案**，正式方案为 Cloudflare Pages。本文档仅作未来如需境内加速时的备份参考。
>
> 适用：SnipX-site 静态站点
> 前提：**域名已完成 ICP 备案**
> 免费额度：1GB 存储 + 5GB 流量/月（足够个人产品站）

## 1. 前置条件

- [ ] 已注册腾讯云账号（已完成实名认证）
- [ ] 域名已完成 ICP 备案（工信部 + 腾讯云接入）
- [ ] 已购买备案号（如 `.com` 域名）

## 2. 开通 CloudBase

1. 登录 https://console.cloud.tencent.com/
2. 搜索「云开发 CloudBase」→ 立即开通
3. 选择「按量付费」（静态托管走免费额度，不会扣费）
4. 创建环境：
   - 环境名称：`snipx-prod`
   - 付费方式：按量付费
   - 地域：**上海 / 广州 / 北京**（离你近）
5. 等待环境创建完成（约 1–2 分钟）

## 3. 开通静态网站托管

1. 进入 CloudBase 控制台 → 选中环境 → 左侧「静态网站托管」
2. 点击「开通」
3. 默认分配域名：`snipx-prod-xxxx.tcloudbaseapp.com`
4. 在「基础配置」里：
   - 默认域名：开启
   - 索引文档：`index.html`
   - 错误文档：`404.html`（可选，先占位）

## 4. 上传站点文件

### 4.1 通过 CloudBase 控制台上传（最简单）
1. 静态网站托管 → 「文件管理」
2. 进入根目录 `/`
3. 上传整个 `SnipX-site/` 项目内容：
   - `index.html`
   - `assets/` 整个目录
4. 上传路径直接是根目录 `/`

### 4.2 通过 CLI 上传（推荐，便于自动化）
```bash
npm install -g @cloudbase/cli
cloudbase login
cd /Users/brad/Documents/SnipX-site
cloudbase hosting deploy ./ . -e snipx-prod
```

## 5. 绑定自有域名

1. 静态网站托管 → 「基础配置」→ 「添加域名」
2. 输入 `www.snipx.app` 或 `snipx.app`
3. CloudBase 会要求 DNS 验证：
   - 在腾讯云 DNSPod 添加 CNAME 记录：
     - 主机记录：`www` 或 `@`
     - 记录类型：`CNAME`
     - 记录值：CloudBase 提供的目标地址（如 `xxxx.tcloudbaseapp.com`）
     - TTL：600
4. 等待 DNS 生效（5–30 分钟）
5. CloudBase 控制台自动签发 Let's Encrypt 免费 SSL 证书

## 6. 切换备案期 Cloudflare Pages（可选）

如果之前用 Cloudflare Pages 临时托管，备案完成后：
1. 在 Cloudflare Pages 保留项目，不要删（便于回滚）
2. CloudBase 上传后，把 DNSPod 的 CNAME 从 `<project>.pages.dev` 改为 CloudBase 目标
3. 等待 DNS 生效，旧 Cloudflare Pages 自然失效

## 7. 验证清单

- [ ] 访问 `https://snipx.app`，页面正常
- [ ] HTTPS 证书有效（浏览器锁标志）
- [ ] 星空动效、TopBar 滚动、reveal 全部正常
- [ ] 备案号已填入 Footer
- [ ] 移动端响应式正常
- [ ] Lighthouse 性能 ≥ 90

## 8. 费用

| 项 | 免费额度 | 超出单价 |
|---|---|---|
| 存储 | 1 GB | ¥0.0043/GB/小时 |
| 流量 | 5 GB/月 | ¥0.21/GB |
| 请求 | 5 万次/月 | ¥0.01/万次 |

SnipX 个人产品站预估月流量 < 1GB，**完全免费**。
