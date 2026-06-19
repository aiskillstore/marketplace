(function () {
      var buttons = Array.prototype.slice.call(document.querySelectorAll("[data-set-lang]"));
      var navLinks = Array.prototype.slice.call(document.querySelectorAll(".report-nav a"));
      var sections = navLinks
        .map(function (link) { return document.querySelector(link.getAttribute("href")); })
        .filter(Boolean);
      var progressBar = document.querySelector(".progress-bar");
      function setLanguage(lang) {
        document.body.setAttribute("data-report-lang", lang);
        document.documentElement.setAttribute("lang", lang);
        buttons.forEach(function (button) {
          button.setAttribute("aria-pressed", button.getAttribute("data-set-lang") === lang ? "true" : "false");
        });
      }
      function updateProgress() {
        var scrollTop = window.scrollY || document.documentElement.scrollTop;
        var height = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
        var pct = Math.min(100, Math.max(0, (scrollTop / height) * 100));
        if (progressBar) progressBar.style.transform = "scaleX(" + pct / 100 + ")";
        var active = sections[0];
        sections.forEach(function (section) {
          if (section.getBoundingClientRect().top <= 110) active = section;
        });
        navLinks.forEach(function (link) {
          link.setAttribute("aria-current", link.getAttribute("href") === "#" + active.id ? "true" : "false");
        });
      }
      buttons.forEach(function (button) {
        button.addEventListener("click", function () {
          setLanguage(button.getAttribute("data-set-lang"));
        });
      });
      window.addEventListener("scroll", updateProgress, { passive: true });
      window.addEventListener("resize", updateProgress);
      setLanguage("zh-CN");
      updateProgress();
    })();
