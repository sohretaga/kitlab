const favoriteBookCount = true;
const favoriteContainer = document.getElementById('favorite-container');

const previewImg = (input) => {

    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById('profile-img').src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    };
};


(
    async () => {
        const response = await fetch('/api/get-user-favorites', {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        if (response.ok) {
            const data = await response.json();
            if (data.books.length) {
                const books = data.books.map(element => {
                    element['id'] = element.book_id;
                    return element;
                });

                appendBooks(books, favoriteContainer);
                document.getElementById('no-favorites').style.display = 'none';
            };
        };
    }
)()