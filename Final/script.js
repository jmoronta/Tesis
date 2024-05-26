document.getElementById('fileInput').addEventListener('change', function(event) {
    const file = event.target.files[0];
    const reader = new FileReader();
  
    reader.onload = function(event) {
      const img = document.createElement('img');
      img.src = event.target.result;
      document.getElementById('imagePreview').innerHTML = '';
      document.getElementById('imagePreview').appendChild(img);
    }
  
    reader.readAsDataURL(file);
  });
  