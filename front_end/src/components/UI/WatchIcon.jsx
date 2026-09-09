function WatchIcon() {
  return (
    <svg
      className="watch-icon"
      width="78"
      height="78"
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Top Strap */}
      <rect
        x="25"
        y="-4"
        width="14"
        height="18"
        rx="3"
        stroke="currentColor"
        strokeWidth="1.5"
      />

      {/* Watch Case */}
<ellipse
  cx="32"
  cy="32"
  rx="17"
  ry="18"
  stroke="currentColor"
  strokeWidth="1.5"
  fill="none"
/>

      {/* Dial */}
      <circle
        cx="32"
        cy="32"
        r="11"
        stroke="currentColor"
        strokeWidth="1.5"
      />

      {/* Hands */}
      <line
        x1="32"
        y1="32"
        x2="32"
        y2="25"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />

      <line
        x1="32"
        y1="32"
        x2="38"
        y2="35"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />

      {/* Bottom Strap */}
      <rect
        x="25"
        y="50"
        width="14"
        height="18"
        rx="3"
        stroke="currentColor"
        strokeWidth="1.5"
      />
    </svg>
  );
}

export default WatchIcon;