document.addEventListener('DOMContentLoaded', () => {
    // Animate report cards
    const cards = document.querySelectorAll('.report-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 200); // Staggered delay for each card
    });

    // Handle flash messages
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach((message) => {
        // Slide-in animation
        setTimeout(() => {
            message.style.opacity = '1';
            message.style.transform = 'translateX(0)';
        }, 100);

        // Auto-remove flash message after 5 seconds
        const autoRemoveTimeout = setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translateX(100%)';
            setTimeout(() => message.remove(), 500); // Remove after slide-out
        }, 5000); // 5 seconds delay

        // Close button functionality
        const closeButton = message.querySelector('.close-btn');
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                clearTimeout(autoRemoveTimeout); // Cancel auto-remove timeout
                message.style.opacity = '0';
                message.style.transform = 'translateX(100%)';
                setTimeout(() => message.remove(), 500); // Remove after slide-out
            });
        }
    });

    // Handle alerts (if any)
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach((alert) => {
        // Fade-in animation
        setTimeout(() => {
            alert.style.opacity = '1';
        }, 100);

        // Auto-remove alert after 3 seconds
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500); // Remove after fade-out
        }, 3000); // 3 seconds delay
    });
});