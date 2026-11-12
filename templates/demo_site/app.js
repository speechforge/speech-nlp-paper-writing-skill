/* Project demo site: switchable audio comparison with a live spectrogram, blind listening test,
   text comparison with word-level differences, figure lightbox, ranked results, and credits.
   No external requests. Every string from the data file is inserted with textContent. */
(() => {
  "use strict";
  const D = JSON.parse(document.getElementById("data").textContent);
  const hue = Number(getComputedStyle(document.documentElement).getPropertyValue("--hue")) || 200;
  const $ = (s, r = document) => r.querySelector(s);
  const el = (tag, attrs = {}, ...kids) => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k.startsWith("aria-")) { n.setAttribute(k, String(v)); continue; }
      if (v === false || v == null) continue;
      if (k === "class") n.className = v; else if (k.startsWith("on")) n.addEventListener(k.slice(2), v); else n.setAttribute(k, v === true ? "" : v);
    }
    for (const c of kids.flat(Infinity)) n.append(c && c.nodeType ? c : document.createTextNode(c == null ? "" : String(c)));
    return n;
  };
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const fmt = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;
  const isRef = (s) => s.reference || /^ref(erence)?\b|ground.?truth|natural/i.test(s.name);

  // theme
  const root = document.documentElement;
  try { const t = localStorage.getItem("theme"); if (t) root.dataset.theme = t; } catch (e) { /* storage may be blocked */ }
  $("#theme").addEventListener("click", () => {
    const dark = root.dataset.theme ? root.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    root.dataset.theme = dark ? "light" : "dark";
    try { localStorage.setItem("theme", root.dataset.theme); } catch (e) { /* ignore */ }
  });

  // header
  $("#h1").textContent = D.project_name;
  $("#tagline").textContent = D.tagline || "";
  $("#summary").textContent = D.summary || "";
  if (!D.tagline) $("#tagline").hidden = true;
  if (!D.summary) $("#summary").hidden = true;

  /* ---------- spectrogram engine ---------- */
  function fft(re, im) {
    const n = re.length;
    for (let i = 1, j = 0; i < n; i++) { let b = n >> 1; for (; j & b; b >>= 1) j ^= b; j ^= b; if (i < j) { [re[i], re[j]] = [re[j], re[i]]; [im[i], im[j]] = [im[j], im[i]]; } }
    for (let len = 2; len <= n; len <<= 1) {
      const a = -2 * Math.PI / len, wr = Math.cos(a), wi = Math.sin(a), h = len >> 1;
      for (let i = 0; i < n; i += len) {
        let cr = 1, ci = 0;
        for (let k = 0; k < h; k++) {
          const ur = re[i + k], ui = im[i + k], xr = re[i + k + h], xi = im[i + k + h];
          const vr = xr * cr - xi * ci, vi = xr * ci + xi * cr;
          re[i + k] = ur + vr; im[i + k] = ui + vi; re[i + k + h] = ur - vr; im[i + k + h] = ui - vi;
          const t = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = t;
        }
      }
    }
  }
  function parseWav(buf) { // PCM 8/16/24/32-bit and float32, first channel
    const v = new DataView(buf); let pos = 12, fmt = null, data = null;
    if (v.getUint32(0, false) !== 0x52494646) throw new Error("not a WAV file");
    while (pos + 8 <= v.byteLength) {
      const id = v.getUint32(pos, false), size = v.getUint32(pos + 4, true);
      if (id === 0x666d7420) fmt = { tag: v.getUint16(pos + 8, true), ch: v.getUint16(pos + 10, true), sr: v.getUint32(pos + 12, true), bits: v.getUint16(pos + 22, true) };
      if (id === 0x64617461) { data = { start: pos + 8, size: Math.min(size, v.byteLength - pos - 8) }; break; }
      pos += 8 + size + (size & 1);
    }
    if (!fmt || !data) throw new Error("incomplete WAV");
    const bytes = fmt.bits / 8, n = Math.floor(data.size / (bytes * fmt.ch)), x = new Float32Array(n);
    for (let i = 0; i < n; i++) {
      const o = data.start + i * bytes * fmt.ch;
      x[i] = fmt.tag === 3 ? v.getFloat32(o, true) : fmt.bits === 16 ? v.getInt16(o, true) / 32768 : fmt.bits === 8 ? (v.getUint8(o) - 128) / 128
        : fmt.bits === 24 ? ((v.getUint8(o) | (v.getUint8(o + 1) << 8) | (v.getInt8(o + 2) << 16)) / 8388608) : v.getInt32(o, true) / 2147483648;
    }
    return { sampleRate: fmt.sr, duration: n / fmt.sr, getChannelData: () => x };
  }
  async function decode(url) {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error("HTTP " + resp.status);
    const buf = await resp.arrayBuffer();
    if (/\.wav(\?|$)/i.test(url)) return parseWav(buf);
    const AC = window.AudioContext || window.webkitAudioContext, ctx = new AC();
    try { return await Promise.race([ctx.decodeAudioData(buf), new Promise((_, rej) => setTimeout(() => rej(new Error("decode timeout")), 10000))]); } finally { if (ctx.close) ctx.close(); }
  }
  function spectrogram(audio) {
    const x = audio.getChannelData(0), sr = audio.sampleRate, N = 1024;
    const hop = Math.max(256, Math.ceil((x.length - N) / 1000));
    const frames = Math.max(1, Math.floor((x.length - N) / hop) + 1);
    const fmax = Math.min(sr / 2, 8000), bins = Math.floor(fmax / (sr / N));
    const db = new Float32Array(frames * bins), re = new Float32Array(N), im = new Float32Array(N);
    const win = new Float32Array(N).map((_, i) => 0.5 - 0.5 * Math.cos(2 * Math.PI * i / N));
    for (let f = 0; f < frames; f++) {
      for (let i = 0; i < N; i++) { re[i] = (x[f * hop + i] || 0) * win[i]; im[i] = 0; }
      fft(re, im);
      for (let b = 0; b < bins; b++) db[f * bins + b] = 20 * Math.log10(Math.hypot(re[b], im[b]) + 1e-8);
    }
    return { frames, bins, db, fmax, duration: audio.duration };
  }
  function ramp(t) { // dark -> project hue -> near white
    const l = 6 + 88 * Math.pow(t, 1.15), s = 70 * (1 - 0.55 * Math.pow(t, 3)), h = hue + 28 * t;
    const a = s * Math.min(l, 100 - l) / 10000, f = (n) => { const k = (n + h / 30) % 12; return Math.round(255 * (l / 100 - a * Math.max(-1, Math.min(k - 3, 9 - k, 1)))); };
    return [f(0), f(8), f(4)];
  }
  function paint(spec, ref, range = 75) {
    const c = document.createElement("canvas"); c.width = spec.frames; c.height = spec.bins;
    const g = c.getContext("2d"), img = g.createImageData(spec.frames, spec.bins);
    for (let f = 0; f < spec.frames; f++) for (let b = 0; b < spec.bins; b++) {
      const t = Math.max(0, Math.min(1, (spec.db[f * spec.bins + b] - ref + range) / range)), [r, gr, bl] = ramp(t);
      const o = ((spec.bins - 1 - b) * spec.frames + f) * 4; img.data[o] = r; img.data[o + 1] = gr; img.data[o + 2] = bl; img.data[o + 3] = 255;
    }
    g.putImageData(img, 0, 0); return c;
  }
  function drawTo(canvas, bitmap, progressive) {
    const w = canvas.clientWidth * devicePixelRatio, h = canvas.clientHeight * devicePixelRatio;
    canvas.width = w; canvas.height = h; const g = canvas.getContext("2d"); g.imageSmoothingEnabled = true;
    if (!progressive || reduced) { g.drawImage(bitmap, 0, 0, w, h); return; }
    const t0 = performance.now(), step = (now) => {
      const p = Math.min(1, (now - t0) / 900); g.clearRect(0, 0, w, h);
      g.drawImage(bitmap, 0, 0, bitmap.width * p, bitmap.height, 0, 0, w * p, h);
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  /* ---------- audio tracks ---------- */
  async function prepare(sample) {
    if (sample._ready) return sample._ready;
    sample._ready = (async () => {
      const out = [];
      for (const s of sample.systems) {
        try { const a = await decode(s.file); out.push({ s, spec: spectrogram(a) }); } catch (e) { out.push({ s, spec: null }); }
      }
      const ref = Math.max(...out.filter((o) => o.spec).map((o) => Math.max(...o.spec.db.filter((_, i) => i % 7 === 0))), -Infinity);
      out.forEach((o) => { if (o.spec) o.bitmap = paint(o.spec, ref); });
      return out;
    })();
    return sample._ready;
  }
  function track(sample) {
    const audio = new Audio(); audio.preload = "metadata";
    let current = 0, ready = [];
    const screen = el("div", { class: "screen seekable" }, el("canvas", { "aria-label": `Spectrogram for ${sample.title || "sample"}` }), el("div", { class: "playhead" }));
    const canvas = $("canvas", screen), head = $(".playhead", screen);
    const note = (t) => screen.append(el("div", { class: "note" }, t));
    const time = el("span", { class: "time" }, "0:00 / 0:00");
    const play = el("button", { class: "play", type: "button", "aria-label": "Play" }, "Play");
    const buttons = sample.systems.map((s, i) => el("button", { type: "button", role: "radio", "aria-checked": i === 0, class: s.highlight ? "proposed" : "", onclick: () => choose(i) }, s.name));
    const dl = el("a", { class: "dl", href: sample.systems[0].file, download: "" }, "Download this sample");
    function show() {
      const o = ready[current]; screen.querySelectorAll(".note,.ax,img").forEach((n) => n.remove());
      if (o && o.bitmap) { drawTo(canvas, o.bitmap); screen.append(el("span", { class: "ax ax-top" }, `${Math.round(o.spec.fmax / 1000)} kHz`), el("span", { class: "ax ax-bot" }, "0"), el("span", { class: "ax ax-end" }, fmt(o.spec.duration))); }
      else if (sample.systems[current].spectrogram) { canvas.style.display = "none"; screen.append(el("img", { src: sample.systems[current].spectrogram, alt: "Spectrogram" })); }
      else { note("Spectrograms are drawn in the browser. Serve this folder over http (see the dashboard) to see them."); }
    }
    function choose(i) {
      const t = audio.currentTime, playing = !audio.paused; current = i;
      buttons.forEach((b, j) => b.setAttribute("aria-checked", j === i));
      audio.src = sample.systems[i].file; dl.href = sample.systems[i].file;
      audio.addEventListener("loadedmetadata", () => { try { audio.currentTime = Math.min(t, audio.duration || t); } catch (e) { /* ignore */ } if (playing) audio.play(); }, { once: true });
      if (ready.length) show();
    }
    audio.src = sample.systems[0].file;
    play.addEventListener("click", () => { if (audio.paused) { document.querySelectorAll("audio").forEach((a) => a.pause()); audio.play(); } else audio.pause(); });
    audio.addEventListener("play", () => { play.textContent = "Pause"; play.setAttribute("aria-label", "Pause"); document.querySelectorAll("audio").forEach((a) => { if (a !== audio) a.pause(); }); loop(); });
    audio.addEventListener("pause", () => { play.textContent = "Play"; play.setAttribute("aria-label", "Play"); });
    audio.addEventListener("ended", () => { play.textContent = "Play"; });
    const loop = () => { const d = audio.duration || 1; head.style.left = `${(audio.currentTime / d) * 100}%`; time.textContent = `${fmt(audio.currentTime)} / ${fmt(d)}`; if (!audio.paused) requestAnimationFrame(loop); };
    audio.addEventListener("timeupdate", loop); audio.addEventListener("loadedmetadata", loop);
    screen.addEventListener("click", (e) => { const r = screen.getBoundingClientRect(); if (audio.duration) { audio.currentTime = ((e.clientX - r.left) / r.width) * audio.duration; loop(); } });
    const node = el("article", { class: "track" },
      el("h3", {}, sample.title || "Sample"),
      sample.transcript ? el("p", { class: "transcript" }, sample.transcript) : "",
      el("div", { class: "switch", role: "radiogroup", "aria-label": "Choose which system to hear" }, buttons),
      screen, el("div", { class: "transport" }, play, time, dl));
    const io = new IntersectionObserver(async (entries) => {
      if (!entries.some((e) => e.isIntersecting)) return; io.disconnect();
      ready = await prepare(sample); show();
    }, { rootMargin: "300px" });
    io.observe(node);
    return node;
  }

  /* ---------- sections ---------- */
  const sections = [];
  const add = (id, title, lede, ...kids) => sections.push({ id, title, node: el("section", { id }, el("h2", {}, title), lede ? el("p", { class: "lede" }, lede) : "", ...kids) });

  if ((D.pipeline || []).length) {
    const panel = el("div", { class: "panel" }); const tabs = el("div", { class: "tabs", role: "tablist" });
    const sel = (i) => { [...tabs.children].forEach((b, j) => b.setAttribute("aria-selected", j === i)); panel.replaceChildren(el("h3", {}, D.pipeline[i].title), el("p", {}, D.pipeline[i].text), D.pipeline[i].image ? el("img", { src: D.pipeline[i].image, alt: D.pipeline[i].title }) : ""); };
    D.pipeline.forEach((p, i) => tabs.append(el("button", { type: "button", role: "tab", "aria-selected": false, onclick: () => sel(i) }, p.title)));
    sel(0); add("how", "How it works", D.pipeline_lede || "", el("div", { class: "steps" }, tabs, panel));
  }

  const aud = (D.audio_samples || []).filter((s) => (s.systems || []).length);
  if (aud.length) add("listen", "Listen and compare", "Pick a system, press play, then switch systems while the sample plays. The playhead stays where it is, so you hear the same moment in each. Spectrograms share one color scale per sample.", ...aud.map((s) => track(s)));

  const pool = aud.filter((s) => s.systems.filter((x) => !isRef(x)).length >= 2);
  if (D.blind_test && D.blind_test.enabled !== false && pool.length) {
    const box = el("div", { class: "blind" });
    const items = pool.map((s) => { const c = s.systems.filter((x) => !isRef(x)).sort(() => Math.random() - 0.5).slice(0, 2); return { s, pair: c }; }).sort(() => Math.random() - 0.5);
    const tally = {}; let i = 0; const audioEl = new Audio();
    const render = () => {
      audioEl.pause();
      if (i >= items.length) {
        const rows = Object.entries(tally).sort((a, b) => b[1].win - a[1].win);
        const tb = el("table", { class: "result" }, el("tr", {}, el("th", {}, "System"), el("th", {}, "Preferred"), el("th", {}, "Heard")), rows.map(([n, v]) => el("tr", {}, el("td", {}, n), el("td", {}, v.win), el("td", {}, v.seen))));
        box.replaceChildren(el("h3", {}, "Your results"), tb, el("p", { class: "meta" }, "These choices stay in this browser. Nothing is sent anywhere."), el("button", { type: "button", onclick: () => location.reload() }, "Start again"));
        try { localStorage.setItem("blind-" + D.slug, JSON.stringify(tally)); } catch (e) { /* ignore */ }
        return;
      }
      const it = items[i], [A, B] = it.pair; let on = 0; const q = (D.blind_test && D.blind_test.question) || "Which sample sounds better?";
      const play = (k) => { const t = audioEl.currentTime, was = !audioEl.paused; on = k; audioEl.src = [A, B][k].file; audioEl.addEventListener("loadedmetadata", () => { audioEl.currentTime = Math.min(t, audioEl.duration || t); audioEl.play(); }, { once: true }); if (!was && !t) audioEl.play(); };
      const pick = (w) => { for (const x of [A, B]) (tally[x.name] = tally[x.name] || { win: 0, seen: 0 }).seen++; if (w) tally[w.name].win++; i++; render(); };
      box.replaceChildren(el("p", { class: "meta" }, `Pair ${i + 1} of ${items.length}`), it.s.transcript ? el("p", {}, it.s.transcript) : "", el("p", {}, q),
        el("div", { class: "row" }, el("button", { type: "button", onclick: () => play(0) }, "Play A"), el("button", { type: "button", onclick: () => play(1) }, "Play B")),
        el("div", { class: "row" }, el("button", { type: "button", onclick: () => pick(A) }, "A is better"), el("button", { type: "button", onclick: () => pick(B) }, "B is better"), el("button", { type: "button", onclick: () => pick(null) }, "No preference")));
    };
    render(); add("blind", "Blind listening test", "System names stay hidden until the end, and the order of A and B is shuffled.", box);
  }

  const txt = D.text_samples || [];
  if (txt.length) {
    const lcsMask = (ref, out) => { const m = ref.length, n = out.length, dp = Array.from({ length: m + 1 }, () => new Uint16Array(n + 1)); for (let a = m - 1; a >= 0; a--) for (let b = n - 1; b >= 0; b--) dp[a][b] = ref[a] === out[b] ? dp[a + 1][b + 1] + 1 : Math.max(dp[a + 1][b], dp[a][b + 1]); const keep = new Array(n).fill(false); let a = 0, b = 0; while (a < m && b < n) { if (ref[a] === out[b]) { keep[b] = true; a++; b++; } else if (dp[a + 1][b] >= dp[a][b + 1]) a++; else b++; } return keep; };
    const marked = (ref, out) => { const r = ref.split(/\s+/), o = out.split(/\s+/), keep = lcsMask(r, o); return o.flatMap((w, i) => [keep[i] ? w : el("mark", { class: "diff" }, w), " "]); };
    const wrap = el("div", {}); const cb = el("input", { type: "checkbox", id: "diffbox", checked: true });
    cb.addEventListener("change", () => wrap.querySelectorAll(".compare").forEach((c) => c.classList.toggle("nodiff", !cb.checked)));
    wrap.append(el("label", { class: "toggle", for: "diffbox" }, cb, "Highlight words that differ from the reference"));
    txt.forEach((t) => wrap.append(el("div", { class: "compare" }, el("h3", {}, t.title || "Example"), el("dl", {},
      t.input ? [el("dt", {}, "Input"), el("dd", {}, t.input)] : "", t.reference ? [el("dt", {}, "Reference"), el("dd", {}, t.reference)] : "",
      (t.outputs || []).map((o) => [el("dt", { class: o.highlight ? "proposed" : "" }, o.name), el("dd", { class: o.highlight ? "proposed" : "" }, t.reference ? marked(t.reference, o.text) : o.text)])))));
    add("outputs", "Compare outputs", "", wrap);
  }

  if ((D.gallery || []).length) {
    const dlg = el("dialog", {}), big = el("img", { alt: "" }); dlg.append(big); dlg.addEventListener("click", () => dlg.close());
    add("figures", "Figures", "", el("div", { class: "gallery" }, D.gallery.map((g) => el("figure", {}, el("img", { src: g.file, alt: g.alt || g.title || "", loading: "lazy", onclick: () => { big.src = g.file; big.alt = g.alt || g.title || ""; dlg.showModal(); } }), el("figcaption", {}, g.caption || g.title || "")))), dlg);
  }
  if ((D.videos || []).length) add("video", "Videos", "", D.videos.map((v) => el("figure", {}, el("video", { controls: true, preload: "metadata", poster: v.poster || false }, el("source", { src: v.file }), v.captions ? el("track", { kind: "captions", src: v.captions, default: true }) : ""), el("figcaption", {}, v.caption || v.title || ""))));

  const res = Array.isArray(D.results) ? D.results : D.results ? [D.results] : [];
  if (res.length) add("results", "Results", "", res.map((r) => {
    const up = r.direction !== "down", rows = [...r.rows].sort((a, b) => (up ? b.value - a.value : a.value - b.value));
    const lo = r.axis_min ?? 0, hi = Math.max(...rows.map((x) => x.value + (x.ci || 0)));
    return el("div", { class: "results" }, el("h3", {}, r.title || r.metric), el("p", { class: "meta" }, `${r.metric}${r.unit ? " (" + r.unit + ")" : ""}: ${up ? "higher" : "lower"} is better.${r.axis_min != null ? " The axis starts at " + r.axis_min + "." : ""}`),
      el("ul", { class: "bars" }, rows.map((x) => el("li", { class: x.highlight ? "proposed" : "" }, el("span", { class: "label" }, x.name),
        el("span", { class: "track-bar" }, el("span", { class: "fill", style: `width:${((x.value - lo) / (hi - lo)) * 100}%` }), x.ci ? el("span", { class: "whisker", style: `left:${((x.value - x.ci - lo) / (hi - lo)) * 100}%;width:${((2 * x.ci) / (hi - lo)) * 100}%` }) : ""),
        el("span", { class: "val" }, x.value.toFixed(r.decimals ?? 2) + (x.ci ? ` ± ${x.ci.toFixed(r.decimals ?? 2)}` : ""))))),
      r.note ? el("p", { class: "meta" }, r.note) : "");
  }));

  $("#sections").append(...sections.map((s) => s.node));
  $("#nav").append(...sections.map((s) => el("a", { href: "#" + s.id }, s.title)));
  const links = [...document.querySelectorAll("#nav a")];
  const spy = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) links.forEach((a) => a.setAttribute("aria-current", a.getAttribute("href") === "#" + e.target.id)); }), { rootMargin: "-40% 0px -55% 0px" });
  sections.forEach((s) => spy.observe(s.node));

  /* hero spectrogram: the first sample, drawn once */
  if (aud.length) {
    const hs = $("#hero-screen"), hc = $("#hero-canvas"); hs.hidden = false;
    prepare(aud[0]).then((r) => { const o = r.find((x) => x.bitmap); if (o) drawTo(hc, o.bitmap, true); else hs.hidden = true; });
    addEventListener("resize", () => prepare(aud[0]).then((r) => { const o = r.find((x) => x.bitmap); if (o) drawTo(hc, o.bitmap); }));
  }

  /* credits and licenses */
  const C = D.credits || {}, foot = $("#credits"), cols = [];
  if ((C.authors || []).length) cols.push(el("div", {}, el("h2", {}, "Credits"), el("table", {}, C.authors.map((a) => el("tr", {}, el("th", {}, a.name), el("td", {}, (a.roles || []).join(", ")))))));
  const lic = Object.entries(C.licenses || {});
  if (lic.length) cols.push(el("div", {}, el("h2", {}, "Licenses"), el("table", {}, lic.map(([k, v]) => el("tr", {}, el("th", {}, k.replace("_", " ")), el("td", {}, v)))),
    C.human_subjects_consent ? el("p", {}, "Speakers and participants consented to public release of their recordings.") : ""));
  if ((C.third_party || []).length || (C.restrictions || []).length) cols.push(el("div", {}, el("h2", {}, "Third-party material"), el("ul", {}, (C.third_party || []).map((t) => el("li", {}, t.url ? el("a", { href: t.url }, t.name) : t.name, ` (${t.kind || "asset"}, ${t.license || "license not stated"})`)), (C.restrictions || []).map((r) => el("li", {}, r)))));
  cols.push(el("div", {}, el("h2", {}, "How to cite"), el("p", {}, D.citation || "Citation details are added once the paper is public."), C.repository_url ? el("p", {}, el("a", { href: C.repository_url }, "Code repository")) : ""));
  foot.append(el("div", { class: "in" }, cols));
})();
