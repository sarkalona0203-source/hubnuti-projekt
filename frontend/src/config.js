// config.js

// Базовый URL API
export const API_URL =
  process.env.REACT_APP_API_URL ||
  "https://hubnuti-projekt-16.onrender.com/api";

// Базовый URL для медиа (картинок)
export const MEDIA_URL =
  process.env.REACT_APP_MEDIA_URL ||
  "https://hubnuti-projekt-17.onrender.com/media";

/**
 * Функция для построения корректного пути к картинке.
 * Принимает объект или строку и возвращает полный URL.
 */
export const getImageUrl = (obrazek) => {
  if (!obrazek) return "https://via.placeholder.com/180";

  if (typeof obrazek === "string") {
    return obrazek.startsWith("http") ? obrazek : `${MEDIA_URL}/${obrazek}`;
  }

  if (obrazek.url) {
    return obrazek.url.startsWith("http") ? obrazek.url : `${MEDIA_URL}/${obrazek.url}`;
  }

  return "https://via.placeholder.com/180";
};
