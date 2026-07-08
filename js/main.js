// ============================================================
// Раньше здесь жило масштабирование hero-холста через transform:scale.
// Теперь вёрстка текучая: на десктопе всё выражено через CSS-единицу
// --u = 100vw/1920 (см. hero.css), на мобилке — vw/clamp + медиазапрос.
// JS для раскладки больше не нужен. Анимации — в js/animations.js.
// ============================================================

// --- Мобильное меню: открытие бургером, закрытие по клику мимо/по ссылке ---
(function () {
  "use strict";
  var burger = document.querySelector(".header__burger");
  var backdrop = document.querySelector(".menu-backdrop");
  var menu = document.getElementById("mobile-menu");
  if (!burger || !menu) return;

  function setOpen(open) {
    var body = document.body;
    if (!open && body.classList.contains("menu-open")) {
      // проигрываем «жидкое» сворачивание, потом прячем
      body.classList.remove("menu-open");
      body.classList.add("menu-closing");
      var done = function () {
        body.classList.remove("menu-closing");
        menu.removeEventListener("animationend", done);
      };
      menu.addEventListener("animationend", done);
    } else if (open) {
      body.classList.remove("menu-closing");
      body.classList.add("menu-open");
    }
    burger.setAttribute("aria-expanded", open ? "true" : "false");
    burger.setAttribute("aria-label", open ? "Закрыть меню" : "Открыть меню");
  }
  burger.addEventListener("click", function () {
    setOpen(!document.body.classList.contains("menu-open"));
  });
  backdrop.addEventListener("click", function () { setOpen(false); });
  menu.addEventListener("click", function (e) {
    if (e.target.tagName === "A") setOpen(false);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") setOpen(false);
  });
})();

// --- Полный запрет масштабирования страницы ---
(function () {
  "use strict";
  // пинч-зум в Safari (iOS/iPadOS), где user-scalable=no игнорируется
  ["gesturestart", "gesturechange", "gestureend"].forEach(function (ev) {
    document.addEventListener(ev, function (e) { e.preventDefault(); }, { passive: false });
  });
  // Ctrl/Cmd + колесо мыши (десктоп)
  document.addEventListener("wheel", function (e) {
    if (e.ctrlKey || e.metaKey) e.preventDefault();
  }, { passive: false });
  // Ctrl/Cmd + «+» / «-» / «0»
  document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && ["+", "-", "=", "0"].indexOf(e.key) !== -1) {
      e.preventDefault();
    }
  });
  // двойной тап для зума на мобилке
  var lastTouch = 0;
  document.addEventListener("touchend", function (e) {
    var now = Date.now();
    if (now - lastTouch <= 300) e.preventDefault();
    lastTouch = now;
  }, { passive: false });
})();
