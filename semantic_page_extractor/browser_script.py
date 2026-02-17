EXTRACTION_SCRIPT = r"""
(() => {
  const normalize = (v) => {
    if (v == null) return null;
    const s = String(v).replace(/\s+/g, " ").trim();
    return s.length ? s : null;
  };

  const textFromUrl = (value) => {
    const v = normalize(value);
    if (!v) return null;
    const byParam = /(?:[?&]|^)categoryId=([A-Za-z0-9_-]+)/i.exec(v);
    if (byParam && byParam[1]) return normalize(byParam[1].replace(/[_-]+/g, " "));
    const byPath = v.split("/").filter(Boolean).pop();
    if (!byPath) return null;
    const clean = byPath.replace(/\.[a-z0-9]+$/i, "").replace(/[_-]+/g, " ");
    return normalize(clean);
  };

  const textFromSrc = (value) => {
    const v = normalize(value);
    if (!v) return null;
    const file = v.split("/").filter(Boolean).pop();
    if (!file) return null;
    return normalize(file.replace(/\.[a-z0-9]+$/i, "").replace(/^(sm_|icon_)/i, "").replace(/[_-]+/g, " "));
  };

  const contextFromAttributes = (el) =>
    normalize(
      el.getAttribute("aria-label") ||
      el.getAttribute("alt") ||
      el.getAttribute("title") ||
      el.getAttribute("name") ||
      el.getAttribute("value")
    );

  const isVisible = (el) => {
    if (!el || !document.contains(el)) return false;
    if (el.tagName && el.tagName.toLowerCase() === "area") {
      const href = el.getAttribute("href");
      const map = el.parentElement;
      if (!href || !map || map.tagName.toLowerCase() !== "map") return false;
      const mapName = map.getAttribute("name");
      if (!mapName) return false;
      const mappedImg = document.querySelector(`img[usemap="#${CSS.escape(mapName)}"]`);
      return Boolean(mappedImg && isVisible(mappedImg));
    }
    const style = window.getComputedStyle(el);
    if (style.display === "none" || style.visibility === "hidden") return false;
    if (el.offsetParent === null) return false;
    return true;
  };

  const visibleText = (el) =>
    normalize(el.innerText || el.textContent || el.getAttribute("value") || contextFromAttributes(el));

  const findSectionContext = (el) => {
    const lastHeadingIn = (root) => {
      const nodes = root.querySelectorAll("h1,h2,h3,legend");
      for (let i = nodes.length - 1; i >= 0; i -= 1) {
        const txt = visibleText(nodes[i]);
        if (txt && isVisible(nodes[i])) return txt;
      }
      return null;
    };

    let current = el;
    while (current) {
      if (current.matches && current.matches("fieldset")) {
        const legend = current.querySelector(":scope > legend");
        if (legend && isVisible(legend)) {
          const txt = visibleText(legend);
          if (txt) return txt;
        }
      }

      let prev = current.previousElementSibling;
      while (prev) {
        const found = lastHeadingIn(prev);
        if (found) return found;
        prev = prev.previousElementSibling;
      }
      current = current.parentElement;
    }

    const globalHeader = document.querySelector("h1,h2,h3");
    if (globalHeader && isVisible(globalHeader)) return visibleText(globalHeader);

    let node = el;
    while (node && node !== document.body) {
      const fromId = normalize(node.getAttribute && node.getAttribute("id"));
      if (fromId) return fromId.replace(/[_-]+/g, " ");
      const fromClass = normalize(node.getAttribute && node.getAttribute("class"));
      if (fromClass) return fromClass.split(" ").filter(Boolean)[0].replace(/[_-]+/g, " ");
      node = node.parentElement;
    }
    return null;
  };

  const fieldType = (el) => {
    const tag = el.tagName.toLowerCase();
    if (tag === "textarea") return "textarea";
    if (tag === "select") return "select";
    if (tag === "input") return normalize(el.getAttribute("type")) || "text";
    return tag;
  };

  const fieldOptions = (el) => {
    const t = fieldType(el);
    if (t === "select") {
      return Array.from(el.querySelectorAll("option"))
        .map((o) => normalize(o.textContent))
        .filter(Boolean);
    }
    if (t === "radio") {
      const name = el.getAttribute("name");
      if (!name) return null;
      const radios = document.querySelectorAll(`input[type=\"radio\"][name=\"${CSS.escape(name)}\"]`);
      const opts = Array.from(radios)
        .filter(isVisible)
        .map((r) => {
          const id = r.getAttribute("id");
          const forLabel = id ? document.querySelector(`label[for=\"${CSS.escape(id)}\"]`) : null;
          return normalize((forLabel && forLabel.textContent) || r.getAttribute("value") || r.getAttribute("aria-label"));
        })
        .filter(Boolean);
      return opts.length ? opts : null;
    }
    return null;
  };

  const resolveLabelParts = (el) => {
    const id = el.getAttribute("id");
    const forLabel = id
      ? normalize((document.querySelector(`label[for=\"${CSS.escape(id)}\"]`) || {}).textContent)
      : null;
    const wrappingLabel = el.closest("label");
    const wrapped = wrappingLabel ? normalize(wrappingLabel.textContent) : null;
    return {
      label_for: forLabel,
      label_wrapped: wrapped,
      aria_label: normalize(el.getAttribute("aria-label")),
      placeholder: normalize(el.getAttribute("placeholder")),
    };
  };

  const toAction = (el) => {
    const tag = el.tagName.toLowerCase();
    const isAnchor = el.tagName.toLowerCase() === "a";
    const hasImg = isAnchor && el.querySelector("img");
    const img = hasImg ? el.querySelector("img") : null;
    const imgText = img
      ? normalize(
          contextFromAttributes(img) ||
          textFromSrc(img.getAttribute("src")) ||
          textFromUrl(el.getAttribute("href"))
        )
      : null;
    const areaText = tag === "area"
      ? normalize(contextFromAttributes(el) || textFromUrl(el.getAttribute("href")))
      : null;
    const defaultText = normalize(visibleText(el) || contextFromAttributes(el) || textFromUrl(el.getAttribute("href")));
    const computedText = hasImg ? (imgText || defaultText) : (areaText || defaultText);
    const role = tag === "area"
      ? "map_area"
      : (hasImg ? "image_link" : (normalize(el.getAttribute("role")) || (isAnchor ? "link" : "button")));
    return {
      role,
      visible_text: computedText,
      aria_label: normalize(el.getAttribute("aria-label")),
      disabled: Boolean(el.disabled || el.getAttribute("aria-disabled") === "true"),
      section_context: findSectionContext(el),
    };
  };

  const toField = (el) => {
    const parts = resolveLabelParts(el);
    return {
      ...parts,
      type: fieldType(el),
      required: Boolean(el.required || el.getAttribute("aria-required") === "true"),
      options: fieldOptions(el),
      disabled: Boolean(el.disabled || el.getAttribute("aria-disabled") === "true"),
      section_context: findSectionContext(el),
    };
  };

  const headers = Array.from(document.querySelectorAll("h1,h2,h3"))
    .filter(isVisible)
    .map((h) => visibleText(h))
    .filter(Boolean);

  const forms = Array.from(document.querySelectorAll("form")).map((form) => {
    const fields = Array.from(form.querySelectorAll("input,textarea,select"))
      .filter(isVisible)
      .filter((el) => {
        const t = (el.getAttribute("type") || "").toLowerCase();
        return !["hidden", "submit", "button", "reset", "image"].includes(t);
      })
      .map(toField);

    const submits = Array.from(form.querySelectorAll("button,input[type='submit'],input[type='button'],input[type='reset'],input[type='image'],[role='button']"))
      .filter(isVisible)
      .map(toAction);

    return {
      section_context: findSectionContext(form),
      fields,
      submit_buttons: submits,
    };
  });

  const seen = new Set();
  const interactive = [];
  const candidates = document.querySelectorAll("button,a[href],area[href],[role='button'],input[type='submit'],input[type='button'],input[type='reset'],input[type='image']");
  for (const el of candidates) {
    if (!isVisible(el)) continue;
    if (seen.has(el)) continue;
    seen.add(el);
    interactive.push(toAction(el));
  }

  return {
    url: window.location.href,
    title: document.title || "",
    headers,
    forms,
    interactive_elements: interactive,
  };
})();
"""
