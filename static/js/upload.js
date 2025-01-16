document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('file');
    const filePreview = document.getElementById('filePreview');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const clearFilesButton = document.getElementById('clearFilesButton');
    const generateReportButton = document.getElementById('generateReportButton');
    const extractedTextInput = document.getElementById('extractedText');

    // Allowed file types
    const allowedFileTypes = ['csv', 'txt', 'log', 'pdf', 'doc', 'docx', 'html', 'xml', 'json'];

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
        handleFileUpload();
    });

    // Clear files button
    clearFilesButton.addEventListener('click', () => {
        fileInput.value = ''; // Clear the file input
        filePreview.innerHTML = '<p>No files selected</p>'; // Reset the preview
        extractedTextInput.value = ''; // Clear the extracted text
    });

    // Browse Files
    uploadArea.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', () => {
        handleFileUpload();
    });

    // Handle File Upload
    async function handleFileUpload() {
        if (fileInput.files.length === 0) {
            filePreview.innerHTML = '<p>No files selected</p>';
            return;
        }

        loadingSpinner.style.display = 'block'; // Show loading spinner

        const formData = new FormData();
        for (const file of fileInput.files) {
            formData.append('file', file);
        }

        try {
            // Step 1: Upload file and extract text
            const response = await fetch('/index', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(data, 'text/html');
                const extractedText = doc.querySelector('#extractedText').value;
                filePreview.innerHTML = `<pre>${extractedText}</pre>`; // Display extracted text
                extractedTextInput.value = extractedText; // Store extracted text in hidden input
            } else {
                throw new Error('File upload failed');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        } finally {
            loadingSpinner.style.display = 'none'; // Hide loading spinner
        }
    }

    // Handle Generate Report Button Click
    generateReportButton.addEventListener('click', async (e) => {
        e.preventDefault(); // Prevent form submission

        const extractedText = extractedTextInput.value;

        if (!extractedText) {
            alert('No extracted text found. Please upload a file first.');
            return;
        }

        loadingSpinner.style.display = 'block'; // Show loading spinner

        try {
            const response = await fetch('/generate-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `extracted_text=${encodeURIComponent(extractedText)}`,
            });

            if (response.redirected) {
                window.location.href = response.url; // Redirect to the report page
            } else {
                throw new Error('Report generation failed');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        } finally {
            loadingSpinner.style.display = 'none'; // Hide loading spinner
        }
    });
});