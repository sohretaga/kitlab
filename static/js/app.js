'use strict';

// modal variables
// const modal = document.querySelector('[data-modal]');
// const modalCloseBtn = document.querySelector('[data-modal-close]');
// const modalCloseOverlay = document.querySelector('[data-modal-overlay]');

// modal function
// const modalCloseFunc = function () { modal.classList.add('closed') }

// modal eventListener
// modalCloseOverlay.addEventListener('click', modalCloseFunc);
// modalCloseBtn.addEventListener('click', modalCloseFunc);





// notification toast variables
// const notificationToast = document.querySelector('[data-toast]');
// const toastCloseBtn = document.querySelector('[data-toast-close]');

// notification toast eventListener
// toastCloseBtn.addEventListener('click', function () {
//   notificationToast.classList.add('closed');
// });





// mobile menu variables
const mobileMenuOpenBtn = document.querySelectorAll('[data-mobile-menu-open-btn]');
const mobileMenu = document.querySelectorAll('[data-mobile-menu]');
const mobileMenuCloseBtn = document.querySelectorAll('[data-mobile-menu-close-btn]');
const overlay = document.querySelector('[data-overlay]');

for (let i = 0; i < mobileMenuOpenBtn.length; i++) {

  // mobile menu function
  const mobileMenuCloseFunc = function () {
    mobileMenu[i].classList.remove('active');
    overlay.classList.remove('active');
  }

  mobileMenuOpenBtn[i].addEventListener('click', function () {
    mobileMenu[i].classList.add('active');
    overlay.classList.add('active');
  });

  mobileMenuCloseBtn[i].addEventListener('click', mobileMenuCloseFunc);
  overlay.addEventListener('click', mobileMenuCloseFunc);

}





// accordion variables
const accordionBtn = document.querySelectorAll('[data-accordion-btn]');
const accordion = document.querySelectorAll('[data-accordion]');

for (let i = 0; i < accordionBtn.length; i++) {

  accordionBtn[i].addEventListener('click', function () {

    const clickedBtn = this.nextElementSibling.classList.contains('active');

    for (let i = 0; i < accordion.length; i++) {

      if (clickedBtn) break;

      if (accordion[i].classList.contains('active')) {

        accordion[i].classList.remove('active');
        accordionBtn[i].classList.remove('active');

      }

    }

    this.nextElementSibling.classList.toggle('active');
    this.classList.toggle('active');

  });

}

// search book name
const searchInput = document.getElementById("search-field");
const dropdownMenu = document.getElementById("search-dropdown-menu");

searchInput.addEventListener("input", () => {
  const query = searchInput.value.toLowerCase();

  if (query.trim() === "") {
    dropdownMenu.style.display = "none";
    return;
  }

  fetch(`/api/search-book-name?q=${query}`)
    .then(response => response.json())
    .then(data => {
      const books = data.books;
      dropdownMenu.innerHTML = "";

      if (books.length) {
        books.forEach(item => {
          const a = document.createElement("a");
          a.className = "search-dropdown-item";
          a.textContent = item.name;
          a.href = `/book/${item.slug}`;
          dropdownMenu.appendChild(a);
        });
      }

      dropdownMenu.style.display = "block";
    });

});

document.addEventListener("click", (event) => {
  if (!event.target.closest(".header-search-container")) {
    dropdownMenu.style.display = "none";
  }
});

async function updadeMessageCount(data) {
  if (data.message) {
    const allNewMessageCount = document.querySelectorAll('.count');
    allNewMessageCount.forEach(count => {
        let currentCount = parseInt(count.textContent) || 0;
        let updatedCount = currentCount + 1;
        count.textContent = updatedCount;
        count.style.display = 'unset';
    });
  }
  
}

const loggedUserId = document.querySelector('meta[name="logged-user"]').getAttribute('content');
const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
var notificationSocket;

if (loggedUserId) {
  notificationSocket = new WebSocket(`${protocol}${window.location.host}/ws/notification/${loggedUserId}/`);

  notificationSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    updadeMessageCount(data);
  };
}