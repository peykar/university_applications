(() => {
  const debounce = (fn, wait = 180) => {
    let timer;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => fn(...args), wait);
    };
  };

  const buildPicker = (container, dependsOn = null) => {
    const select = container.querySelector("select");
    if (!select || select.dataset.enhanced === "true") return null;
    select.dataset.enhanced = "true";

    const wrapper = document.createElement("div");
    wrapper.className = "single-picker";

    const search = document.createElement("input");
    search.type = "search";
    search.className = "single-picker-search";
    search.autocomplete = "off";
    search.placeholder = select.dataset.placeholder || "Search";

    const panel = document.createElement("div");
    panel.className = "single-picker-options";

    select.classList.add("single-picker-native");
    select.insertAdjacentElement("afterend", wrapper);
    wrapper.append(search, panel);

    const setDisabled = (disabled) => {
      search.disabled = disabled;
      if (disabled) {
        search.value = "";
        select.replaceChildren();
        panel.replaceChildren();
        panel.classList.remove("is-open");
      }
    };

    const render = (results) => {
      panel.replaceChildren();
      if (!results.length) {
        const empty = document.createElement("div");
        empty.className = "single-picker-empty";
        empty.textContent = "No matching options";
        panel.append(empty);
        return;
      }
      results.forEach((result) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "single-picker-option";
        button.textContent = result.label;
        button.addEventListener("click", () => {
          select.replaceChildren(new Option(result.label, result.id, true, true));
          search.value = result.label;
          panel.classList.remove("is-open");
          select.dispatchEvent(new Event("change", { bubbles: true }));
        });
        panel.append(button);
      });
    };

    const fetchOptions = debounce(async () => {
      const url = new URL(container.dataset.searchUrl, window.location.origin);
      if (dependsOn) {
        if (!dependsOn.value) {
          setDisabled(true);
          return;
        }
        setDisabled(false);
        url.searchParams.set("program_id", dependsOn.value);
      } else {
        url.searchParams.set("q", search.value.trim());
      }

      const response = await fetch(url, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      if (!response.ok) return;
      const data = await response.json();
      render(data.results || []);
      panel.classList.add("is-open");
    });

    search.addEventListener("input", fetchOptions);
    search.addEventListener("focus", fetchOptions);
    search.addEventListener("click", fetchOptions);

    document.addEventListener("click", (event) => {
      if (!wrapper.contains(event.target)) panel.classList.remove("is-open");
    });

    if (dependsOn) {
      setDisabled(!dependsOn.value);
      dependsOn.addEventListener("change", () => {
        select.replaceChildren();
        search.value = "";
        setDisabled(!dependsOn.value);
        if (dependsOn.value) fetchOptions();
      });
    }

    return { select };
  };

  document.addEventListener("DOMContentLoaded", () => {
    const programContainer = document.querySelector(".searchable-program-field");
    const offeringContainer = document.querySelector(".searchable-offering-field");
    if (!programContainer || !offeringContainer) return;

    const programPicker = buildPicker(programContainer);
    if (!programPicker) return;
    buildPicker(offeringContainer, programPicker.select);
  });
})();
