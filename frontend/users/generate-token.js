$(document).ready(function() {
    // Wait a bit for auth manager to initialize
    setTimeout(() => {
        // Check authentication on page load
        checkAuth();
        
        // Initialize sidebar
        initializeSidebar();
        
        // Event handlers
        $('#generate-token-btn').click(generateToken);
        $('#cancel-btn').click(cancelGeneration);
        $('#copy-token-btn').click(copyToken);
        $('#generate-another-btn').click(generateAnotherToken);
        $('#back-btn').click(goBack);
    }, 100);
});

/**
 * Generate a new JWT token
 */
async function generateToken() {
    try {
        // Show loading state
        $('#generate-token-btn').prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Generating...');
        
        // Clear any previous messages
        clearMessages();
        
        // Get the current token for authentication
        const token = window.authManager ? window.authManager.getToken() : localStorage.getItem('dmcp_bearer_token');
        if (!token) {
            showError('Authentication required. Please log in.');
            return;
        }
        
        // Make API request to generate token
        const response = await fetch(`${APP_CONFIG.API_BASE_URL}/users/generate-token`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            // Display the generated token
            displayToken(result.data);
        } else {
            // Handle error response
            const errorMessage = result.errors && result.errors.length > 0 
                ? result.errors[0].msg || result.errors[0] 
                : 'Failed to generate token';
            showError(errorMessage);
        }
    } catch (error) {
        console.error('Error generating token:', error);
        showError('Failed to generate token. Please try again.');
    } finally {
        // Reset button state
        $('#generate-token-btn').prop('disabled', false).html('<i class="fas fa-key"></i> Generate Token');
    }
}

/**
 * Display the generated token
 */
function displayToken(tokenData) {
    // Hide the form and show the token display
    $('#token-form').hide();
    $('#token-display').removeClass('hidden').show();
    
    // Populate token information
    $('#token-text').text(tokenData.token);
    $('#expires-at').text(formatDateTime(tokenData.expires_at));
    $('#token-user').text(tokenData.username);
    
    // Show success message
    showSuccess('Token generated successfully! Copy the token below.');
}

/**
 * Copy token to clipboard
 */
async function copyToken() {
    const token = $('#token-text').text();
    
    try {
        await navigator.clipboard.writeText(token);
        
        // Show temporary success message
        const copyBtn = $('#copy-token-btn');
        const originalText = copyBtn.html();
        copyBtn.html('<i class="fas fa-check"></i> Copied!');
        copyBtn.css('background-color', '#10b981');
        
        setTimeout(() => {
            copyBtn.html(originalText);
            copyBtn.css('background-color', '#000000');
        }, 2000);
    } catch (error) {
        console.error('Failed to copy token:', error);
        showError('Failed to copy token to clipboard. Please copy it manually.');
    }
}

/**
 * Generate another token
 */
function generateAnotherToken() {
    // Hide token display and show form
    $('#token-display').hide();
    $('#token-form').show();
    
    // Clear any messages
    clearMessages();
}

/**
 * Go back to previous page
 */
function goBack() {
    window.history.back();
}

/**
 * Cancel token generation
 */
function cancelGeneration() {
    window.history.back();
}

/**
 * Show success message
 */
function showSuccess(message) {
    const messageHtml = `
        <div class="success-message">
            <i class="fas fa-check-circle mr-2"></i>
            ${message}
        </div>
    `;
    $('#message-container').html(messageHtml);
}

/**
 * Show error message
 */
function showError(message) {
    const messageHtml = `
        <div class="error-message">
            <i class="fas fa-exclamation-circle mr-2"></i>
            ${message}
        </div>
    `;
    $('#message-container').html(messageHtml);
}

/**
 * Clear all messages
 */
function clearMessages() {
    $('#message-container').empty();
}

/**
 * Format datetime for display
 */
function formatDateTime(dateTimeString) {
    const date = new Date(dateTimeString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZoneName: 'short'
    });
}

/**
 * Check if user is authenticated
 */
function checkAuth() {
    // Use the auth manager if available
    if (window.authManager) {
        if (!window.authManager.isAuthenticated()) {
            window.authManager.showLoginDialog();
            return false;
        }
        return true;
    } else {
        // Fallback to direct localStorage check
        const token = localStorage.getItem('dmcp_bearer_token');
        if (!token) {
            window.location.href = '../index.html';
            return false;
        }
        return true;
    }
}

/**
 * Initialize sidebar
 */
function initializeSidebar() {
    // This will be handled by sidebar.js
    // The sidebar should already be initialized from the HTML
}
