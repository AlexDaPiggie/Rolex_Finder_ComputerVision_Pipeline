import { useState, useEffect } from "react";
import "./NavBar.css";

function NavBar({ currentPage, onPageChange }) {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = (e) => {
      const target = e.target;
      let scrollTop = 0;
      if (target === document || target === window) {
        scrollTop = window.scrollY;
      } else if (target && target.scrollTop !== undefined) {
        scrollTop = target.scrollTop;
      }
      setIsScrolled(scrollTop > 15);
    };

    // Capturing phase listener catches scroll events from nested containers like .prediction-panel
    window.addEventListener("scroll", handleScroll, true);
    return () => {
      window.removeEventListener("scroll", handleScroll, true);
    };
  }, []);

  return (
    <nav className={`nav-bar ${isScrolled ? "scrolled" : ""}`}>
      <button
        className={`nav-link ${currentPage === "home" ? "active" : ""}`}
        onClick={() => onPageChange("home")}
      >
        Home
      </button>
      <button
        className={`nav-link ${currentPage === "authors" ? "active" : ""}`}
        onClick={() => onPageChange("authors")}
      >
        Authors
      </button>
    </nav>
  );
}

export default NavBar;
