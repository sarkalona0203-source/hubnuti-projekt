// Базовый URL для медиа (теперь берём из public)
export const MEDIA_URL = process.env.REACT_APP_MEDIA_URL || "/media";

// Функция для построения пути к картинке
export const getImageUrl = (obrazek) => {
  if (!obrazek) return "https://via.placeholder.com/180";

  // Если строка — просто путь к файлу в /media/jidla/
  if (typeof obrazek === "string") {
    return obrazek.startsWith("http") ? obrazek : `${MEDIA_URL}/jidla/${obrazek}`;
  }

  // Если объект с полем url
  if (obrazek.url) {
    return obrazek.url.startsWith("http") ? obrazek.url : `${MEDIA_URL}/jidla/${obrazek.url}`;
  }

  return "https://via.placeholder.com/180";
};