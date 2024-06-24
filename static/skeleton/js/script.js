const fileInput = document.getElementById('file');
const fileUploadLabel = document.getElementById('fileUploadLabel');
const filesUploadedContainer = document.getElementById('filesUploaded');
const sendButton = document.getElementById('sendButton');
const cycleTypeSelect = document.getElementById('SelectOEM');
const currentThresholdInput = document.getElementById('member4');

let uploadedFiles = [];

fileUploadLabel.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileUploadLabel.classList.add('drag-over');
});

fileUploadLabel.addEventListener('dragleave', () => {
    fileUploadLabel.classList.remove('drag-over');
});

fileUploadLabel.addEventListener('drop', (e) => {
    e.preventDefault();
    fileUploadLabel.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    handleFiles(files);
});

fileInput.addEventListener('change', () => {
    const files = fileInput.files;
    handleFiles(files);
    fileInput.value = ''; // Clear the input
});

function handleFiles(files) {
    const fileList = Array.from(files);

    fileList.forEach((file) => {
        const fileName = truncateFileName(file.name, 35);
        uploadedFiles.push(file); // Add files to the global array

        const fileItem = document.createElement('div');
        fileItem.classList.add('file-item');
        fileItem.innerHTML =
            `<div class="file">
                <img src="https://img.icons8.com/?size=256&id=11651&format=png" alt=""/>
                <span class="file-name">${fileName}</span>
                <div class="uploaded">
                    <img id="checkIcon" src="https://img.icons8.com/?size=256&id=7690&format=png" alt=""/>
                    <p>Uploaded</p>
                </div>
                <button class="delete-button" data-index="${uploadedFiles.length - 1}">Delete</button>
            </div>`;

        filesUploadedContainer.appendChild(fileItem);
    });

    updateDeleteButtons();
}

function updateDeleteButtons() {
    const deleteButtons = document.querySelectorAll('.delete-button');
    deleteButtons.forEach(button => {
        button.removeEventListener('click', handleDeleteButtonClick); // Remove previous listeners to avoid duplication
        button.addEventListener('click', handleDeleteButtonClick);
    });
}

function handleDeleteButtonClick(e) {
    const fileItem = e.target.closest('.file-item');
    const index = parseInt(e.target.dataset.index, 10);
    uploadedFiles.splice(index, 1); // Remove the file from the global array
    fileItem.remove();
    refreshFileItems();
}

function refreshFileItems() {
    const fileItems = document.querySelectorAll('.file-item');
    fileItems.forEach((fileItem, index) => {
        const deleteButton = fileItem.querySelector('.delete-button');
        deleteButton.setAttribute('data-index', index);
    });
}

function truncateFileName(name, maxLength) {
    return name.length > maxLength ? name.substring(0, maxLength) + '...' : name;
}

sendButton.addEventListener('click', () => {
    const cycleType = cycleTypeSelect.value;
    const currentThreshold = currentThresholdInput.value;

    const formData = new FormData();
    formData.append('cycle_type', cycleType);
    formData.append('current_threshold', currentThreshold);

    uploadedFiles.forEach((file) => {
        formData.append('files', file);
    });

    fetch('/analyze/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => {
        const contentDisposition = response.headers.get('Content-Disposition');
        const filename = contentDisposition.split('filename=')[1].replace(/"/g, '');
        return response.blob().then(blob => ({ filename, blob }));
    })
    .then(({ filename, blob }) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});
