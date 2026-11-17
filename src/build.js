// Builds theme/faceplate.json from the sources in this folder.
//
//   node src/build.js
//
// dark.css and light.css are complete stylesheets for each mode. Rules that are identical in both are written once;
// rules that differ are written twice, scoped to the app's mode with :where(html.dark) / :where(html:not(.dark)).
// :where() adds no specificity, so the cascade inside each mode is exactly what the per-mode file says.
const fs = require("fs");
const path = require("path");
const here = (f) => path.join(__dirname, f);
const LIMIT = 50000; // T3 Code's limit on a theme's css

const strip = (s) => s.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\s*\n\s*/g, "").trim();

function rules(css) { // top-level rules, keeping at-rule blocks whole
  const out = []; let depth = 0, start = 0;
  for (let i = 0; i < css.length; i++) {
    if (css[i] === "{") depth++;
    else if (css[i] === "}") { depth--; if (depth === 0) { out.push(css.slice(start, i + 1)); start = i + 1; } }
  }
  return out;
}

function splitSelectors(sel) { // split on commas that are not inside parentheses, brackets or strings
  const out = []; let depth = 0, cur = "", quote = null;
  for (const ch of sel) {
    if (quote) { cur += ch; if (ch === quote) quote = null; continue; }
    if (ch === '"' || ch === "'") { quote = ch; cur += ch; continue; }
    if (ch === "(" || ch === "[") depth++;
    if (ch === ")" || ch === "]") depth--;
    if (ch === "," && depth === 0) { out.push(cur); cur = ""; } else cur += ch;
  }
  out.push(cur);
  return out;
}

function scope(rule, mode) {
  if (rule.startsWith("@")) throw new Error("an at-rule differs between dark.css and light.css: " + rule.slice(0, 80));
  const brace = rule.indexOf("{");
  const html = mode === "dark" ? "html.dark" : "html:not(.dark)";
  const selectors = splitSelectors(rule.slice(0, brace)).map((s) => {
    s = s.trim();
    return s.startsWith(":root") ? `:root:where(${html})${s.slice(5)}` : `:where(${html}) ${s}`;
  });
  return selectors.join(",") + rule.slice(brace);
}

function merge(darkCss, lightCss) {
  const D = rules(strip(darkCss)), L = rules(strip(lightCss));
  const inDark = new Set(D), inLight = new Set(L);
  const out = []; let i = 0, j = 0;
  while (i < D.length || j < L.length) {
    if (i < D.length && j < L.length && D[i] === L[j]) { out.push(D[i]); i++; j++; }
    else if (i < D.length && !inLight.has(D[i])) out.push(scope(D[i++], "dark"));
    else if (j < L.length) out.push(scope(L[j++], "light"));
    else out.push(scope(D[i++], "dark"));
  }
  return out.join("");
}

const css = merge(fs.readFileSync(here("dark.css"), "utf8"), fs.readFileSync(here("light.css"), "utf8"));

if (css.length > LIMIT) throw new Error(`css is ${css.length} characters; the limit is ${LIMIT}`);

const roles = JSON.parse(fs.readFileSync(here("roles.json"), "utf8"));
const theme = {
  name: "Faceplate",
  appearance: "dark",
  canvas: roles.dark.canvas,
  accent: roles.dark.accent,
  colors: roles.dark.colors,
  variants: { light: { canvas: roles.light.canvas, accent: roles.light.accent, ...roles.light.colors } },
  css,
};
const out = path.join(__dirname, "..", "theme", "faceplate.json");
fs.writeFileSync(out, JSON.stringify(theme));
console.log(`wrote ${out} (css ${css.length} of ${LIMIT} characters)`);
