export const API_URL =
  process.env.REACT_APP_API_URL || "https://hubnuti-projekt-16.onrender.com/api";

export const MEDIA_URL =
  process.env.REACT_APP_MEDIA_URL || "https://hubnuti-projekt-16.onrender.com/media";

export const getImageUrl = (obrazek) => {
  if (!obrazek) return `${MEDIA_URL}/jidla/fallback.jpg`;

  // Если это уже URL (начинается с http), возвращаем как есть
  if (obrazek.startsWith("http")) return obrazek;

  // Если имя файла начинается с 'jidla/', не добавляем снова
  if (obrazek.startsWith("jidla/")) return `${MEDIA_URL}/${obrazek}`;

  return `${MEDIA_URL}/jidla/${obrazek}`;
};