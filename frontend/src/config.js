// config.js

// API_URL: берём из .env, иначе localhost для dev
export const API_URL =
  process.env.REACT_APP_API_URL || "http://localhost:8000/api";

// MEDIA_URL: тот же хост, что и API, просто заменяем /api на /media
export const MEDIA_URL =
  process.env.REACT_APP_MEDIA_URL || API_URL.replace(/\/api$/, "") + "/media";

export const getImageUrl = (obrazek_url) => {
  const fallback = `${MEDIA_URL}/fallback.jpg`;

  if (!obrazek_url) return fallback;
  if (obrazek_url.startsWith("http")) return obrazek_url;

  const clean = obrazek_url.replace(/^\/+/, "");
  return `${MEDIA_URL}/${clean}`;
};