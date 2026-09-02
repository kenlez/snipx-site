/* snipX-site · 星空背景 canvas
 * 轻量级：仅生成静态星点 + 慢速闪烁，避免重渲染。
 * 遵循 prefers-reduced-motion。
 */
(function () {
  "use strict";

  const canvas = document.getElementById("space-canvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const reduceMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  let width = 0;
  let height = 0;
  let dpr = 1;
  let stars = [];
  let rafId = null;

  function randomBetween(min, max) {
    return min + Math.random() * (max - min);
  }

  function generateStars() {
    const area = width * height;
    const density = area / 3800;
    const count = Math.max(120, Math.min(420, Math.floor(density)));

    stars = new Array(count).fill(0).map(() => {
      const radius = randomBetween(0.4, 1.6);
      return {
        x: Math.random() * width,
        y: Math.random() * height,
        radius,
        baseAlpha: randomBetween(0.25, 0.85),
        twinkleSpeed: randomBetween(0.6, 1.8),
        twinklePhase: Math.random() * Math.PI * 2,
        hue:
          Math.random() < 0.18
            ? ["180, 220, 255", "255, 220, 240", "200, 255, 240"][
                Math.floor(Math.random() * 3)
              ]
            : "255, 255, 255",
      };
    });
  }

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    canvas.style.width = width + "px";
    canvas.style.height = height + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    generateStars();
  }

  let lastTime = 0;

  function render(time) {
    const elapsed = (time - lastTime) / 1000;
    lastTime = time;

    ctx.clearRect(0, 0, width, height);

    for (let i = 0; i < stars.length; i++) {
      const s = stars[i];
      let alpha = s.baseAlpha;

      if (!reduceMotion) {
        const twinkle =
          0.5 + 0.5 * Math.sin(time * 0.001 * s.twinkleSpeed + s.twinklePhase);
        alpha = s.baseAlpha * (0.55 + twinkle * 0.45);
      }

      ctx.beginPath();
      ctx.fillStyle = `rgba(${s.hue}, ${alpha})`;
      ctx.arc(s.x, s.y, s.radius, 0, Math.PI * 2);
      ctx.fill();

      if (s.radius > 1.2 && !reduceMotion) {
        const glow = ctx.createRadialGradient(
          s.x,
          s.y,
          0,
          s.x,
          s.y,
          s.radius * 6
        );
        glow.addColorStop(0, `rgba(${s.hue}, ${alpha * 0.4})`);
        glow.addColorStop(1, `rgba(${s.hue}, 0)`);
        ctx.fillStyle = glow;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.radius * 6, 0, Math.PI * 2);
        ctx.fill();
      }

      if (reduceMotion) {
        s.y += elapsed * 0;
      } else {
        s.y += elapsed * 4;
        if (s.y > height + 4) {
          s.y = -4;
          s.x = Math.random() * width;
        }
      }
    }

    rafId = requestAnimationFrame(render);
  }

  function start() {
    lastTime = performance.now();
    rafId = requestAnimationFrame(render);
  }

  function stop() {
    if (rafId !== null) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }
  }

  let resizeTimer = null;
  window.addEventListener(
    "resize",
    () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(resize, 120);
    },
    { passive: true }
  );

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      stop();
    } else {
      start();
    }
  });

  resize();
  start();
})();
