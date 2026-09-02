/* snipX-site · 主脚本
 * - TopBar 滚动时变高变小 + 加毛玻璃
 * - IntersectionObserver reveal 动效
 * - 平滑锚点跳转（处理 sticky topbar 偏移）
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
})();
