export const API_URL =
  process.env.REACT_APP_API_URL || "https://hubnuti-projekt-16.onrender.com/api";

export const MEDIA_URL =
  process.env.REACT_APP_MEDIA_URL || "https://hubnuti-projekt-16.onrender.com/media";

export const getImageUrl = (obrazek) => {
  if (!obrazek) return "https://via.placeholder.com/180";

  // ✔ Если полная ссылка — возвращаем как есть
  if (typeof obrazek === "string" && obrazek.startsWith("http")) {
    return obrazek;
  }

  // ✔ Добавляем если путь относительный
  return `${MEDIA_URL}/${obrazek}`;
};