export const getImageUrl = (obrazek_url) => {
  if (!obrazek_url) return null;
  if (obrazek_url.startsWith("http")) return obrazek_url;

  // КАРТИНКИ ВСЕГДА С ФРОНТА
  return `/media/${obrazek_url.replace(/^\/+/, "")}`;
};