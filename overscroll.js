// Bouncing past the bottom of the page reveals the plain background below the
// footer's drawing. CSS can only turn bouncing off at both ends, so turn it off
// whenever the page is scrolled away from the top, where bouncing stays.
function updateOverscroll() {
  document.documentElement.style.overscrollBehaviorY = scrollY > 0 ? 'none' : '';
}

updateOverscroll();
addEventListener('scroll', updateOverscroll, { passive: true });
