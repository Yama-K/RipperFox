const API = "http://localhost:5100/api";
let SETTINGS = {};
let previousStatuses = {};

// ---------- tiny utils ----------
const $ = s => document.querySelector(s);
function toast(msg, ok=true){
  if (!$("#showToasts") || !$("#showToasts").checked) return;
  const el = $("#toast");
  el.textContent = msg;
  el.style.borderLeftColor = ok ? "#4caf50" : "#f44336";
  el.classList.add("show");
  setTimeout(()=>el.classList.remove("show"), 2000);
}

// ---------- tabs ----------
function initTabs(){
  const dBtn = $("#tab-downloads");
  const sBtn = $("#tab-settings");
  const dTab = $("#downloads");
  const sTab = $("#settings");
  dBtn.onclick = ()=>{ dBtn.classList.add("active"); sBtn.classList.remove("active"); dTab.classList.add("active"); sTab.classList.remove("active"); };
  sBtn.onclick = ()=>{ sBtn.classList.add("active"); dBtn.classList.remove("active"); sTab.classList.add("active"); dTab.classList.remove("active"); };
}

// ---------- settings load/save ----------
async function loadSettings(){
  try{
    const res = await fetch(`${API}/settings`);
    SETTINGS = await res.json();
    renderSettings(SETTINGS);
    $("#settingsError").style.display = "none";
  }catch(e){
    console.error("[yt-dlp] settings fetch failed", e);
    const box = $("#settingsError");
    box.textContent = "Could not load settings. Is backend running?";
    box.style.display = "";
  }
}

function renderSettings(s){
  $("#genPath").value   = s.yt_dlp_path ?? "yt-dlp";
  $("#genOutput").value = s.default_dir ?? "";
  $("#genArgs").value   = s.default_args ?? "";
  $("#showToasts").checked = s.show_toasts ?? true;
  renderSites(s.download_dirs || {});
}

async function saveGeneral(){
  SETTINGS.yt_dlp_path  = $("#genPath").value.trim() || "yt-dlp";
  SETTINGS.default_dir  = $("#genOutput").value.trim();
  SETTINGS.default_args = $("#genArgs").value.trim();
  SETTINGS.show_toasts  = $("#showToasts").checked;
  try{
    await fetch(`${API}/settings`, {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify(SETTINGS)
    });
    toast("Settings saved");
  }catch(e){
    console.error("[yt-dlp] save general failed", e);
    toast("Failed to save", false);
  }
}
$("#saveGeneral").onclick = saveGeneral;

// ---------- per-site (simple add/edit) ----------
function renderSites(map){
  const wrap = $("#sites");
  wrap.innerHTML = "";
  const entries = Object.entries(map);
  if (!entries.length){
    wrap.innerHTML = `<div class="muted">No sites configured yet.</div>`;
    return;
  }
  for (const [pattern, conf] of entries){
    const card = document.createElement("div");
    card.className = "site";
    card.innerHTML = `
      <div class="field-label">Site pattern(s)</div>
      <input class="pattern" value="${pattern}">
      <div class="field-label">Directory</div>
      <input class="dir" value="${conf.dir ?? ""}">
      <div class="field-label">Extra args</div>
      <textarea class="args">${conf.args ?? ""}</textarea>
      <div class="row">
        <button class="save grow">Save</button>
        <button class="del" style="background:#7b1e1e">Delete</button>
      </div>
    `;
    const f = {
      pattern: card.querySelector(".pattern"),
      dir:     card.querySelector(".dir"),
      args:    card.querySelector(".args"),
      save:    card.querySelector(".save"),
      del:     card.querySelector(".del"),
    };

    f.save.onclick = async ()=>{
      const oldKey = pattern;
      const newKey = f.pattern.value.trim() || oldKey;
      if (newKey !== oldKey) delete SETTINGS.download_dirs[oldKey];
      SETTINGS.download_dirs[newKey] = { dir:f.dir.value.trim(), args:f.args.value.trim() };
      await fetch(`${API}/settings`, {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify(SETTINGS)
      });
      toast("Site saved");
      renderSites(SETTINGS.download_dirs);
    };

    f.del.onclick = async ()=>{
      delete SETTINGS.download_dirs[pattern];
      await fetch(`${API}/settings`, {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify(SETTINGS)
      });
      toast("Site deleted");
      renderSites(SETTINGS.download_dirs);
    };

    wrap.appendChild(card);
  }
}

$("#saveSite").onclick = async ()=>{
  const pattern = $("#sitePattern").value.trim();
  if (!pattern){ toast("Pattern missing", false); return; }
  const dir = $("#siteDir").value.trim();
  const args = $("#siteArgs").value.trim();
  if (!SETTINGS.download_dirs) SETTINGS.download_dirs = {};
  SETTINGS.download_dirs[pattern] = { dir, args };
  await fetch(`${API}/settings`, {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify(SETTINGS)
  });
  toast("Site saved");
  renderSites(SETTINGS.download_dirs);
};

// ---------- downloads ----------
async function pollStatus(){
  const stateEl = $("#jobsState");
  const listEl  = $("#jobList");
  try{
    const res = await fetch(`${API}/status`);
    const jobs = await res.json();
    const items = Object.entries(jobs);
    listEl.innerHTML = "";

    if (!items.length){
      stateEl.textContent = "Idle";
      previousStatuses = {};
      return;
    }
    stateEl.textContent = "";

    // newest first (keys are epoch ms)
    items.sort((a,b)=> (parseInt(b[0])||0) - (parseInt(a[0])||0));

    for (const [id, job] of items){
      const div = document.createElement("div");
      const st = (job.status || "").toLowerCase();
      div.className = "job " + (st.includes("error") ? "err" : st.startsWith("run")||st.startsWith("start") ? "run" : "ok");
      div.innerHTML = `
        <b>${job.site || "Unknown site"}</b><br>
        <small class="muted">${job.url || ""}</small><br>
        Status: ${job.status}<br>
        Directory: ${job.dir || ""}
      `;
      listEl.appendChild(div);
      previousStatuses[id] = job.status;
    }
  }catch(e){
    console.error("[yt-dlp] jobs fetch failed", e);
    stateEl.textContent = "Backend unreachable";
    listEl.innerHTML = "";
  }
}

$("#clearDownloads").onclick = async ()=>{
  try{
    const res = await fetch(`${API}/status`, { method:"DELETE" });
    if (res.ok){
      $("#jobList").innerHTML = "";
      $("#jobsState").textContent = "Cleared.";
      toast("Cleared downloads");
    }
  }catch(e){
    console.error("[yt-dlp] clear failed", e);
  }
};

// ---------- boot ----------
document.addEventListener("DOMContentLoaded", ()=>{
  initTabs();
  // draw immediately
  $("#jobsState").textContent = "Idle";
  $("#jobList").innerHTML = "";
  // load data
  loadSettings();
  pollStatus();                 // first fetch right away
  setInterval(pollStatus, 3000);
});
