// config.js
export const API_URL =
  process.env.REACT_APP_API_URL || "https://hubnuti-projekt-16.onrender.com/api";

export const MEDIA_URL =
  process.env.REACT_APP_MEDIA_URL || "/media";

export const getImageUrl = (obrazek_url) => {
  const fallback = `${MEDIA_URL.replace(/\/$/, "")}/jidla/fallback.jpg`;

  if (!obrazek_url) return fallback;

  if (obrazek_url.startsWith("http")) return obrazek_url;

  const clean = obrazek_url.replace(/^\/+/, "");
  return `${MEDIA_URL.replace(/\/$/, "")}/${clean}`;
};