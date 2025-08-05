$(document).ready(function() {
    const API_BASE_URL = APP_CONFIG.API_BASE_URL;
    let isEditMode = false;
    let currentDatasourceId = null;
    let fieldConfigs = null;

    // Get datasource ID from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const datasourceId = urlParams.get('id');

    if (datasourceId) {
        isEditMode = true;
        currentDatasourceId = datasourceId;
        $('#pageTitle').text('Datasource');
        $('#deleteBtn').show();
        loadDatasource(datasourceId);
    } else {
        $('#pageTitle').text('Create New Datasource');
        $('#saveBtn').text('Create Datasource');
        hideLoadingState();
    }

    // Load field configurations from API
    loadFieldConfigs();

    // Event listeners
    $('#backBtn, #cancelBtn').on('click', function() {
        window.location.href = APP_CONFIG.urls.datasource();
    });

    $('#datasourceForm').on('submit', function(e) {
        e.preventDefault();
        saveDatasource();
    });

    $('#deleteBtn').on('click', function() {
        if (confirm('Are you sure you want to delete this datasource? This action cannot be undone.')) {
            deleteDatasource();
        }
    });

    $('#testConnectionBtn').on('click', function() {
        testConnection();
    });

    // Database type change handler
    $('#database_type').on('change', function() {
        updateFormFields();
    });

    // Auto-format JSON in additional_params field
    $('#additional_params').on('blur', function() {
        try {
            const value = $(this).val().trim();
            if (value && value !== '{}') {
                const parsed = JSON.parse(value);
                $(this).val(JSON.stringify(parsed, null, 2));
                $(this).removeClass('border-red-300').addClass('border-gray-300');
            }
        } catch (e) {
            $(this).removeClass('border-gray-300').addClass('border-red-300');
        }
    });

    // Load field configurations from API
    function loadFieldConfigs() {
        makeApiRequest({
            url: `${API_BASE_URL}/datasources/field-config`,
            method: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success && response.data) {
                    fieldConfigs = response.data;
                    // If we're in edit mode, we'll update the form after loading the datasource
                    if (!isEditMode) {
                        updateFormFields();
                    }
                } else {
                    showNotification('Failed to load field configurations', 'error');
                }
            },
            error: function(xhr) {
                let errorMessage = 'Failed to load field configurations';
                if (xhr.responseJSON && xhr.responseJSON.errors && xhr.responseJSON.errors.length > 0) {
                    errorMessage = xhr.responseJSON.errors[0].msg || errorMessage;
                }
                showNotification(errorMessage, 'error');
            }
        });
    }

    // Update form fields based on database type
    function updateFormFields() {
        if (!fieldConfigs) return;
        
        const databaseType = $('#database_type').val();
        
        // Hide all configuration sections
        $('.field-group').addClass('hidden');
        
        // Show relevant configuration based on database type
        if (databaseType && fieldConfigs[databaseType]) {
            const config = fieldConfigs[databaseType];
            const sectionId = config.sections[0]?.id;
            if (sectionId) {
                $(`#${sectionId}`).removeClass('hidden');
            }
        }
    }

    // Load existing datasource data
    function loadDatasource(id) {
        showLoadingState();

        makeApiRequest({
            url: `${API_BASE_URL}/datasources/${id}`,
            method: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success && response.data) {
                    populateForm(response.data);
                } else {
                    showNotification('Failed to load datasource: ' + (response.errors?.[0]?.msg || 'Unknown error'), 'error');
                    setTimeout(() => window.location.href = APP_CONFIG.urls.datasource(), 2000);
                }
            },
            error: function(xhr, status, error) {
                let errorMessage = 'Failed to load datasource';
                if (xhr.responseJSON && xhr.responseJSON.errors && xhr.responseJSON.errors.length > 0) {
                    errorMessage = xhr.responseJSON.errors[0].msg || errorMessage;
                }
                showNotification(errorMessage, 'error');
                setTimeout(() => window.location.href = APP_CONFIG.urls.datasource(), 2000);
            },
            complete: function() {
                hideLoadingState();
            }
        });
    }

    // Populate form with datasource data
    function populateForm(datasource) {
        $('#datasourceId').val(datasource.id);
        $('#name').val(datasource.name);
        $('#database_type').val(datasource.database_type);
        
        // Populate fields based on database type
        switch (datasource.database_type) {
            case 'sqlite':
                $('#sqlite_database').val(datasource.database);
                break;
            case 'postgresql':
            case 'mysql':
                $('#host').val(datasource.host || '');
                $('#port').val(datasource.port || '');
                $('#database').val(datasource.database);
                $('#username').val(datasource.username || '');
                $('#ssl_mode').val(datasource.ssl_mode || '');
                break;
            case 'databricks':
                $('#databricks_host').val(datasource.host || '');
                $('#http_path').val(datasource.additional_params?.http_path || '');
                $('#catalog').val(datasource.additional_params?.catalog || '');
                $('#schema').val(datasource.additional_params?.schema || '');
                break;
        }
        
        $('#connection_string').val(datasource.connection_string || '');
        
        // Format additional_params as pretty JSON
        const additionalParams = datasource.additional_params || {};
        $('#additional_params').val(JSON.stringify(additionalParams, null, 2));
        
        // Update form fields visibility
        updateFormFields();
    }

    // Save datasource (create or update)
    function saveDatasource() {
        const formData = getFormData();
        
        if (!validateForm(formData)) {
            return;
        }

        const $saveBtn = $('#saveBtn');
        const originalText = $saveBtn.text();
        $saveBtn.text('Saving...').prop('disabled', true);

        const url = isEditMode ? `${API_BASE_URL}/datasources/${currentDatasourceId}` : `${API_BASE_URL}/datasources`;
        const method = isEditMode ? 'PUT' : 'POST';

        makeApiRequest({
            url: url,
            method: method,
            contentType: 'application/json',
            data: JSON.stringify(formData),
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    showNotification(isEditMode ? 'Datasource updated successfully' : 'Datasource created successfully', 'success');
                    setTimeout(() => window.location.href = APP_CONFIG.urls.datasource(), 1500);
                } else {
                    const errorMessage = response.errors?.[0]?.msg || 'Unknown error occurred';
                    showNotification('Failed to save datasource: ' + errorMessage, 'error');
                }
            },
            error: function(xhr) {
                let errorMessage = 'Failed to save datasource';
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

    // Delete datasource
    function deleteDatasource() {
        const $deleteBtn = $('#deleteBtn');
        $deleteBtn.text('Deleting...').prop('disabled', true);

        makeApiRequest({
            url: `${API_BASE_URL}/datasources/${currentDatasourceId}`,
            method: 'DELETE',
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    showNotification('Datasource deleted successfully', 'success');
                    setTimeout(() => window.location.href = APP_CONFIG.urls.datasource(), 1500);
                } else {
                    const errorMessage = response.errors?.[0]?.msg || 'Unknown error occurred';
                    showNotification('Failed to delete datasource: ' + errorMessage, 'error');
                }
            },
            error: function(xhr) {
                let errorMessage = 'Failed to delete datasource';
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

    // Test database connection
    function testConnection() {
        if (!isEditMode) {
            showNotification('Please save the datasource first before testing the connection', 'warning');
            return;
        }

        const $testBtn = $('#testConnectionBtn');
        const originalText = $testBtn.text();
        $testBtn.text('Testing...').prop('disabled', true);

        makeApiRequest({
            url: `${API_BASE_URL}/datasources/${currentDatasourceId}/test`,
            method: 'POST',
            dataType: 'json',
            success: function(response) {
                if (response.success && response.data) {
                    const data = response.data;
                    showNotification(`Connection successful! (${data.connection_time_ms}ms)`, 'success');
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
                $testBtn.text(originalText).prop('disabled', false);
            }
        });
    }

    // Get form data based on database type
    function getFormData() {
        const databaseType = $('#database_type').val();
        const formData = {
            name: $('#name').val().trim(),
            database_type: databaseType
        };

        // Add fields based on database type
        switch (databaseType) {
            case 'sqlite':
                formData.database = $('#sqlite_database').val().trim();
                break;
            case 'postgresql':
            case 'mysql':
                formData.host = $('#host').val().trim() || null;
                formData.port = $('#port').val() ? parseInt($('#port').val()) : null;
                formData.database = $('#database').val().trim();
                formData.username = $('#username').val().trim() || null;
                formData.password = $('#password').val() || null;
                formData.ssl_mode = $('#ssl_mode').val() || null;
                break;
            case 'databricks':
                formData.host = $('#databricks_host').val().trim() || null;
                formData.password = $('#databricks_token').val() || null;
                formData.database = 'databricks'; // Default database name for Databricks
                
                // Build additional_params for Databricks
                const additionalParams = {};
                const httpPath = $('#http_path').val().trim();
                const catalog = $('#catalog').val().trim();
                const schema = $('#schema').val().trim();
                
                if (httpPath) additionalParams.http_path = httpPath;
                if (catalog) additionalParams.catalog = catalog;
                if (schema) additionalParams.schema = schema;
                
                formData.additional_params = additionalParams;
                break;
        }

        // Add common fields
        formData.connection_string = $('#connection_string').val().trim() || null;

        // Parse additional_params JSON if not already set
        if (!formData.additional_params) {
            try {
                const additionalParamsValue = $('#additional_params').val().trim();
                formData.additional_params = additionalParamsValue ? JSON.parse(additionalParamsValue) : {};
            } catch (e) {
                formData.additional_params = {};
            }
        }

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

    // Form validation based on field configurations from API
    function validateForm(data) {
        let isValid = true;
        
        // Clear previous errors
        $('.border-red-300').removeClass('border-red-300').addClass('border-gray-300');

        // Required fields for all types
        if (!data.name) {
            $('#name').removeClass('border-gray-300').addClass('border-red-300');
            isValid = false;
        }

        if (!data.database_type) {
            $('#database_type').removeClass('border-gray-300').addClass('border-red-300');
            isValid = false;
        }

        // Type-specific validation using field configurations
        if (data.database_type && fieldConfigs && fieldConfigs[data.database_type]) {
            const config = fieldConfigs[data.database_type];
            config.fields.forEach(field => {
                if (field.required) {
                    const fieldValue = $(`#${field.name}`).val().trim();
                    if (!fieldValue) {
                        $(`#${field.name}`).removeClass('border-gray-300').addClass('border-red-300');
                        isValid = false;
                    }
                }
            });
        }

        // Validate JSON in additional_params
        try {
            const additionalParamsValue = $('#additional_params').val().trim();
            if (additionalParamsValue) {
                JSON.parse(additionalParamsValue);
            }
        } catch (e) {
            $('#additional_params').removeClass('border-gray-300').addClass('border-red-300');
            showNotification('Invalid JSON in Additional Parameters', 'error');
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