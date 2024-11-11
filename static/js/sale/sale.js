// Get the CSRF token from the meta tag in the HTML
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

function previewImage(event) {
    var reader = new FileReader();
    reader.onload = function(){
        var output = document.getElementById('image-preview');
        output.src = reader.result;
        output.style.display = 'block';
    };
    reader.readAsDataURL(event.target.files[0]);
}

function changeMainImage(imageContainer) {
  const mainImagePreviewContainer = document.getElementById('main-image-preview');
  const currentImgSrc = mainImagePreviewContainer.querySelector('img').src;
  mainImagePreviewContainer.querySelector('img').src = imageContainer.target.src;
  imageContainer.target.src = currentImgSrc;
}

async function setImageToFileInput(imgElement) {
  // 1. Get the Base64 data of the image
  const base64Data = imgElement.src;

  // 2. Decode Base64 data and convert it to binary data
  const res = await fetch(base64Data);
  const blob = await res.blob();

  // 3. Convert Blob data to File object
  const file = new File([blob], "book_image.jpg", { type: blob.type });

  // 4. Add the File object to the input as a FileList
  const dataTransfer = new DataTransfer();
  dataTransfer.items.add(file);
  const fileInput = document.createElement('input');
  fileInput.type = 'file';
  fileInput.accept = 'image/*';
  fileInput.name = 'cover_photo';
  fileInput.files = dataTransfer.files;

  // 5. Append the file input to a container element on the page
  const imageInputContainer = document.getElementById('image-input-container');
  imageInputContainer.appendChild(fileInput);
}

function handleImageInputs() {
  const imageInputContainer = document.getElementById('image-input-container');
  imageInputContainer.innerHTML = '';
  const mainImage = document.querySelector('#main-image-preview img');
  const otherImages = document.querySelectorAll('#image-preview img');

  if (mainImage) {
    setImageToFileInput(mainImage);
  }

}

document.getElementById("image-input").addEventListener("change", function(event) {
    const mainImageContainer = document.getElementById('main-image-container');
    const mainImagePreviewContainer = document.getElementById('main-image-preview');
    const imagePreviewContainer = document.getElementById("image-preview");
    const uploadedImageCount = document.querySelectorAll('#book-images img').length;
    let files = event.target.files;

    // If the number of selected images is more than 5, only take the first 5
    if (files.length > 5) {
      files = Array.from(files).slice(0, 5);
    }

    // If the current uploaded image count is less than 5 and the total of newly selected files will exceed 5,
    // select only the missing ones
    if (uploadedImageCount < 5 && uploadedImageCount + files.length > 5) {
      // Limit the number of files to a maximum of 5 images in total
      const remainingSlots = 5 - uploadedImageCount;
      files = Array.from(files).slice(0, remainingSlots);
      notyf.open({
        type: 'info',
        message: `${remainingSlots} şəkil əlavə edildi. Ən çox 5 şəkil yükləyə bilərsiniz!`
      });
    };

    // If the total number of images reaches or exceeds 5, stop uploading and give warning
    if (uploadedImageCount >= 5 || uploadedImageCount + files.length > 5) {
      notyf.open({
        type: 'info',
        message: 'Ən çox 5 şəkil yükləyə bilərsiniz!'
      });
      return;
    };
  
    Array.from(files).forEach((file, index) => {
      const reader = new FileReader();
      reader.onload = function(e) {
        const imageContainer = document.createElement("div");
        imageContainer.classList.add("image-container");
  
        const imageElement = document.createElement("img");
        imageElement.src = e.target.result;
        
        const removeButton = document.createElement("button");
        removeButton.innerText = "×";
        removeButton.classList.add("remove-image");
  
        removeButton.addEventListener("click", function() {
          imageContainer.remove();
          if (uploadedImageCount < 5) {
            document.getElementById("image-input").disabled = false;
          }
        });

        if(index == 0 && mainImageContainer.style.display != 'inline') {
          imageContainer.appendChild(imageElement);
          mainImageContainer.style.display = 'inline';
          mainImagePreviewContainer.appendChild(imageContainer)
        } else {
          imageElement.addEventListener('click', changeMainImage);
          imageContainer.appendChild(imageElement);
          imageContainer.appendChild(removeButton);
          imagePreviewContainer.appendChild(imageContainer);
        }
  
        if (uploadedImageCount >= 5) {
          document.getElementById("image-input").disabled = true;
        }
      };
      reader.readAsDataURL(file);
    });
    
    event.target.value = "";
    setTimeout(handleImageInputs, 50);
  });

function listSubCategories(data) {
  const subCategorySelect = document.getElementById('subcategory');
  const defaultOption = document.createElement('option');
  defaultOption.value = '';
  defaultOption.textContent = 'Seç...';
  subCategorySelect.innerHTML = '';
  subCategorySelect.appendChild(defaultOption);

  if (data) {
    data.forEach(category => {
      const option = document.createElement('option');
      option.value = category.id;
      option.textContent = category.name;
      subCategorySelect.appendChild(option);
    });
  };
};
  

async function getSubCategories(category) {
  const url = "/get-sub-categories";
  const categoryId = category.value;
  
  if (categoryId) {
    const payload = {'id': categoryId};

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
      }

      const data = await response.json()
      listSubCategories(data);
    } catch (error) {
      console.error(error.message);
    }
  } else {
    listSubCategories(false)
  }

};

function checkFormValid(button) {
  const nameInput = document.getElementById('book-name').value;
  const categoryInput = document.getElementById('category').value;
  const subCategoryInput = document.getElementById('subcategory').value;
  const languageInput = document.getElementById('language').value;
  const cityInput = document.getElementById('city').value;
  const conditionInput = document.getElementById('condition').value;
  const priceInput = document.getElementById('price').value;
  const descriptionInput = document.getElementById('book-description').value;

  if (!nameInput) {
    notyf.error('Kitab adı yazılmalıdır!');
    return;
  }

  else if (!categoryInput) {
    notyf.error('Kateqoriya seçilməlidir!');
    return;
  }

  else if (!subCategoryInput) {
    notyf.error('Alt kateqoriya seçilməlidir!');
    return;
  }

  else if (!languageInput) {
    notyf.error('Kitab dili seçilməlidir!');
    return;
  }

  else if (!cityInput) {
    notyf.error('Şəhər seçilməlidir!');
    return;
  }

  else if (!conditionInput) {
    notyf.error('Kitab vəziyyəti seçilməlidir!');
    return;
  }

  else if (!priceInput) {
    notyf.error('Kitab qiyməti yazılmalıdır!');
    return;
  }

  else if (!descriptionInput) {
    notyf.error('Kitab açıqlaması yazılmalıdır!');
    return;
  }

  const mainImagePreviewContainer = document.getElementById('main-image-preview');
  if (!mainImagePreviewContainer.children.length){
    notyf.error('Kitabın ən az bir şəkilini əlavə etməlisiniz!');
    return;
  }

  const form = button.closest('form');
  form.submit();
};