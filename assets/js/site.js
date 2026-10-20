// Looping clips on the home sheet play muted. With reduced motion they stay on their poster frame.
(function () {
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  function apply() {
    document.querySelectorAll("video[data-loop]").forEach(function (v) {
      if (reduce.matches) { v.pause(); }
      else { v.play().catch(function () {}); }
    });
  }
  apply();
  reduce.addEventListener("change", apply);
})();
