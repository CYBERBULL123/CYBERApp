document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('file');
    const filePreview = document.getElementById('filePreview');
    const progressBar = document.getElementById('progressBar');
    const progress = progressBar.querySelector('.progress');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const clearFilesButton = document.getElementById('clearFilesButton');

    // Allowed file types
    const allowedFileTypes = ['csv', 'txt', 'doc', 'docx', 'pdf', 'json', 'log'];

    // Drag-and-Drop Functionality
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        fileInput.files = e.dataTransfer.files;
        validateAndUpdateFilePreview();
    });

    // Clear files button
    clearFilesButton.addEventListener('click', () => {
        fileInput.value = ''; // Clear the file input
        filePreview.innerHTML = '<p>No files selected</p>'; // Reset the preview
    });

    // Browse Files
    uploadArea.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', () => {
        validateAndUpdateFilePreview();
    });

    // Validate file type and update file preview
    function validateAndUpdateFilePreview() {
        if (fileInput.files.length > 0) {
            const invalidFiles = [];
            let fileList = '';

            for (const file of fileInput.files) {
                const fileExtension = file.name.split('.').pop().toLowerCase();
                if (!allowedFileTypes.includes(fileExtension)) {
                    invalidFiles.push(file.name);
                } else {
                    fileList += `<p>${file.name} (${formatBytes(file.size)})</p>`;
                    readFileContent(file); // Read and display file content
                }
            }

            if (invalidFiles.length > 0) {
                // Redirect to error page if invalid files are found
                window.location.href = '/error';
                return;
            }

            filePreview.innerHTML = fileList;
        } else {
            filePreview.innerHTML = '<p>No files selected</p>';
        }
    }

    // Read and Display File Content
    function readFileContent(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            filePreview.innerHTML += `<pre>${content}</pre>`; // Display file content
        };
        reader.readAsText(file); // Read file as text
    }

    // Format File Size
    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Handle File Upload
    document.getElementById('uploadForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        progressBar.style.display = 'block';
        progress.style.width = '0%';
        loadingSpinner.style.display = 'block'; // Show loading spinner

        const formData = new FormData();
        for (const file of fileInput.files) {
            formData.append('file', file);
        }

        try {
            const response = await fetch('/index', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                // The backend will handle the redirection
                progress.style.width = '100%';
            } else {
                console.error('Upload failed');
                alert('Upload failed. Please try again.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        } finally {
            loadingSpinner.style.display = 'none'; // Hide loading spinner
        }
    });
});