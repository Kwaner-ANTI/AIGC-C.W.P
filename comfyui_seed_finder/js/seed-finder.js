/* Paste this entire file into DevTools on the running ComfyUI page. No imports. */
(() => {
  "use strict";
  // Tokenize strings first so digits inside filenames/prompts are never rewritten.
  // Preserve every JSON integer as its original decimal text before JSON.parse.
  function parseHistory(text) {
    return JSON.parse(text.replace(/"(?:[^"\\]|\\.)*"|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/g,
      token => token[0] !== '"' && /^-?\d+$/.test(token) ? JSON.stringify(token) : token));
  }

  const isGraph = value => value && typeof value === "object" && !Array.isArray(value);
  const isLink = value => Array.isArray(value) && value.length === 2;
  function display(value) {
    if (value == null) return "—";
    if (isLink(value)) return `未解析：节点 ${value[0]} 输出 ${value[1]}`;
    return typeof value === "object" ? "未解析的输入" : String(value);
  }

  function findTasks(history, filename) {
    const name = filename.trim();
    if (!name || !/\.png$/i.test(name)) throw new Error("请输入完整 PNG 文件名（含 .png）。");
    if (!isGraph(history)) throw new Error("/history 返回格式无效。");
    const matches = [];
    for (const [promptId, task] of Object.entries(history)) {
      for (const [outputId, output] of Object.entries(task?.outputs || {})) {
        for (const img of Array.isArray(output?.images) ? output.images : []) {
          if (img.filename !== name) continue;
          // Native history queue tuple: [number, prompt_id, executed API graph, extra_data, ...].
          // Never consult extra_data.extra_pnginfo.workflow or the active canvas.
          const graph = task.prompt?.[2];
          const nodes = [];
          const visited = new Set();
          const pending = [outputId];
          while (pending.length && isGraph(graph)) {
            const id = String(pending.pop());
            if (visited.has(id)) continue;
            visited.add(id);
            const node = graph[id];
            if (!node) continue;
            const inputs = node.inputs || {};
            for (const value of Object.values(inputs)) {
              if (isLink(value) && Object.hasOwn(graph, String(value[0]))) pending.push(String(value[0]));
            }
            const fields = ["seed", "noise_seed", "steps", "cfg", "sampler_name", "sampler"];
            if (!fields.some(field => Object.hasOwn(inputs, field))) continue;
            nodes.push({ nodeId: id, classType: node.class_type || "未知类型",
              seed: display(inputs.seed), noiseSeed: display(inputs.noise_seed),
              steps: display(inputs.steps), cfg: display(inputs.cfg),
              sampler: display(inputs.sampler_name ?? inputs.sampler) });
          }
          matches.push({ promptId, outputId, filename: img.filename,
            subfolder: img.subfolder || "", type: img.type || "", nodes,
            warning: !isGraph(graph) ? "任务缺少执行图。" : !nodes.length
              ? "此输出的上游执行图没有可读取的采样参数。" : "" });
        }
      }
    }
    return matches;
  }

  async function query(filename, fetchHistory) {
    if (!filename.trim() || !/\.png$/i.test(filename.trim())) throw new Error("请输入完整 PNG 文件名（含 .png）。");
    const response = await fetchHistory();
    if (!response.ok) throw new Error(`/history 请求失败：HTTP ${response.status}`);
    let history;
    try { history = parseHistory(await response.text()); }
    catch { throw new Error("/history 不是有效 JSON；请确认当前页面为已登录的 ComfyUI。"); }
    return findTasks(history, filename);
  }

  function mount(fetchHistory) {
    const existing = document.getElementById("comfy-seed-finder");
    if (existing) {
      if (fetchHistory) existing.fetchHistory = fetchHistory;
      return existing;
    }
    const root = document.createElement("section");
    root.id = "comfy-seed-finder";
    root.fetchHistory = fetchHistory || (() => {
      const base = new URL(location.href);
      base.search = ""; base.hash = "";
      if (!base.pathname.endsWith("/")) base.pathname += "/";
      return fetch(new URL("history", base), { method: "GET", credentials: "same-origin", cache: "no-store" });
    });
    root.style.cssText = "position:fixed;right:16px;bottom:16px;z-index:10000;background:#222;color:#eee;padding:12px;border:1px solid #777;border-radius:8px;max-width:90vw;font:13px sans-serif";
    const details = document.createElement("details");
    const summary = document.createElement("summary");
    summary.textContent = "Seed Finder";
    details.append(summary);
    const form = document.createElement("form");
    const input = document.createElement("input");
    input.placeholder = "完整输出 PNG 文件名";
    input.setAttribute("aria-label", input.placeholder);
    input.required = true;
    const search = document.createElement("button");
    search.textContent = "查询";
    const status = document.createElement("p");
    status.setAttribute("role", "status");
    const results = document.createElement("div");
    results.style.cssText = "max-height:55vh;overflow:auto;max-width:85vw";
    form.append(input, search);
    details.append(form, status, results);
    root.append(details);
    document.body.append(root);
    async function copy(text) {
      try { await navigator.clipboard.writeText(text); status.textContent = "已复制"; }
      catch {
        const area = document.createElement("textarea");
        area.value = text; results.prepend(area); area.select();
        status.textContent = "剪贴板不可用；已选中文本，请按 Ctrl/Cmd+C。";
      }
    }
    function copyButton(label, text) {
      const button = document.createElement("button");
      button.type = "button"; button.textContent = label;
      button.onclick = () => copy(text);
      return button;
    }
    form.onsubmit = async event => {
      event.preventDefault(); search.disabled = true; results.replaceChildren();
      status.textContent = "正在读取 /history…";
      try {
        const tasks = await query(input.value, root.fetchHistory);
        status.textContent = tasks.length ? `匹配 ${tasks.length} 个输出；仅显示该输出上游执行图的参数。`
          : "未匹配。运行中的任务可能尚未写入 history，或记录已被清理。";
        for (const task of tasks) {
          const heading = document.createElement("p");
          heading.textContent = `Prompt ID: ${task.promptId} | 输出节点: ${task.outputId} | ${task.subfolder}/${task.filename} (${task.type})`;
          results.append(heading, copyButton("复制任务参数", JSON.stringify(task, null, 2)));
          if (task.warning) {
            const warning = document.createElement("p"); warning.textContent = task.warning; results.append(warning);
          }
          const table = document.createElement("table");
          const header = table.insertRow();
          for (const name of ["节点 ID / 类型", "Seed", "noise_seed", "Steps", "CFG", "Sampler"]) {
            const th = document.createElement("th"); th.textContent = name; header.append(th);
          }
          for (const node of task.nodes) {
            const row = table.insertRow();
            for (const [key, value] of Object.entries({ node: `${node.nodeId} / ${node.classType}`, seed: node.seed,
              noiseSeed: node.noiseSeed, steps: node.steps, cfg: node.cfg, sampler: node.sampler })) {
              const cell = row.insertCell(); cell.textContent = value; cell.style.padding = "6px";
              if ((key === "seed" || key === "noiseSeed") && /^\d+$/.test(value)) cell.append(copyButton("复制", value));
            }
          }
          results.append(table);
        }
      } catch (error) { status.textContent = error.message; }
      finally { search.disabled = false; }
    };
    return root;
  }
  globalThis.ComfySeedFinder = { parseHistory, findTasks, query, mount };
  if (typeof document !== "undefined" && document.body) mount();
})();
