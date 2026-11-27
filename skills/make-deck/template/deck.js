(function () {
  "use strict";
  var STEPS = new Map([["ArrowRight", 1], ["ArrowDown", 1], ["PageDown", 1], [" ", 1], ["ArrowLeft", -1], ["ArrowUp", -1], ["PageUp", -1]]);
  var stage = document.getElementById("stage");
  var hint = document.getElementById("hint");
  var slides = Array.prototype.slice.call(stage.querySelectorAll(".slide:not(.print-only)"));
  var current = 0;
  var touchStartX = null;

  function fit() {
    var scale = Math.min(window.innerWidth / 1280, window.innerHeight / 720);
    stage.style.setProperty("--scale", String(scale));
  }

  function show(index) {
    if (slides.length === 0) return;
    current = Math.max(0, Math.min(slides.length - 1, index));
    slides.forEach(function (slide, i) {
      slide.classList.toggle("is-current", i === current);
    });
    hint.textContent = (current + 1) + " / " + slides.length;
  }

  function selectTab(slide, index) {
    if (!slide) return;
    slide.querySelectorAll("[role='tab']").forEach(function (button) {
      button.setAttribute("aria-selected", String(Number(button.dataset.tab) === index));
    });
    slide.querySelectorAll(".tab-panel").forEach(function (panel) {
      panel.classList.toggle("is-active", Number(panel.dataset.panel) === index);
    });
  }

  document.addEventListener("keydown", function (event) {
    if (event.metaKey || event.ctrlKey || event.altKey) return;
    var step = STEPS.get(event.key);
    if (step) {
      event.preventDefault();
      show(current + step);
      return;
    }
    if (/^[1-9]$/.test(event.key)) {
      var slide = slides[current];
      var index = Number(event.key) - 1;
      if (slide && index < slide.querySelectorAll("[role='tab']").length) {
        selectTab(slide, index);
      }
    }
  });

  document.addEventListener("click", function (event) {
    var button = event.target.closest ? event.target.closest("[role='tab']") : null;
    if (button) selectTab(button.closest(".slide"), Number(button.dataset.tab));
  });

  document.addEventListener("touchstart", function (event) {
    touchStartX = event.touches[0].clientX;
  }, { passive: true });

  document.addEventListener("touchend", function (event) {
    if (touchStartX === null) return;
    var dx = event.changedTouches[0].clientX - touchStartX;
    touchStartX = null;
    if (Math.abs(dx) >= 40) show(current + (dx < 0 ? 1 : -1));
  });

  window.addEventListener("resize", fit);
  fit();
  show(0);
})();
