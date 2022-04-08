const fileInput = document.querySelector('#fileUpload input[type=file]');
  fileInput.onchange = () => {
    if (fileInput.files.length > 0) {
      const fileName = document.querySelector('#fileUpload .file-name');
      fileName.textContent = fileInput.files[0].name;
    }
  }