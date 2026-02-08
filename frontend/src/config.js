// config.js

export const API_URL =
  process.env.REACT_APP_API_URL ||
  "https://hubnuti-projekt-15.onrender.com/api";

// ⬇️ ЕДИНСТВЕННЫЙ источник картинок
export const FRONTEND_MEDIA_URL =
  "https://hubnuti-projekt-15.onrender.com/media";

export const getImageUrl = (obrazek_url) => {
  if (!obrazek_url) return null;

  // если пришёл полный URL — вырезаем всё до /media/
  const filename = obrazek_url.includes("/media/")
    ? obrazek_url.split("/media/").pop()
    : obrazek_url;

  return `${FRONTEND_MEDIA_URL}/${filename.replace(/^\/+/, "")}`;
};