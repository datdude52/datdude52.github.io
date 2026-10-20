// ARC-001 scan: drag the angle and read what each sensor saw there.
// The page is complete without this file; it only reveals the slider and moves the beam.
// The sentence mirrors scan_sentence() in scripts/build.py.
(function () {
  var MAX = 700;
  document.querySelectorAll("[data-scan]").forEach(function (fig) {
    var angles = JSON.parse(fig.querySelector(".scan__data").textContent);
    var controls = fig.querySelector(".scan__controls");
    var input = controls.querySelector("input");
    var out = controls.querySelector("output");
    var beam = fig.querySelector(".scan__beam");
    var marks = {
      ray: beam.querySelector(".scan__truth"),
      us: beam.querySelector(".scan__hit--us"),
      tof: beam.querySelector(".scan__hit--tof")
    };
    var readout = fig.querySelector(".scan__readout");

    function read(v, name) {
      return v !== null ? "the " + name + " sensor read " + v + " mm" : "the " + name + " sensor had no return";
    }
    function sentence(a) {
      var s = "At " + Math.round(a.deg) + "°, " + read(a.tof, "time-of-flight") + " and " + read(a.us, "ultrasonic") + ". ";
      if (a.ray !== null) {
        s += "The object on the beam's center line is " + a.ray + " mm away";
        s += a.cone !== null ? ", and the nearest surface inside the ultrasonic beam is " + a.cone + " mm away." : ".";
      } else if (a.cone !== null) {
        s += "No object sits on the beam's center line. The nearest surface inside the ultrasonic beam is " + a.cone + " mm away.";
      }
      return s;
    }
    function place(el, v) {
      var shown = v !== null && v <= MAX;
      el.toggleAttribute("hidden", !shown);
      if (shown) el.setAttribute("cx", v);
    }
    function update() {
      var a = angles[+input.value];
      beam.setAttribute("transform", "rotate(" + -a.deg + ")");
      Object.keys(marks).forEach(function (k) { place(marks[k], a[k]); });
      out.textContent = Math.round(a.deg) + "°";
      readout.textContent = sentence(a);
    }
    input.addEventListener("input", update);
    controls.hidden = false;
  });
})();
