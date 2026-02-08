export const API_URL =
  process.env.REACT_APP_API_URL ||
  "https://hubnuti-projekt-15.onrender.com/api";

export const MEDIA_BASE_URL =
  process.env.REACT_APP_MEDIA_URL ||
  "https://hubnuti-projekt-15.onrender.com/media";

export const getImageUrl = (obrazek_url) => {
  if (!obrazek_url) return null;
  if (obrazek_url.startsWith("http")) return obrazek_url;
  return `${MEDIA_BASE_URL}/${obrazek_url.replace(/^\/+/, "")}`;
};