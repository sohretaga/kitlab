function previewImage(event) {
    var reader = new FileReader();
    reader.onload = function(){
        var output = document.getElementById('image-preview');
        output.src = reader.result;
        output.style.display = 'block'; // Resim yüklendiğinde önizlemeyi göster
    };
    reader.readAsDataURL(event.target.files[0]);
}