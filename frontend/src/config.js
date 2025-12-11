export const API_URL =
  process.env.REACT_APP_API_URL || "https://hubnuti-projekt-16.onrender.com/api";

export const MEDIA_URL =
  process.env.REACT_APP_MEDIA_URL || "https://hubnuti-projekt-16.onrender.com/media";

export const getImageUrl = (obrazek) => {
  if (!obrazek) return `${MEDIA_URL}/jidla/fallback.jpg`; // fallback через MEDIA_URL
  return `${MEDIA_URL}/jidla/${obrazek}`;                 // картинки через MEDIA_URL
};