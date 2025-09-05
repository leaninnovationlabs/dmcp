$(document).ready(function() {
    const API_BASE_URL = APP_CONFIG.API_BASE_URL;
    
    // Initialize the page
    loadTools();

    // Event listeners
    $('#addToolBtn, .addToolBtn').on('click', function() {
        window.location.href = APP_CONFIG.urls.toolsEdit();
    });

    $('#retryBtn').on('click', function() {
        loadTools();
    });

    // Load and display tools
    function loadTools() {
        showLoadingState();
        
        makeApiRequest({
            url: `${API_BASE_URL}/tools`,
            method: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success && response.data) {
                    displayTools(response.data);
                } else {
                    showErrorState('Failed to load tools: ' + (response.errors?.[0]?.msg || 'Unknown error'));
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

    // Load datasources for tool cards
    let datasourcesMap = {};
    function loadDatasources() {
        makeApiRequest({
            url: `${API_BASE_URL}/datasources`,
            method: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success && response.data) {
                    response.data.forEach(ds => {
                        datasourcesMap[ds.id] = ds;
                    });
                }
            },
            error: function() {
                // Silently fail - not critical for display
            }
        });
    }
    loadDatasources();

    // Display tools in card format
    function displayTools(tools) {
        hideAllStates();
        
        if (!tools || tools.length === 0) {
            showEmptyState();
            return;
        }

        const $grid = $('#toolsGrid');
        $grid.empty();
        
        tools.forEach(tool => {
            const card = createToolCard(tool);
            $grid.append(card);
        });
        
        $grid.show();
    }

    // Create individual tool card
    function createToolCard(tool) {
        const typeIcon = getToolTypeIcon(tool.type);
        const typeColor = getToolTypeColor(tool.type);
        const datasource = datasourcesMap[tool.datasource_id];
        const datasourceName = datasource ? datasource.name : `Datasource #${tool.datasource_id}`;
        const paramCount = tool.parameters ? tool.parameters.length : 0;
        
        return $(`
            <div class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer tool-card mb-4" data-id="${tool.id}">
                <div class="p-6">
                    <!-- Header -->
                    <div class="flex items-start justify-between mb-4">
                        <div class="flex items-center space-x-3">
                            <div class="text-2xl">${typeIcon}</div>
                            <div>
                                <h3 class="text-lg font-semibold text-gray-900 truncate">${escapeHtml(tool.name)}</h3>
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${typeColor}">
                                    ${tool.type.toUpperCase()}
                                </span>
                            </div>
                        </div>
                        <div class="flex items-center space-x-2">
                            <button class="text-gray-400 hover:text-gray-600 transition-colors execute-tool-btn" data-id="${tool.id}" title="Execute Tool">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h1m4 0h1m6-10V9a3 3 0 01-3 3h-4.5M21 9.5V6a3 3 0 00-3-3h-4.5a3 3 0 00-3 3v3.5a3 3 0 003 3h4.5a3 3 0 003-3z"></path>
                                </svg>
                            </button>
                        </div>
                    </div>

                    <!-- Description -->
                    ${tool.description ? `
                        <p class="text-sm text-gray-600 mb-4 line-clamp-2">${escapeHtml(tool.description)}</p>
                    ` : ''}

                    <!-- Tool Info -->
                    <div class="space-y-2 text-sm text-gray-600">
                        <div class="flex items-center space-x-2">
                            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"></path>
                            </svg>
                            <span>${escapeHtml(datasourceName)}</span>
                        </div>
                        <div class="flex items-center space-x-2">
                            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                            </svg>
                            <span>${paramCount} parameter${paramCount !== 1 ? 's' : ''}</span>
                        </div>
                    </div>

                    <!-- SQL Preview -->
                    ${tool.sql ? `
                        <div class="mt-4 p-3 bg-gray-50 rounded-md">
                            <div class="flex items-center justify-between mb-2">
                                <span class="text-xs font-medium text-gray-500 uppercase tracking-wide">SQL Preview</span>
                            </div>
                            <code class="text-xs text-gray-700 block truncate">${escapeHtml(tool.sql.substring(0, 100))}${tool.sql.length > 100 ? '...' : ''}</code>
                        </div>
                    ` : ''}

                    <!-- Footer -->
                    <div class="mt-4 pt-4 border-t border-gray-200 flex justify-between items-center text-xs text-gray-500">
                        <span>Created: ${formatDate(tool.created_at)}</span>
                        <span class="text-purple-600 font-medium">Click to edit</span>
                    </div>
                </div>
            </div>
        `);
    }

    // Handle card click (navigate to edit page)
    $(document).on('click', '.tool-card', function(e) {
        // Prevent navigation if clicking on execute button
        if ($(e.target).closest('.execute-tool-btn').length > 0) {
            return;
        }
        
        const toolId = $(this).data('id');
        window.location.href = APP_CONFIG.urls.toolsEdit(toolId);
    });

    // Handle tool execution
    $(document).on('click', '.execute-tool-btn', function(e) {
        e.stopPropagation();
        const toolId = $(this).data('id');
        executeTool(toolId, $(this));
    });

    // Execute tool
    function executeTool(toolId, $button) {
        const originalHtml = $button.html();
        $button.html('<div class="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>');
        $button.prop('disabled', true);

        makeApiRequest({
            url: `${API_BASE_URL}/execute/${toolId}`,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ parameters: {} }),
            dataType: 'json',
            success: function(response) {
                if (response.success && response.data) {
                    // Check if the inner data indicates success or failure
                    if (response.data.success) {
                        const rowCount = response.data.row_count || 0;
                        const executionTime = response.data.execution_time_ms || 0;
                        showNotification(`Tool executed successfully! ${rowCount} rows returned in ${executionTime}ms`, 'success');
                    } else {
                        // Handle error from the inner data
                        const errorMessage = response.data.error || 'Tool execution failed';
                        showNotification(`Execution failed: ${errorMessage}`, 'error');
                    }
                } else {
                    showNotification('Tool execution failed', 'error');
                }
            },
            error: function(xhr) {
                let errorMessage = 'Tool execution failed';
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
        $('#loadingState, #errorState, #emptyState, #toolsGrid').hide();
    }

    // Utility functions
    function getToolTypeIcon(toolType) {
        const icons = {
            'query': '🔍',
            'http': '🌐',
            'code': '⚙️'
        };
        return icons[toolType] || '🛠️';
    }

    function getToolTypeColor(toolType) {
        const colors = {
            'query': 'bg-blue-100 text-blue-800',
            'http': 'bg-gray-100 text-gray-500', // Disabled color for unsupported type
            'code': 'bg-gray-100 text-gray-500'   // Disabled color for unsupported type
        };
        return colors[toolType] || 'bg-gray-100 text-gray-800';
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