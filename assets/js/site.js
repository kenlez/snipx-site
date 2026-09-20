/* SnipX-site · 主脚本
 * - TopBar 滚动时变高变小 + 加毛玻璃
 * - IntersectionObserver reveal 动效
 * - 平滑锚点跳转（处理 sticky topbar 偏移）
 * - 主题切换（跟随系统 / 浅色 / 深色）
 */
(function () {
  "use strict";

  const topbar = document.getElementById("topbar");
  const STICK_THRESHOLD = 32;

  function onScroll() {
    if (!topbar) return;
    if (window.scrollY > STICK_THRESHOLD) {
      topbar.classList.add("is-stuck");
    } else {
      topbar.classList.remove("is-stuck");
    }
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- 平滑锚点跳转（含 topbar 偏移） ---------- */
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener("click", (e) => {
      const href = a.getAttribute("href");
      if (!href || href === "#") return;
      const target = document.querySelector(href);
      if (!target) return;
      e.preventDefault();
      const topbarH = topbar
        ? topbar.getBoundingClientRect().height
        : 0;
      const y =
        target.getBoundingClientRect().top + window.scrollY - topbarH - 12;
      window.scrollTo({ top: y, behavior: "smooth" });
      history.replaceState(null, "", href);
    });
  });

  /* ---------- Reveal 动效 ---------- */
  const revealTargets = document.querySelectorAll(
    ".hero-copy, .hero-visual, .section-head, .feature-row, .install-step, .about-card"
  );

  revealTargets.forEach((el) => el.classList.add("reveal"));

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
    );

    revealTargets.forEach((el) => observer.observe(el));
  } else {
    revealTargets.forEach((el) => el.classList.add("is-visible"));
  }

  /* ---------- 占位图点击：复制文件名到剪贴板（便于替换） ---------- */
  document.querySelectorAll(".ph-image").forEach((el) => {
    const label = el.getAttribute("data-label");
    if (!label) return;
    el.addEventListener("click", () => {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(label).catch(() => {});
      }
    });
    el.style.cursor = "copy";
    el.title = "点击复制文件名：" + label;
  });

  /* ---------- 主题切换（system / light / dark 三态循环） ---------- */
  const THEME_KEY = "snipx-theme";
  const THEME_ICONS = { system: "◐", light: "☀", dark: "☾" };
  const THEME_LABELS = {
    system: "主题：跟随系统",
    light: "主题：浅色",
    dark: "主题：深色",
  };
  const THEME_CYCLE = { system: "light", light: "dark", dark: "system" };

  function getStoredTheme() {
    try {
      return localStorage.getItem(THEME_KEY) || "system";
    } catch (e) {
      return "system";
    }
  }

  function applyTheme(mode) {
    const resolved =
      mode === "system"
        ? (window.matchMedia("(prefers-color-scheme: light)").matches
            ? "light"
            : "dark")
        : mode;
    document.documentElement.setAttribute("data-theme", resolved);
    document.documentElement.setAttribute("data-theme-mode", mode);

    /* 同步 meta theme-color（Safari / Chrome 地址栏配色） */
    const mc = document.querySelector('meta[name="theme-color"]');
    if (mc) {
      mc.setAttribute("content", resolved === "light" ? "#f5f5f0" : "#050505");
    }

    const btn = document.querySelector(".theme-toggle");
    if (!btn) return;
    btn.setAttribute("data-mode", mode);
    btn.setAttribute("title", THEME_LABELS[mode]);
    btn.setAttribute("aria-label", THEME_LABELS[mode]);
    const icon = btn.querySelector(".theme-toggle-icon");
    if (icon) icon.textContent = THEME_ICONS[mode];
  }

  const themeBtn = document.querySelector(".theme-toggle");
  if (themeBtn) {
    applyTheme(getStoredTheme());
    themeBtn.addEventListener("click", () => {
      const current = themeBtn.getAttribute("data-mode") || "system";
      const next = THEME_CYCLE[current] || "system";
      try {
        localStorage.setItem(THEME_KEY, next);
      } catch (e) {}
      applyTheme(next);
    });
  }

  /* 跟随系统模式下，系统主题切换时同步 */
  const mq = window.matchMedia("(prefers-color-scheme: light)");
  const onSystemChange = () => {
    if (getStoredTheme() === "system") applyTheme("system");
  };
  if (mq.addEventListener) mq.addEventListener("change", onSystemChange);
  else if (mq.addListener) mq.addListener(onSystemChange);
})();
