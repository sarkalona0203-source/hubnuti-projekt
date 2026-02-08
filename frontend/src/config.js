// config.js
export const API_URL =
  process.env.REACT_APP_API_URL || "https://hubnuti-projekt-15.onrender.com/api";

// getImageUrl для фронта — берём из public/media
export const getImageUrl = (obrazek_url) => {
  if (!obrazek_url) return null;
  if (obrazek_url.startsWith("http")) return obrazek_url; // полный URL уже есть
  // полный путь к продакшен-бекенду, где реально лежат медиа
  return `https://hubnuti-projekt-15.onrender.com/media/${obrazek_url.replace(/^\/+/, "")}`;
};