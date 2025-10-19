const apiBase = "http://localhost:5100/api";
let lastState = "idle";
const action = browser.action || browser.browserAction;

// ----------------------------------------------------
// Context Menu
// ----------------------------------------------------
browser.contextMenus.removeAll().then(() => {
  browser.contextMenus.create({
    id: "ripperfox-download",
    title: "RipperFox Download",
    contexts: ["link", "video", "image", "page"]
  });
});

browser.contextMenus.onClicked.addListener(async (info, tab) => {
  try {
    let url = info.linkUrl || info.srcUrl || tab.url;
    if (!url) {
      console.warn("[yt-dlp] No valid URL found in context click");
      return;
    }

    // Handle thumbnails linking to post pages
    if (info.mediaType === "image" && info.linkUrl) {
      console.log("[yt-dlp] Thumbnail detected — using linked post URL:", info.linkUrl);
      url = info.linkUrl;
    }

    const mediaType = detectMediaType(url);
    console.log(`[yt-dlp] Context click → ${url} (${mediaType})`);

    await fetch(`${apiBase}/download`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, mediaType })
    });

    setEmoji("⚙️", "yt-dlp: Starting download...");
  } catch (err) {
    console.error("[yt-dlp] Context menu request failed:", err);
    setEmoji("❌", "yt-dlp: Error");
  }
});

function detectMediaType(url) {
  const lower = url.toLowerCase();
  if (lower.endsWith(".gif")) return "gif";
  if (lower.endsWith(".gifv")) return "gifv";
  if (lower.endsWith(".mp4") || lower.endsWith(".webm")) return "video";
  return "video";
}

// ----------------------------------------------------
// Emoji Icon Poller (lightweight status indicator)
// ----------------------------------------------------
async function checkDownloads() {
  try {
    const res = await fetch(`${apiBase}/status`);
    const jobs = await res.json();
    const statuses = Object.values(jobs).map(j => j.status);
    let newState = "idle";

    if (statuses.some(s => s.includes("error"))) newState = "error";
    else if (statuses.some(s => s.includes("running") || s.includes("starting"))) newState = "active";
    else if (statuses.some(s => s.includes("completed"))) newState = "done";
    else newState = "idle";

    if (newState !== lastState) {
      lastState = newState;
      updateEmoji(newState);
    }
  } catch (err) {
    console.error("[yt-dlp] Poll failed:", err);
  }
}

function updateEmoji(state) {
  let emoji = "💤";
  let title = "yt-dlp: Idle";

  switch (state) {
    case "active":
      emoji = "⚙️";
      title = "yt-dlp: Downloading...";
      break;
    case "error":
      emoji = "❌";
      title = "yt-dlp: Error";
      break;
    case "done":
      emoji = "✅";
      title = "yt-dlp: Done";
      break;
  }

  setEmoji(emoji, title);
}

function setEmoji(emoji, title) {
  if (action.setBadgeText) {
    action.setBadgeText({ text: emoji });
    action.setBadgeBackgroundColor?.({ color: "#2b2b2b" });
  }
  action.setTitle({ title });
}

// ----------------------------------------------------
// Poll Loop (minimal, low overhead)
// ----------------------------------------------------
setInterval(checkDownloads, 4000);
updateEmoji("idle");
checkDownloads();
