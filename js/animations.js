// ============================================================
// Движок анимаций (стиль family.co).
// - IntersectionObserver: вход секций и reveal-элементов по скроллу
//   (для hero, который над сгибом, срабатывает сразу на загрузке).
// - Длина SVG-путей для прорисовки линий.
// - Stagger-задержки декора через CSS-переменную --deco-delay.
// Всё пассивно, без layout-трешинга: работаем только с классами/переменными.
// ============================================================
(function () {
  "use strict";

  // --- 1. Длина путей для прорисовки линий/стрелок ---
  document.querySelectorAll(".deco--draw path").forEach(function (p) {
    try {
      p.style.setProperty("--len", p.getTotalLength());
    } catch (e) {}
  });

  // --- 2. Stagger-задержки декора (--deco-delay) ---
  function stagger(selector, step, base) {
    document.querySelectorAll(selector).forEach(function (el, i) {
      el.style.setProperty("--deco-delay", base + i * step + "ms");
    });
  }
  stagger(".deco--blob", 60, 0); // фон появляется первым
  stagger(".deco--float", 55, 150);
  stagger(".deco--twinkle", 70, 450);
  document.querySelectorAll(".deco--draw").forEach(function (el, i) {
    el.style.setProperty("--deco-delay", 700 + i * 200 + "ms");
  });
  // курсор всплывает уже после того, как дорисовался завиток (line5)
  var cursor = document.querySelector(".deco--cursor");
  if (cursor) cursor.style.setProperty("--deco-delay", "1500ms");

  // --- 3. Stagger для reveal-контента ---
  document.querySelectorAll("[data-stagger]").forEach(function (group) {
    group.querySelectorAll(".reveal").forEach(function (el, i) {
      if (!el.dataset.delay) el.dataset.delay = i * 90;
    });
  });

  // --- 4. Вход секций (декор, аватар, прорисовка) ---
  var sectionIO = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add("is-visible");
        sectionIO.unobserve(e.target);
      });
    },
    /* блоки «оживают» чуть раньше входа в вьюпорт */
    { threshold: 0.1, rootMargin: "0px 0px 6% 0px" }
  );
  document.querySelectorAll("[data-animate]").forEach(function (s) {
    sectionIO.observe(s);
  });

  // --- 5. Reveal отдельных элементов по скроллу ---
  var revealIO = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var el = e.target;
        el.style.setProperty("--reveal-delay", (el.dataset.delay || 0) + "ms");
        el.classList.add("is-visible");
        el.addEventListener(
          "transitionend",
          function () {
            el.style.willChange = "auto";
          },
          { once: true }
        );
        revealIO.unobserve(el);
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -3% 0px" }
  );
  document.querySelectorAll(".reveal").forEach(function (el) {
    revealIO.observe(el);
  });
})();
