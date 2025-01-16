document.addEventListener('DOMContentLoaded', () => {
    // Animate report cards
    const cards = document.querySelectorAll('.report-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s, transform 0.5s';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 200); // Staggered delay for each card
    });

    // Handle flash messages
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        // Show the flash message with a slide-in animation
        setTimeout(() => {
            message.classList.add('show');
        }, 100);

        // Auto-remove flash message after 5 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 500); // Remove after fade-out
        }, 5000); // 5 seconds delay

        // Close button functionality
        const closeButton = message.querySelector('.close');
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                message.style.opacity = '0';
                setTimeout(() => message.remove(), 500); // Remove after fade-out
            });
        }
    });

    // Handle alerts (if any)
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500); // Remove after fade-out
        }, 3000); // 3 seconds delay
    });
});