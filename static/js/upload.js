document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('file');
    const filePreview = document.getElementById('filePreview');
    const clearFilesButton = document.getElementById('clearFilesButton');
    const generateReportButton = document.getElementById('generateReportButton');
    const extractedTextInput = document.getElementById('extractedText');
    const fullScreenSpinner = document.getElementById('fullScreenSpinner');
    const progressBarContainer = document.getElementById('progressBarContainer');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const fileNameInput = document.createElement('input'); // Create a hidden input for the file name
    fileNameInput.type = 'hidden';
    fileNameInput.id = 'fileName';
    document.body.appendChild(fileNameInput); // Append it to the body

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
        fileNameInput.value = ''; // Clear the file name
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

        fullScreenSpinner.style.display = 'flex'; // Show full-screen spinner

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
                const fileNameWithExtension = fileInput.files[0].name; // Get the file name with extension
                const fileName = fileNameWithExtension.split('.').slice(0, -1).join('.'); // Remove the extension
                filePreview.innerHTML = `<pre>${extractedText}</pre>`; // Display extracted text
                extractedTextInput.value = extractedText; // Store extracted text in hidden input
                fileNameInput.value = fileName; // Store file name (without extension) in hidden input
            } else {
                throw new Error('File upload failed');
            }
        } catch (error) {
            console.error('Error:', error);
            window.location.href = '/error'; // Redirect to error page
        } finally {
            fullScreenSpinner.style.display = 'none'; // Hide full-screen spinner
        }
    }

    // Handle Generate Report Button Click
    generateReportButton.addEventListener('click', async (e) => {
        e.preventDefault(); // Prevent form submission

        const extractedText = extractedTextInput.value;
        const fileName = fileNameInput.value; // Get the file name (without extension)

        if (!extractedText || !fileName) {
            window.location.href = '/error'; // Redirect to error page if no extracted text or file name
            return;
        }

        // Show and progress bar
        progressBarContainer.style.display = 'flex';
        progressBar.style.width = '0';
        progressText.textContent = '0%'; // Start with 0%

        // Simulate progress bar animation
        let progress = 0;
        const interval = setInterval(() => {
            progress += 1;
            progressBar.style.width = `${progress}%`;
            progressText.textContent = `${progress}%`; // Update percentage text

            // Stop the progress bar when it reaches 100%
            if (progress >= 100) {
                clearInterval(interval);
            }
        }, 60); // Adjust the speed of the progress bar (lower = faster)

        try {
            const response = await fetch('/generate-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `extracted_text=${encodeURIComponent(extractedText)}&fileName=${encodeURIComponent(fileName)}`,
            });

            if (response.redirected) {
                // Wait for the progress bar to complete before redirecting
                setTimeout(() => {
                    window.location.href = response.url; // Redirect to the report page
                }, 1000); // Add a slight delay for a smooth transition
            } else {
                throw new Error('Report generation failed');
            }
        } catch (error) {
            console.error('Error:', error);
            window.location.href = '/error'; // Redirect to error page
        } finally {
            // Hide spinner and progress bar after completion
            setTimeout(() => {
                progressBarContainer.style.display = 'none';
            }, 1000); // Add a slight delay for a smooth transition
        }
    });
});