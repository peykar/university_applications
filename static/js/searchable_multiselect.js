(() => {
  const enhance = (select) => {
    if (select.dataset.enhanced === "true") return;
    select.dataset.enhanced = "true";

    const wrapper = document.createElement("div");
    wrapper.className = "multi-picker";

    const search = document.createElement("input");
    search.type = "search";
    search.className = "multi-picker-search";
    search.placeholder = select.dataset.placeholder || "Search";
    search.autocomplete = "off";

    const chips = document.createElement("div");
    chips.className = "multi-picker-chips";

    const optionsPanel = document.createElement("div");
    optionsPanel.className = "multi-picker-options";

    const options = Array.from(select.options);

    const renderChips = () => {
      chips.replaceChildren();
      options.filter((option) => option.selected).forEach((option) => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "multi-picker-chip";
        chip.textContent = option.text;
        chip.setAttribute("aria-label", `Remove ${option.text}`);
        chip.addEventListener("click", () => {
          option.selected = false;
          select.dispatchEvent(new Event("change", { bubbles: true }));
          render();
        });
        chips.append(chip);
      });
      chips.hidden = chips.childElementCount === 0;
    };

    const renderOptions = () => {
      const query = search.value.trim().toLocaleLowerCase();
      optionsPanel.replaceChildren();

      const matches = options
        .filter((option) => !option.selected)
        .filter((option) => option.text.toLocaleLowerCase().includes(query))
        .slice(0, 12);

      if (matches.length === 0) {
        const empty = document.createElement("div");
        empty.className = "multi-picker-empty";
        empty.textContent = "No matching options";
        optionsPanel.append(empty);
        return;
      }

      matches.forEach((option) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "multi-picker-option";
        button.textContent = option.text;
        button.addEventListener("click", () => {
          option.selected = true;
          search.value = "";
          select.dispatchEvent(new Event("change", { bubbles: true }));
          render();
          search.focus();
        });
        optionsPanel.append(button);
      });
    };

    const render = () => {
      renderChips();
      renderOptions();
    };

    search.addEventListener("input", renderOptions);
    search.addEventListener("focus", () => {
      optionsPanel.classList.add("is-open");
      renderOptions();
    });
    search.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        optionsPanel.classList.remove("is-open");
        search.blur();
      }
    });
    document.addEventListener("click", (event) => {
      if (!wrapper.contains(event.target)) {
        optionsPanel.classList.remove("is-open");
      }
    });

    select.classList.add("multi-picker-native");
    select.insertAdjacentElement("afterend", wrapper);
    wrapper.append(search, chips, optionsPanel);
    render();
  };

  document
    .querySelectorAll("select.searchable-multiselect")
    .forEach(enhance);
})();
