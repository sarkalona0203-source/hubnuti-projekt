// config.js

export const API_URL =
  process.env.REACT_APP_API_URL || "http://localhost:8000/api";

export const getImageUrl = (obrazek_url) => {
  if (!obrazek_url) return null;
  if (obrazek_url.startsWith("http")) return obrazek_url;

  // картинки ТОЛЬКО из frontend/public/media
  return `/media/${obrazek_url.replace(/^\/+/, "")}`;
};