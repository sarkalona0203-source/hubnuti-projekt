export const MEDIA_URL =
  process.env.REACT_APP_MEDIA_URL ||
  "https://hubnuti-projekt-16.onrender.com/media";

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