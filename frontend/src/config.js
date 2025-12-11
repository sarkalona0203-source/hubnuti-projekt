export const API_URL =
  process.env.REACT_APP_API_URL || "https://hubnuti-projekt-16.onrender.com/api";

export const MEDIA_URL =
  process.env.REACT_APP_MEDIA_URL || "https://hubnuti-projekt-16.onrender.com/media";

export const getImageUrl = (obrazek) => {
  const fallback = `${MEDIA_URL}/jidla/fallback.jpg`;

  if (!obrazek) return fallback;

  // Убираем все дублирующиеся "jidla/" в начале
  let cleanObrazek = obrazek.replace(/^(\/?jidla\/)+/, "");

  return `${MEDIA_URL}/jidla/${cleanObrazek}`;
};