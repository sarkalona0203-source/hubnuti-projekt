export const API_URL =
  process.env.REACT_APP_API_URL || "https://hubnuti-projekt-16.onrender.com/api";

export const MEDIA_URL =
  process.env.REACT_APP_MEDIA_URL || "https://hubnuti-projekt-16.onrender.com/media/jidla";

export const getImageUrl = (obrazek_url) => {
  const fallback = `${MEDIA_URL}/fallback.jpg`;

  if (!obrazek_url) return fallback;

  // если уже абсолютный URL — возвращаем как есть
  if (obrazek_url.startsWith("http")) return obrazek_url;

  // если путь начинается с "/media/jidla/" или "jidla/"
  const clean = obrazek_url.replace(/^\/?(media\/)?jidla\//, "");

  return `${MEDIA_URL}/${clean}`;
};