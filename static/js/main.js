document.addEventListener('DOMContentLoaded', function() {
  const toggle = document.querySelector('.mobile-toggle');
  const nav = document.querySelector('.main-nav');
  const dropdowns = document.querySelectorAll('.has-dropdown');

  if (toggle && nav) {
    toggle.addEventListener('click', function() {
      const isOpen = nav.classList.toggle('active');
      toggle.setAttribute('aria-expanded', isOpen);
    });
  }

  dropdowns.forEach(function(item) {
    const link = item.querySelector('.nav-link');
    if (link) {
      link.addEventListener('click', function(e) {
        if (window.innerWidth <= 900) {
          e.preventDefault();
          item.classList.toggle('active');
        }
      });
    }
  });

  document.addEventListener('click', function(e) {
    if (!e.target.closest('.site-header')) {
      if (nav) nav.classList.remove('active');
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
    }
  });
});
