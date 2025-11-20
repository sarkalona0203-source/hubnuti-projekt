import React, { useState } from "react";

export default function ImageWithFallback({ src, alt, className }) {
  const [error, setError] = useState(false);

  return (
    <img
      src={error ? "/fallback.jpg" : src}
      alt={alt}
      className={className}
      onError={() => setError(true)}
    />
  );
}