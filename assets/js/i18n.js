/* SnipX-site · 多语言切换器
 * - 自动从 URL 路径 /<lang>/... 推断当前语言
 * - 渲染 topbar 的语言下拉菜单，跳转时保持当前页（index/privacy/support）
 * - 持久化用户语言偏好到 localStorage.snipx-lang（仅当用户主动切换时）
 */
(function () {
  "use strict";

  const LANGS = [
    { code: "zh-CN", label: "中文（简体）", short: "中文" },
    { code: "zh-TW", label: "中文（繁體）", short: "繁體中文" },
    { code: "en", label: "English", short: "English" },
    { code: "ja", label: "日本語", short: "日本語" },
    { code: "ko", label: "한국어", short: "한국어" },
    { code: "es", label: "Español", short: "Español" },
    { code: "pt", label: "Português", short: "Português" },
  ];
  const LANG_CODES = LANGS.map((l) => l.code);

  function detectLangFromPath() {
    var m = window.location.pathname.match(/^\/([a-z]{2}(?:-[A-Z]{2})?)\//);
    return m ? m[1] : null;
  }

  function detectPageFromPath() {
    var p = window.location.pathname;
    if (/\/privacy\.html$/.test(p)) return "privacy";
    if (/\/support\.html$/.test(p)) return "support";
    return "index";
  }

  function closeMenu(toggle, menu) {
    if (!toggle || !menu) return;
    toggle.setAttribute("aria-expanded", "false");
    menu.hidden = true;
  }

  function toggleMenu(toggle, menu) {
    var open = toggle.getAttribute("aria-expanded") === "true";
    if (open) closeMenu(toggle, menu);
    else {
      toggle.setAttribute("aria-expanded", "true");
      menu.hidden = false;
    }
  }

  function buildSwitcher(currentLang, currentPage) {
    var switcher = document.querySelector(".lang-switcher");
    if (!switcher) return;
    switcher.setAttribute("data-current", currentLang || "");

    var lang = LANGS.find((l) => l.code === currentLang) || LANGS[0];

    var labelEl = switcher.querySelector(".lang-switcher-label");
    if (labelEl) labelEl.textContent = lang.short;

    var menu = switcher.querySelector(".lang-switcher-menu");
    if (menu) {
      menu.innerHTML = LANGS.map(function (l) {
        var href = "/" + l.code + "/" + currentPage + ".html";
        var active = l.code === currentLang ? " aria-selected=\"true\"" : "";
        return (
          "<li role=\"option\">" +
          "<a href=\"" + href + "\" data-lang=\"" + l.code + "\"" + active + ">" +
          l.label +
          "</a></li>"
        );
      }).join("");
    }

    var toggle = switcher.querySelector(".lang-switcher-toggle");
    if (toggle) {
      toggle.addEventListener("click", function (e) {
        e.stopPropagation();
        toggleMenu(toggle, menu);
      });

      /* 持久化用户主动切换：点 a 链接时写 localStorage */
      if (menu) {
        menu.addEventListener("click", function (e) {
          var a = e.target.closest && e.target.closest("a[data-lang]");
          if (!a) return;
          try {
            localStorage.setItem("snipx-lang", a.getAttribute("data-lang"));
          } catch (_) {}
        });
      }
    }

    /* 点外面或 Esc 关闭 */
    document.addEventListener("click", function (e) {
      if (!switcher.contains(e.target)) closeMenu(toggle, menu);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeMenu(toggle, menu);
    });
  }

  /* 根路径自动判断：读 navigator.language，匹配则跳子目录 */
  function autoRedirectFromRoot() {
    if (window.location.pathname !== "/" && window.location.pathname !== "/index.html") {
      return;
    }
    var stored = null;
    try {
      stored = localStorage.getItem("snipx-lang");
    } catch (_) {}
    var raw = (stored || navigator.language || "en").toLowerCase();
    var matched = LANG_CODES.find(function (code) {
      return raw === code.toLowerCase() || raw.startsWith(code.toLowerCase().split("-")[0] + "-");
    });
    if (matched && matched !== "zh-CN") {
      window.location.replace("/" + matched + "/");
    }
  }

  /* 初始化：先判断是否需要从根跳转，再构建切换器 */
  autoRedirectFromRoot();
  buildSwitcher(detectLangFromPath(), detectPageFromPath());
})();