const header = document.getElementById('siteHeader');
const hero = document.querySelector('.hero');

function updateHeader() {
  const threshold = hero ? hero.offsetHeight - 80 : 80;
  header.classList.toggle('is-scrolled', window.scrollY > threshold);
}
updateHeader();
window.addEventListener('scroll', updateHeader, { passive: true });

const navToggle = document.getElementById('navToggle');
const mainNav = document.getElementById('mainNav');

navToggle.addEventListener('click', () => {
  const isOpen = mainNav.classList.toggle('is-open');
  navToggle.setAttribute('aria-expanded', String(isOpen));
});

mainNav.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    mainNav.classList.remove('is-open');
    navToggle.setAttribute('aria-expanded', 'false');
  });
});