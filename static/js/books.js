let currentPage = 1;
const loadMoreButton = document.getElementById('load-more-btn');
const bookContainer = document.getElementById('book-container');
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

async function fetchBooks(page) {
    try {
        const response = await fetch(`/api/load-more-book?page=${page}`);
        if (!response.ok) throw new Error('Failed to fetch books');
        
        const data = await response.json();
        appendBooks(data.books);

        if (!data.has_next) {
            loadMoreButton.disabled = true;
            loadMoreButton.innerText = 'Bu qədər :)';
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function appendBooks(books) {
    books.forEach(book => {
        // Showcase main div
        const showcase = document.createElement('div');
        showcase.classList.add('showcase');

        // Showcase banner
        const showcaseBanner = document.createElement('div');
        showcaseBanner.classList.add('showcase-banner');

        // Image link
        const imgBox = document.createElement('a');
        imgBox.classList.add('showcase-img-box');
        imgBox.href = book.is_approved ? `/book/${book.slug}` : '#';

        // Cover image link
        const defaultImg = document.createElement('img');
        defaultImg.src = `/media/${book.cover_photo}`;
        defaultImg.alt = book.name;
        defaultImg.width = 200;
        defaultImg.height = 200;
        defaultImg.loading = 'lazy';
        defaultImg.classList.add('product-img', 'default');

        imgBox.appendChild(defaultImg);

        // Hover image link
        const hoverImg = document.createElement('img');
        hoverImg.src = book.hover_image ? `/media/${book.hover_image}` : `/media/${book.cover_photo}`;
        hoverImg.alt = book.name;
        hoverImg.width = 200;
        hoverImg.height = 200;
        hoverImg.loading = 'lazy';
        hoverImg.classList.add('product-img', 'hover');

        imgBox.appendChild(hoverImg);
        showcaseBanner.appendChild(imgBox);

        // Status badge
        if (!book.is_approved) {
            const badge = document.createElement('p');
            badge.classList.add('showcase-badge', 'angle', 'amber');
            badge.textContent = 'Gözləyir';
            showcaseBanner.appendChild(badge);
        } else if (book.new) {
            const badge = document.createElement('p');
            badge.classList.add('showcase-badge', 'angle', 'pink');
            badge.textContent = 'Yeni';
            showcaseBanner.appendChild(badge);
        }

        // Showcase actions
        const showcaseActions = document.createElement('div');
        showcaseActions.classList.add('showcase-actions');

        // Mobile showcase actions
        const mobileShowcaseActions = document.createElement('div');
        mobileShowcaseActions.classList.add('mobile-showcase-actions');

        ['heart-outline', 'repeat-outline', 'chatbubble-ellipses-outline'].forEach(iconName => {
            const button = document.createElement('button');
            button.classList.add('btn-action');

            if (iconName == 'heart-outline') {
                button.onclick = () => favorite(book.id);
                button.classList.add(`favorite-btn-${book.id}`);

                if (book.is_favorite) {
                    button.classList.add('favorite');
                };
            };

            const icon = document.createElement('ion-icon');
            icon.setAttribute('name', iconName);

            button.appendChild(icon);
            const mobileButton = button.cloneNode(true);

            mobileShowcaseActions.appendChild(mobileButton);
            showcaseActions.appendChild(button);
        });

        showcaseBanner.appendChild(showcaseActions);
        showcase.appendChild(showcaseBanner);

        // Showcase content
        const showcaseContent = document.createElement('div');
        showcaseContent.classList.add('showcase-content');

        const categoryLink = document.createElement('a');
        categoryLink.classList.add('showcase-category');
        categoryLink.textContent = book.category_name;
        showcaseContent.appendChild(categoryLink);


        const titleLink = document.createElement('a');
        titleLink.href = `/book/${book.slug}`;
        const title = document.createElement('h3');
        title.classList.add('showcase-title');
        title.textContent = book.name;
        titleLink.appendChild(title);
        showcaseContent.appendChild(titleLink);

        showcaseContent.appendChild(mobileShowcaseActions);

        const priceBox = document.createElement('div');
        priceBox.classList.add('price-box');
        const price = document.createElement('p');
        price.classList.add('price');
        price.textContent = `${book.price}₼`;
        priceBox.appendChild(price);
        showcaseContent.appendChild(priceBox);

        showcase.appendChild(showcaseContent);
        bookContainer.appendChild(showcase);
    });
}

loadMoreButton.addEventListener('click', () => {
    currentPage++;
    fetchBooks(currentPage);
});

async function favorite(bookId) {
    try {
        const response = await fetch('/api/favorite', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                book_id: bookId
            })
        });
    
        if (response.ok) {
            const data = await response.json();
            const favoriteBtns = document.querySelectorAll(`.favorite-btn-${bookId}`);
            favoriteBtns.forEach(btn => {
                btn.classList.toggle('favorite');
            });

            if (data.created) {
                notyf.open({
                    type: 'info',
                    message: 'Sevimlilərə əlavə edildi'
                });
            } else {
                notyf.open({
                    type: 'info',
                    message: 'Sevimlilərdən silindi'
                });
            }

        } else {
            console.error('Error: ', response.status);
        }
    } catch (error) {
        console.error(error);
    };
};