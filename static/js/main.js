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

  /* ===== Inquiry List (localStorage) ===== */
  const INQUIRY_KEY = 'hw_inquiry_list';

  function getInquiryList() {
    try { return JSON.parse(localStorage.getItem(INQUIRY_KEY)) || []; }
    catch (e) { return []; }
  }

  function saveInquiryList(list) {
    localStorage.setItem(INQUIRY_KEY, JSON.stringify(list));
  }

  function isInList(url) {
    return getInquiryList().some(function(item) { return item.url === url; });
  }

  function updateInquiryButtons() {
    document.querySelectorAll('.btn-inquiry').forEach(function(btn) {
      var url = btn.getAttribute('data-url');
      if (url && isInList(url)) {
        btn.classList.add('added');
        btn.disabled = true;
      }
    });
  }

  document.querySelectorAll('.btn-inquiry').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      var title = btn.getAttribute('data-title');
      var url   = btn.getAttribute('data-url');
      var image = btn.getAttribute('data-image');
      if (!title || !url) return;

      var list = getInquiryList();
      if (!isInList(url)) {
        list.push({ title: title, url: url, image: image || '', addedAt: Date.now() });
        saveInquiryList(list);
        btn.classList.add('added');
        btn.disabled = true;
      }
    });
  });

  updateInquiryButtons();
});
