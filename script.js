document.addEventListener('DOMContentLoaded', () => {
  const header = document.getElementById('siteHeader');
  const hero = document.querySelector('.hero');
  const navToggle = document.getElementById('navToggle');
  const mainNav = document.getElementById('mainNav');

  function updateHeader() {
    if (!header) return;
    const threshold = hero ? hero.offsetHeight - 80 : 80;
    header.classList.toggle('is-scrolled', window.scrollY > threshold);
  }

  updateHeader();
  window.addEventListener('scroll', updateHeader, { passive: true });

  if (navToggle && mainNav) {
    navToggle.addEventListener('click', () => {
      const isOpen = mainNav.classList.toggle('is-open');
      navToggle.classList.toggle('is-open', isOpen);
      header.classList.toggle('menu-open', isOpen);
      navToggle.setAttribute('aria-expanded', String(isOpen));
    });

    mainNav.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        mainNav.classList.remove('is-open');
        navToggle.classList.remove('is-open');
        header.classList.remove('menu-open');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });

    window.addEventListener('resize', () => {
      if (window.innerWidth > 720 && mainNav.classList.contains('is-open')) {
        mainNav.classList.remove('is-open');
        navToggle.classList.remove('is-open');
        header.classList.remove('menu-open');
        navToggle.setAttribute('aria-expanded', 'false');
      }
    });
  }
});