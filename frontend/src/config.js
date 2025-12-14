export const API_URL =
  process.env.REACT_APP_API_URL || "https://hubnuti-projekt-16.onrender.com/api";

export const MEDIA_URL =
  process.env.REACT_APP_MEDIA_URL || "https://hubnuti-projekt-16.onrender.com/media";

export const getImageUrl = (obrazek_url) => {
  const fallback = `${MEDIA_URL}/jidla/fallback.jpg`;
  if (!obrazek_url) return fallback;

  // если уже абсолютный URL — просто отдаём
  if (obrazek_url.startsWith("http")) {
    return obrazek_url;
  }

  // если приходит "/media/..."
  if (obrazek_url.startsWith("/media/")) {
    return `${MEDIA_URL}${obrazek_url.replace("/media", "")}`;
  }

  // если приходит "jidla/xxx.jpg" или просто "xxx.jpg"
  const clean = obrazek_url.replace(/^(\/?jidla\/)+/, "");

  return `${MEDIA_URL}/jidla/${clean}`;
};