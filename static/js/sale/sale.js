// Get the CSRF token from the meta tag in the HTML
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

function previewImage(event) {
    var reader = new FileReader();
    reader.onload = function(){
        var output = document.getElementById('image-preview');
        output.src = reader.result;
        output.style.display = 'block'; // Resim yüklendiğinde önizlemeyi göster
    };
    reader.readAsDataURL(event.target.files[0]);
}


document.getElementById("image-input").addEventListener("change", function(event) {
    const imagePreviewContainer = document.getElementById("image-preview");
    const files = event.target.files;
    
    if (files.length > 4 || imagePreviewContainer.children.length + files.length > 4) {
      alert("En fazla 4 resim seçebilirsiniz.");
      event.target.value = "";
      return;
    }
  
    Array.from(files).forEach((file) => {
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
          if (imagePreviewContainer.children.length < 4) {
            document.getElementById("image-input").disabled = false;
          }
        });
  
        imageContainer.appendChild(imageElement);
        imageContainer.appendChild(removeButton);
        imagePreviewContainer.appendChild(imageContainer);
  
        if (imagePreviewContainer.children.length >= 4) {
          document.getElementById("image-input").disabled = true;
        }
      };
      reader.readAsDataURL(file);
    });
    
    event.target.value = "";
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