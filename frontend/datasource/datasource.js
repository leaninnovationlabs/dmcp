$(document).ready(function() {
    const API_BASE_URL = APP_CONFIG.API_BASE_URL;
    
    // Initialize the page
    loadDatasources();

    // Event listeners
    $('#addDatasourceBtn, .addDatasourceBtn').on('click', function() {
        window.location.href = APP_CONFIG.urls.datasourceEdit();
    });

    $('#retryBtn').on('click', function() {
        loadDatasources();
    });

    // Load and display datasources
    function loadDatasources() {
        showLoadingState();
        
        $.ajax({
            url: `${API_BASE_URL}/datasources`,
            method: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success && response.data) {
                    displayDatasources(response.data);
                } else {
                    showErrorState('Failed to load datasources: ' + (response.errors?.[0]?.msg || 'Unknown error'));
                }
            },
            error: function(xhr, status, error) {
                let errorMessage = 'Failed to connect to server';
                if (xhr.responseJSON && xhr.responseJSON.errors && xhr.responseJSON.errors.length > 0) {
                    errorMessage = xhr.responseJSON.errors[0].msg || errorMessage;
                }
                showErrorState(errorMessage);
            }
        });
    }

    // Display datasources in card format
    function displayDatasources(datasources) {
        hideAllStates();
        
        if (!datasources || datasources.length === 0) {
            showEmptyState();
            return;
        }

        const $grid = $('#datasourcesGrid');
        $grid.empty();
        
        datasources.forEach(datasource => {
            const card = createDatasourceCard(datasource);
            $grid.append(card);
        });
        
        $grid.show();
    }

    // Create individual datasource card
    function createDatasourceCard(datasource) {
        const databaseTypeIcon = getDatabaseIcon(datasource.database_type);
        const statusColor = 'bg-green-100 text-green-800'; // Default to healthy
        
        return $(`
            <div class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer datasource-card mb-4" data-id="${datasource.id}">
                <div class="p-6">
                    <!-- Header -->
                    <div class="flex items-start justify-between mb-4">
                        <div class="flex items-center space-x-3">
                            <div>${databaseTypeIcon}</div>
                            <div>
                                <h3 class="text-lg font-semibold text-gray-900 truncate">${escapeHtml(datasource.name)}</h3>
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColor}">
                                    ${datasource.database_type.toUpperCase()}
                                </span>
                            </div>
                        </div>
                        <div class="flex items-center space-x-2">
                            <button class="text-gray-400 hover:text-gray-600 transition-colors test-connection-btn" data-id="${datasource.id}" title="Test Connection">
                                <i class="fas fa-plug text-lg"></i>
                            </button>
                        </div>
                    </div>

                    <!-- Connection Info -->
                    <div class="space-y-2 text-sm text-gray-600">
                        ${datasource.host ? `
                            <div class="flex items-center space-x-2">
                                <i class="fas fa-server text-gray-400"></i>
                                <span>${escapeHtml(datasource.host)}${datasource.port ? ':' + datasource.port : ''}</span>
                            </div>
                        ` : ''}
                        <div class="flex items-center space-x-2">
                            <i class="fas fa-database text-gray-400"></i>
                            <span>${escapeHtml(datasource.database)}</span>
                        </div>
                        ${datasource.username ? `
                            <div class="flex items-center space-x-2">
                                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                                </svg>
                                <span>${escapeHtml(datasource.username)}</span>
                            </div>
                        ` : ''}
                    </div>

                    <!-- Footer -->
                    <div class="mt-4 pt-4 border-t border-gray-200 flex justify-between items-center text-xs text-gray-500">
                        <span>Created: ${formatDate(datasource.created_at)}</span>
                        <span class="text-blue-600 font-medium">Click to edit</span>
                    </div>
                </div>
            </div>
        `);
    }

    // Handle card click (navigate to edit page)
    $(document).on('click', '.datasource-card', function(e) {
        // Prevent navigation if clicking on test connection button
        if ($(e.target).closest('.test-connection-btn').length > 0) {
            return;
        }
        
        const datasourceId = $(this).data('id');
        window.location.href = APP_CONFIG.urls.datasourceEdit(datasourceId);
    });

    // Handle test connection
    $(document).on('click', '.test-connection-btn', function(e) {
        e.stopPropagation();
        const datasourceId = $(this).data('id');
        testConnection(datasourceId, $(this));
    });

    // Test database connection
    function testConnection(datasourceId, $button) {
        const originalHtml = $button.html();
        $button.html('<div class="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>');
        $button.prop('disabled', true);

        $.ajax({
            url: `${API_BASE_URL}/datasources/${datasourceId}/test`,
            method: 'POST',
            dataType: 'json',
            success: function(response) {
                if (response.success && response.data) {
                    showNotification('Connection test successful', 'success');
                } else {
                    showNotification('Connection test failed', 'error');
                }
            },
            error: function(xhr) {
                let errorMessage = 'Connection test failed';
                if (xhr.responseJSON && xhr.responseJSON.errors && xhr.responseJSON.errors.length > 0) {
                    errorMessage = xhr.responseJSON.errors[0].msg || errorMessage;
                }
                showNotification(errorMessage, 'error');
            },
            complete: function() {
                $button.html(originalHtml);
                $button.prop('disabled', false);
            }
        });
    }

    // State management functions
    function showLoadingState() {
        hideAllStates();
        $('#loadingState').show();
    }

    function showErrorState(message) {
        hideAllStates();
        $('#errorMessage').text(message);
        $('#errorState').show();
    }

    function showEmptyState() {
        hideAllStates();
        $('#emptyState').show();
    }

    function hideAllStates() {
        $('#loadingState, #errorState, #emptyState, #datasourcesGrid').hide();
    }

    // Utility functions
    function getDatabaseIcon(databaseType) {
        const icons = {
            'postgresql': '<i class="fab fa-elephant text-2xl text-blue-600"></i>',
            'mysql': '<i class="fas fa-fish text-2xl text-orange-500"></i>',
            'sqlite': '<i class="fas fa-cube text-2xl text-gray-600"></i>'
        };
        return icons[databaseType] || '<i class="fas fa-database text-2xl text-blue-500"></i>';
    }

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString();
    }

    function escapeHtml(text) {
        if (!text) return '';
        return $('<div>').text(text).html();
    }

    function showNotification(message, type = 'info') {
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            info: 'bg-blue-500',
            warning: 'bg-yellow-500'
        };

        const notification = $(`
            <div class="notification ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg transform translate-x-full transition-transform duration-300 max-w-sm">
                <p class="font-medium">${escapeHtml(message)}</p>
            </div>
        `);

        $('#statusMessages').append(notification);
        
        // Slide in
        setTimeout(() => {
            notification.removeClass('translate-x-full');
        }, 100);

        // Remove after 5 seconds
        setTimeout(() => {
            notification.addClass('translate-x-full');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
    }
}); 