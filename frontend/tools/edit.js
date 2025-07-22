$(document).ready(function() {
    const API_BASE_URL = 'http://localhost:8000/dbmcp';
    let isEditMode = false;
    let currentToolId = null;

    // Get tool ID from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const toolId = urlParams.get('id');

    if (toolId) {
        isEditMode = true;
        currentToolId = toolId;
        $('#pageTitle').text('Edit Tool');
        $('#deleteBtn, #executeBtn').show();
        loadTool(toolId);
    } else {
        $('#pageTitle').text('Create New Tool');
        $('#saveBtn').text('Create Tool');
        hideLoadingState();
    }

    // Load datasources for dropdown
    loadDatasources();

    // Event listeners
    $('#backBtn, #cancelBtn').on('click', function() {
        window.location.href = './';
    });

    $('#toolForm').on('submit', function(e) {
        e.preventDefault();
        saveTool();
    });

    $('#deleteBtn').on('click', function() {
        if (confirm('Are you sure you want to delete this tool? This action cannot be undone.')) {
            deleteTool();
        }
    });

    $('#executeBtn').on('click', function() {
        executeTool();
    });

    $('#addParameterBtn').on('click', function() {
        addParameter();
    });

    // Handle parameter removal
    $(document).on('click', '.remove-parameter', function() {
        $(this).closest('.parameter-item').remove();
        updateParametersDisplay();
    });

    // Update parameters display when changes are made
    $(document).on('input change', '.parameter-item input, .parameter-item select', function() {
        updateParametersDisplay();
    });

    // Load datasources for dropdown
    function loadDatasources() {
        $.ajax({
            url: `${API_BASE_URL}/datasources`,
            method: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success && response.data) {
                    const $select = $('#datasource_id');
                    $select.empty().append('<option value="">Select datasource</option>');
                    
                    response.data.forEach(datasource => {
                        $select.append(`<option value="${datasource.id}">${escapeHtml(datasource.name)} (${datasource.database_type})</option>`);
                    });
                }
            },
            error: function() {
                showNotification('Failed to load datasources', 'warning');
            }
        });
    }

    // Load existing tool data
    function loadTool(id) {
        showLoadingState();

        $.ajax({
            url: `${API_BASE_URL}/tools/${id}`,
            method: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success && response.data) {
                    populateForm(response.data);
                } else {
                    showNotification('Failed to load tool: ' + (response.errors?.[0]?.msg || 'Unknown error'), 'error');
                    setTimeout(() => window.location.href = './', 2000);
                }
            },
            error: function(xhr, status, error) {
                let errorMessage = 'Failed to load tool';
                if (xhr.responseJSON && xhr.responseJSON.errors && xhr.responseJSON.errors.length > 0) {
                    errorMessage = xhr.responseJSON.errors[0].msg || errorMessage;
                }
                showNotification(errorMessage, 'error');
                setTimeout(() => window.location.href = './', 2000);
            },
            complete: function() {
                hideLoadingState();
            }
        });
    }

    // Populate form with tool data
    function populateForm(tool) {
        $('#toolId').val(tool.id);
        $('#name').val(tool.name);
        $('#description').val(tool.description || '');
        $('#type').val(tool.type);
        $('#sql').val(tool.sql);
        $('#datasource_id').val(tool.datasource_id);
        
        // Load parameters
        if (tool.parameters && tool.parameters.length > 0) {
            tool.parameters.forEach(param => {
                addParameter(param);
            });
        }
        
        updateParametersDisplay();
    }

    // Add parameter to the form
    function addParameter(paramData = null) {
        const template = $('#parameterTemplate').html();
        const $param = $(template);
        
        if (paramData) {
            $param.find('.param-name').val(paramData.name || '');
            $param.find('.param-type').val(paramData.type || 'string');
            $param.find('.param-default').val(paramData.default || '');
            $param.find('.param-required').prop('checked', paramData.required || false);
            $param.find('.param-description').val(paramData.description || '');
        }
        
        $('#parametersContainer').append($param);
        updateParametersDisplay();
    }

    // Update parameters display
    function updateParametersDisplay() {
        const paramCount = $('.parameter-item').length;
        if (paramCount > 0) {
            $('#noParametersMessage').hide();
            $('#parametersContainer').show();
        } else {
            $('#noParametersMessage').show();
            $('#parametersContainer').hide();
        }
    }

    // Save tool (create or update)
    function saveTool() {
        const formData = getFormData();
        
        if (!validateForm(formData)) {
            return;
        }

        const $saveBtn = $('#saveBtn');
        const originalText = $saveBtn.text();
        $saveBtn.text('Saving...').prop('disabled', true);

        const url = isEditMode ? `${API_BASE_URL}/tools/${currentToolId}` : `${API_BASE_URL}/tools`;
        const method = isEditMode ? 'PUT' : 'POST';

        $.ajax({
            url: url,
            method: method,
            contentType: 'application/json',
            data: JSON.stringify(formData),
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    showNotification(isEditMode ? 'Tool updated successfully' : 'Tool created successfully', 'success');
                    setTimeout(() => window.location.href = './', 1500);
                } else {
                    const errorMessage = response.errors?.[0]?.msg || 'Unknown error occurred';
                    showNotification('Failed to save tool: ' + errorMessage, 'error');
                }
            },
            error: function(xhr) {
                let errorMessage = 'Failed to save tool';
                if (xhr.responseJSON && xhr.responseJSON.errors && xhr.responseJSON.errors.length > 0) {
                    errorMessage = xhr.responseJSON.errors[0].msg || errorMessage;
                }
                showNotification(errorMessage, 'error');
            },
            complete: function() {
                $saveBtn.text(originalText).prop('disabled', false);
            }
        });
    }

    // Delete tool
    function deleteTool() {
        const $deleteBtn = $('#deleteBtn');
        $deleteBtn.text('Deleting...').prop('disabled', true);

        $.ajax({
            url: `${API_BASE_URL}/tools/${currentToolId}`,
            method: 'DELETE',
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    showNotification('Tool deleted successfully', 'success');
                    setTimeout(() => window.location.href = './', 1500);
                } else {
                    const errorMessage = response.errors?.[0]?.msg || 'Unknown error occurred';
                    showNotification('Failed to delete tool: ' + errorMessage, 'error');
                }
            },
            error: function(xhr) {
                let errorMessage = 'Failed to delete tool';
                if (xhr.responseJSON && xhr.responseJSON.errors && xhr.responseJSON.errors.length > 0) {
                    errorMessage = xhr.responseJSON.errors[0].msg || errorMessage;
                }
                showNotification(errorMessage, 'error');
            },
            complete: function() {
                $deleteBtn.text('Delete').prop('disabled', false);
            }
        });
    }

    // Execute tool
    function executeTool() {
        if (!isEditMode) {
            showNotification('Please save the tool first before executing it', 'warning');
            return;
        }

        const $executeBtn = $('#executeBtn');
        const originalText = $executeBtn.text();
        $executeBtn.text('Executing...').prop('disabled', true);

        $.ajax({
            url: `${API_BASE_URL}/execute/${currentToolId}`,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ parameters: {} }),
            dataType: 'json',
            success: function(response) {
                if (response.success && response.data) {
                    const data = response.data;
                    const rowCount = data.row_count || 0;
                    const executionTime = data.execution_time_ms || 0;
                    showNotification(`Tool executed successfully! ${rowCount} rows returned in ${executionTime}ms`, 'success');
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
                $executeBtn.text(originalText).prop('disabled', false);
            }
        });
    }

    // Get form data
    function getFormData() {
        const parameters = [];
        
        $('.parameter-item').each(function() {
            const $param = $(this);
            const name = $param.find('.param-name').val().trim();
            if (name) {
                const param = {
                    name: name,
                    type: $param.find('.param-type').val(),
                    description: $param.find('.param-description').val().trim() || null,
                    required: $param.find('.param-required').is(':checked'),
                    default: $param.find('.param-default').val().trim() || null
                };
                parameters.push(param);
            }
        });

        const formData = {
            name: $('#name').val().trim(),
            description: $('#description').val().trim() || null,
            type: $('#type').val(),
            sql: $('#sql').val().trim(),
            datasource_id: parseInt($('#datasource_id').val()),
            parameters: parameters
        };

        // Remove null/empty values for updates
        if (isEditMode) {
            Object.keys(formData).forEach(key => {
                if (formData[key] === null || formData[key] === '') {
                    delete formData[key];
                }
            });
        }

        return formData;
    }

    // Form validation
    function validateForm(data) {
        let isValid = true;
        
        // Clear previous errors
        $('.border-red-300').removeClass('border-red-300').addClass('border-gray-300');

        // Required fields
        if (!data.name) {
            $('#name').removeClass('border-gray-300').addClass('border-red-300');
            isValid = false;
        }

        if (!data.type) {
            $('#type').removeClass('border-gray-300').addClass('border-red-300');
            isValid = false;
        }

        if (!data.sql) {
            $('#sql').removeClass('border-gray-300').addClass('border-red-300');
            isValid = false;
        }

        if (!data.datasource_id) {
            $('#datasource_id').removeClass('border-gray-300').addClass('border-red-300');
            isValid = false;
        }

        // Validate parameters
        let parameterNamesSet = new Set();
        let hasParameterErrors = false;
        
        $('.parameter-item').each(function() {
            const $param = $(this);
            const name = $param.find('.param-name').val().trim();
            
            if (name) {
                if (parameterNamesSet.has(name)) {
                    $param.find('.param-name').removeClass('border-gray-300').addClass('border-red-300');
                    hasParameterErrors = true;
                    showNotification('Duplicate parameter names are not allowed', 'error');
                } else {
                    parameterNamesSet.add(name);
                }
                
                // Validate parameter name format (alphanumeric and underscore only)
                if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(name)) {
                    $param.find('.param-name').removeClass('border-gray-300').addClass('border-red-300');
                    hasParameterErrors = true;
                    showNotification('Parameter names must start with a letter or underscore and contain only letters, numbers, and underscores', 'error');
                }
            }
        });

        if (hasParameterErrors) {
            isValid = false;
        }

        if (!isValid) {
            showNotification('Please fix the highlighted fields', 'error');
        }

        return isValid;
    }

    // State management
    function showLoadingState() {
        $('#loadingState').show();
        $('#formContainer').hide();
    }

    function hideLoadingState() {
        $('#loadingState').hide();
        $('#formContainer').show();
    }

    // Initialize parameters display
    updateParametersDisplay();

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