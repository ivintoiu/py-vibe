// VibeDrive Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Add any client-side functionality here
    console.log('VibeDrive loaded');

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('[class*="border-l-4"]');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.display = 'none';
        }, 5000);
    });
});

// Helper function for API calls with JWT token
async function apiCall(url, method = 'GET', data = null) {
    const headers = {
        'Content-Type': 'application/json',
    };

    // Add JWT token if available from session storage
    const token = localStorage.getItem('access_token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const options = {
        method: method,
        headers: headers,
    };

    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        const jsonData = await response.json();

        if (!response.ok) {
            throw new Error(jsonData.error || 'API request failed');
        }

        return jsonData;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}
