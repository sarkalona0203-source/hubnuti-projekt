export const API_URL =
  process.env.REACT_APP_API_URL || "https://hubnuti-projekt-16.onrender.com/api";

export const MEDIA_URL =
  process.env.REACT_APP_MEDIA_URL || "http://localhost:8000/media";

export const getImageUrl = (obrazek_url) => {
  const fallback = `${MEDIA_URL}/jidla/fallback.jpg`;

  if (!obrazek_url) return fallback;

  // если абсолютный URL — оставляем как есть
  if (obrazek_url.startsWith("http")) return obrazek_url;

  // чистим ведущие слеши, чтобы не было двойного "jidla/jidla"
  const clean = obrazek_url.replace(/^\/+/, "");

  return `${MEDIA_URL}/${clean}`;
};