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
        
        makeApiRequest({
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
        const typeIcon = getDatabaseTypeIcon(datasource.database_type);
        const typeColor = getDatabaseTypeColor(datasource.database_type);
        
        return $(`
            <div class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer datasource-card mb-4" data-id="${datasource.id}">
                <div class="p-6">
                    <!-- Header -->
                    <div class="flex items-start justify-between mb-4">
                        <div class="flex items-center space-x-3">
                            <div class="text-2xl">${typeIcon}</div>
                            <div>
                                <h3 class="text-lg font-semibold text-gray-900 truncate">${escapeHtml(datasource.name)}</h3>
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${typeColor}">
                                    ${datasource.database_type.toUpperCase()}
                                </span>
                            </div>
                        </div>
                        <div class="flex items-center space-x-2">
                            <button class="test-connection text-green-600 hover:text-green-700 p-1 rounded" data-id="${datasource.id}" title="Test Connection">
                                <i class="fas fa-plug"></i>
                            </button>
                            <button class="edit-datasource text-blue-600 hover:text-blue-700 p-1 rounded" data-id="${datasource.id}" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                        </div>
                    </div>

                    <!-- Details -->
                    <div class="space-y-2 text-sm text-gray-600">
                        ${datasource.host ? `<div><span class="font-medium">Host:</span> ${escapeHtml(datasource.host)}${datasource.port ? ':' + datasource.port : ''}</div>` : ''}
                        <div><span class="font-medium">Database:</span> ${escapeHtml(datasource.database)}</div>
                        ${datasource.username ? `<div><span class="font-medium">Username:</span> ${escapeHtml(datasource.username)}</div>` : ''}
                        ${datasource.ssl_mode ? `<div><span class="font-medium">SSL Mode:</span> ${escapeHtml(datasource.ssl_mode)}</div>` : ''}
                    </div>

                    <!-- Connection Status -->
                    <div class="mt-4 pt-4 border-t border-gray-200">
                        <div class="flex items-center justify-between">
                            <span class="text-sm text-gray-500">Connection Status</span>
                            <div class="connection-status-${datasource.id} flex items-center space-x-1">
                                <div class="w-2 h-2 bg-gray-400 rounded-full"></div>
                                <span class="text-xs text-gray-500">Unknown</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `);
    }

    // Database type icons and colors
    function getDatabaseTypeIcon(type) {
        const icons = {
            'postgresql': '<i class="fas fa-database text-blue-600"></i>',
            'mysql': '<i class="fas fa-database text-orange-600"></i>',
            'sqlite': '<i class="fas fa-database text-green-600"></i>',
            'mongodb': '<i class="fas fa-leaf text-green-600"></i>',
            'redis': '<i class="fas fa-memory text-red-600"></i>'
        };
        return icons[type] || '<i class="fas fa-database text-gray-600"></i>';
    }

    function getDatabaseTypeColor(type) {
        const colors = {
            'postgresql': 'bg-blue-100 text-blue-800',
            'mysql': 'bg-orange-100 text-orange-800',
            'sqlite': 'bg-green-100 text-green-800',
            'mongodb': 'bg-green-100 text-green-800',
            'redis': 'bg-red-100 text-red-800'
        };
        return colors[type] || 'bg-gray-100 text-gray-800';
    }

    // Event delegation for card actions
    $(document).on('click', '.datasource-card', function(e) {
        if ($(e.target).closest('button').length) return; // Don't trigger on button clicks
        
        const datasourceId = $(this).data('id');
        window.location.href = APP_CONFIG.urls.datasourceEdit(datasourceId);
    });

    $(document).on('click', '.edit-datasource', function(e) {
        e.stopPropagation();
        const datasourceId = $(this).data('id');
        window.location.href = APP_CONFIG.urls.datasourceEdit(datasourceId);
    });

    $(document).on('click', '.test-connection', function(e) {
        e.stopPropagation();
        const datasourceId = $(this).data('id');
        testConnection(datasourceId);
    });

    // Test connection functionality
    function testConnection(datasourceId) {
        const $statusContainer = $(`.connection-status-${datasourceId}`);
        const $testBtn = $(this);
        
        // Show testing state
        $statusContainer.html(`
            <div class="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
            <span class="text-xs text-yellow-600">Testing...</span>
        `);

        makeApiRequest({
            url: `${API_BASE_URL}/datasources/${datasourceId}/test`,
            method: 'POST',
            dataType: 'json',
            success: function(response) {
                if (response.success && response.data) {
                    const data = response.data;
                    $statusContainer.html(`
                        <div class="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span class="text-xs text-green-600">Connected (${data.connection_time_ms}ms)</span>
                    `);
                    showNotification('Connection successful!', 'success');
                } else {
                    $statusContainer.html(`
                        <div class="w-2 h-2 bg-red-500 rounded-full"></div>
                        <span class="text-xs text-red-600">Failed</span>
                    `);
                    showNotification('Connection test failed', 'error');
                }
            },
            error: function(xhr) {
                let errorMessage = 'Connection test failed';
                if (xhr.responseJSON && xhr.responseJSON.errors && xhr.responseJSON.errors.length > 0) {
                    errorMessage = xhr.responseJSON.errors[0].msg || errorMessage;
                }
                $statusContainer.html(`
                    <div class="w-2 h-2 bg-red-500 rounded-full"></div>
                    <span class="text-xs text-red-600">Failed</span>
                `);
                showNotification(errorMessage, 'error');
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

    // Notification system
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

        // Create container if it doesn't exist
        if ($('#statusMessages').length === 0) {
            $('body').append('<div id="statusMessages" class="fixed top-4 right-4 z-50 space-y-2"></div>');
        }

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

    function escapeHtml(text) {
        if (!text) return '';
        return $('<div>').text(text).html();
    }
});