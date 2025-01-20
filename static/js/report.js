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
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            // Show the full-screen spinner
            fullScreenSpinner.style.display = 'flex';


            // Create FormData object from the form
            const formData = new FormData(this);

            // Send form data directly to the backend
            fetch('/generate-report', {
                method: 'POST',
                body: formData, // Send FormData directly
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    flash('Report generated successfully!');
                    // Wait for the progress bar to complete before redirecting
                    setTimeout(() => {
                        window.location.href = `/report/${data.report_id}`; // Redirect to the report page
                    }, 1000); // Add a slight delay for a smooth transition
                } else {
                    throw new Error(data.message || 'Failed to generate report');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                flash('An error occurred while generating the report. Please check the console for details.');
            })
            .finally(() => {
                // Hide the full-screen spinner and progress bar after completion
                setTimeout(() => {
                    fullScreenSpinner.style.display = 'none';
                    }, 
                );
            });
        });
    });
});