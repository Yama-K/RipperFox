console.log("[yt-dlp] Content script active on", location.hostname);

// Helper: find a usable media element
function findMediaElement(target) {
  if (!target) return null;

  if (target.tagName === "VIDEO" || target.tagName === "IMG") return target;

  // Sometimes nested in containers (like <a> or <div>)
  return target.closest("video, img");
}

  const media = findMediaElement(e.target);
  if (!media) return;

  // Determine the source URL
  const src =
    media.currentSrc ||
    media.src ||
    media.poster ||
    (media.querySelector("source") ? media.querySelector("source").src : null);

  if (!src) return;

  e.preventDefault();
  e.stopPropagation();

  const url = new URL(src, location.href).toString();
  const site = location.hostname;
  let mediaType = "video";

  // Detect GIFs
  if (url.match(/\.gif($|\?)/i) || (media.tagName === "IMG" && media.src.includes(".gif"))) {
    mediaType = "gif";
  }

  console.log(`[yt-dlp] Alt+click download on ${site}: ${url} (${mediaType})`);

  browser.runtime.sendMessage({
    type: "yt-dlp-download",
    url,
    site,
    mediaType
  });
});
