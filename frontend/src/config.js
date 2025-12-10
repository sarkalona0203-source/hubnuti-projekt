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
 * Автоматически заменяет домен -16 на -17.
 */
export const getImageUrl = (obrazek) => {
  if (!obrazek) return "https://via.placeholder.com/180";

  // Если строка
  if (typeof obrazek === "string") {
    // Подменяем домен, если это старый хост
    const updatedUrl = obrazek.replace(
      "https://hubnuti-projekt-16.onrender.com",
      "https://hubnuti-projekt-17.onrender.com"
    );
    return updatedUrl.startsWith("http") ? updatedUrl : `${MEDIA_URL}/${updatedUrl}`;
  }

  // Если объект с полем url
  if (obrazek.url) {
    const updatedUrl = obrazek.url.replace(
      "https://hubnuti-projekt-16.onrender.com",
      "https://hubnuti-projekt-17.onrender.com"
    );
    return updatedUrl.startsWith("http") ? updatedUrl : `${MEDIA_URL}/${updatedUrl}`;
  }

  return "https://via.placeholder.com/180";
};