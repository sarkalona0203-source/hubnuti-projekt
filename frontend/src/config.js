/// API_URL
export const API_URL =
  process.env.REACT_APP_API_URL || "http://localhost:8000/api";

// MEDIA_URL — ТОЛЬКО для реальных картинок из Django
export const MEDIA_URL =
  process.env.REACT_APP_MEDIA_URL ||
  API_URL.replace(/\/api$/, "") + "/media";

// 🔥 fallback — фронтендовый файл
const FALLBACK_IMAGE = "/fallback.jpg";

export const getImageUrl = (obrazek_url) => {
  if (!obrazek_url) return FALLBACK_IMAGE;

  if (obrazek_url.startsWith("http")) return obrazek_url;

  const clean = obrazek_url.replace(/^\/+/, "");
  return `${MEDIA_URL}/${clean}`;
};