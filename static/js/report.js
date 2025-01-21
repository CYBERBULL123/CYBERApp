document.addEventListener('DOMContentLoaded', function () {
    // Handle tab switching
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', function () {
            const tabId = this.getAttribute('data-tab');

            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to the clicked button and corresponding content
            this.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // Handle form submissions
    const forms = document.querySelectorAll('.report-form');
    const fullScreenSpinner = document.getElementById('fullScreenSpinner');

    forms.forEach(form => {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();

            // Show the full-screen spinner
            fullScreenSpinner.style.display = 'flex';

            try {
                // Create FormData object from the form
                const formData = new FormData(this);

                // Send form data directly to the backend
                const response = await fetch('/generate-report', {
                    method: 'POST',
                    body: formData, // Send FormData directly
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                // Check if the response is a redirect
                if (response.redirected) {
                    // Redirect to the URL provided by Flask
                    window.location.href = response.url;
                } else {
                    // Handle JSON response (if any)
                    const data = await response.json();
                    if (data.success) {
                        // Flash success message (assuming you have a flash function)
                        flash('Report generated successfully!', 'success');
                        // Redirect to the report page after a slight delay
                        setTimeout(() => {
                            window.location.href = `/report/${data.report_id}`;
                        }, 1000); // Add a slight delay for a smooth transition
                    } else {
                        throw new Error(data.message || 'Failed to generate report');
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                // Flash error message (assuming you have a flash function)
                flash('An error occurred while generating the report. Please check the console for details.', 'error');
            } finally {
                // Hide the full-screen spinner after completion
                setTimeout(() => {
                    fullScreenSpinner.style.display = 'none';
                }, 1000); // Add a slight delay for a smooth transition
            }
        });
    });

    // Prevent form submission on Enter key press
    forms.forEach(form => {
        form.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault(); // Prevent form submission
                saveFormData(form); // Save form data
            }
        });
    });

    // Function to save form data
    function saveFormData(form) {
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });
        console.log('Form Data Saved:', data);
    }

    // Flash message function (if not already defined)
    function flash(message, type) {
        const flashContainer = document.createElement('div');
        flashContainer.className = `flash-message ${type}`;
        flashContainer.textContent = message;
        document.body.appendChild(flashContainer);

        // Remove the flash message after 3 seconds
        setTimeout(() => {
            flashContainer.remove();
        }, 3000);
    }
});