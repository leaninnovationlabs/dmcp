$(document).ready(function() {
    const API_BASE_URL = APP_CONFIG.API_BASE_URL;
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
        // Load datasources first, then load the tool to ensure proper population
        loadDatasources().then(() => {
            loadTool(toolId);
        });
    } else {
        $('#pageTitle').text('Create New Tool');
        $('#saveBtn').text('Create Tool');
        loadDatasources();
        hideLoadingState();
    }

    // Event listeners
    $('#backBtn, #cancelBtn').on('click', function() {
        window.location.href = APP_CONFIG.urls.tools();
    });

    $('#toolForm').on('submit', function(e) {
        e.preventDefault();
        saveTool();
    });

    // Handle tool type selection - prevent unsupported types
    $('#type').on('change', function() {
        const selectedType = $(this).val();
        if (selectedType === 'http' || selectedType === 'code') {
            alert('Tool type "' + selectedType.charAt(0).toUpperCase() + selectedType.slice(1) + '" is not supported yet. Please select a different tool type.');
            $(this).val(''); // Reset to empty selection
            return false;
        }
    });

    $('#deleteBtn').on('click', function() {
        if (confirm('Are you sure you want to delete this tool? This action cannot be undone.')) {
            deleteTool();
        }
    });

    $('#executeBtn').on('click', function() {
        showExecuteModal();
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

    // Modal event handlers
    $('#closeExecuteModal, #cancelExecute, #closeResults').on('click', function() {
        hideExecuteModal();
    });

    $('#executeModal').on('click', function(e) {
        if (e.target === this) {
            hideExecuteModal();
        }
    });

    $('#executeForm').on('submit', function(e) {
        e.preventDefault();
        executeToolWithParameters();
    });

    $('#runAgain').on('click', function() {
        showParametersSection();
    });

    $('#exportResults').on('click', function() {
        exportResultsToCSV();
    });

    // Load datasources for dropdown
    function loadDatasources() {
        return makeApiRequest({
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

        makeApiRequest({
            url: `${API_BASE_URL}/tools/${id}`,
            method: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.success && response.data) {
                    populateForm(response.data);
                } else {
                    showNotification('Failed to load tool: ' + (response.errors?.[0]?.msg || 'Unknown error'), 'error');
                    setTimeout(() => window.location.href = APP_CONFIG.urls.tools(), 2000);
                }
            },
            error: function(xhr, status, error) {
                let errorMessage = 'Failed to load tool';
                if (xhr.responseJSON && xhr.responseJSON.errors && xhr.responseJSON.errors.length > 0) {
                    errorMessage = xhr.responseJSON.errors[0].msg || errorMessage;
                }
                showNotification(errorMessage, 'error');
                setTimeout(() => window.location.href = APP_CONFIG.urls.tools(), 2000);
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

        makeApiRequest({
            url: url,
            method: method,
            contentType: 'application/json',
            data: JSON.stringify(formData),
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    showNotification(isEditMode ? 'Tool updated successfully' : 'Tool created successfully', 'success');
                    setTimeout(() => window.location.href = APP_CONFIG.urls.tools(), 1500);
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

        makeApiRequest({
            url: `${API_BASE_URL}/tools/${currentToolId}`,
            method: 'DELETE',
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    showNotification('Tool deleted successfully', 'success');
                    setTimeout(() => window.location.href = APP_CONFIG.urls.tools(), 1500);
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

    // Show execute modal
    function showExecuteModal() {
        if (!isEditMode) {
            showNotification('Please save the tool first before executing it', 'warning');
            return;
        }

        // Get current tool data
        const toolData = getCurrentToolData();
        
        // Populate modal with tool info
        $('#executeToolName').text(toolData.name);
        $('#executeToolDescription').text(toolData.description || 'No description provided');
        
        // Generate parameter inputs
        generateParameterInputs(toolData.parameters);
        
        // Show modal
        $('#executeModal').removeClass('hidden');
        $('body').addClass('overflow-hidden');
    }

    // Hide execute modal
    function hideExecuteModal() {
        $('#executeModal').addClass('hidden');
        $('body').removeClass('overflow-hidden');
        $('#executeParametersContainer').empty();
        showParametersSection();
    }

    // Show parameters section
    function showParametersSection() {
        $('#parametersSection').removeClass('hidden');
        $('#resultsSection').addClass('hidden');
        $('#confirmExecute').prop('disabled', false).html('<i class="fas fa-play mr-2"></i>Execute Tool');
    }

    // Show results section
    function showResultsSection() {
        $('#parametersSection').addClass('hidden');
        $('#resultsSection').removeClass('hidden');
    }

    // Get current tool data from form
    function getCurrentToolData() {
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

        return {
            name: $('#name').val().trim(),
            description: $('#description').val().trim() || null,
            parameters: parameters
        };
    }

    // Generate parameter inputs for execution
    function generateParameterInputs(parameters) {
        const $container = $('#executeParametersContainer');
        $container.empty();

        if (!parameters || parameters.length === 0) {
            $('#executeNoParametersMessage').removeClass('hidden');
            return;
        }

        $('#executeNoParametersMessage').addClass('hidden');

        parameters.forEach(param => {
            const inputHtml = generateParameterInput(param);
            $container.append(inputHtml);
        });
    }

    // Generate individual parameter input
    function generateParameterInput(param) {
        const required = param.required ? 'required' : '';
        const requiredLabel = param.required ? ' <span class="text-red-500">*</span>' : '';
        const defaultValue = param.default || '';
        const placeholder = defaultValue ? `Default: ${defaultValue}` : '';

        let inputElement;
        
        switch (param.type) {
            case 'boolean':
                inputElement = `
                    <select name="param_${param.name}" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent" ${required}>
                        <option value="">Select value</option>
                        <option value="true" ${defaultValue === 'true' ? 'selected' : ''}>True</option>
                        <option value="false" ${defaultValue === 'false' ? 'selected' : ''}>False</option>
                    </select>
                `;
                break;
            
            case 'integer':
                inputElement = `
                    <input type="number" name="param_${param.name}" 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent" 
                           step="1" value="${defaultValue}" placeholder="${placeholder}" ${required}>
                `;
                break;
            
            case 'float':
                inputElement = `
                    <input type="number" name="param_${param.name}" 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent" 
                           step="any" value="${defaultValue}" placeholder="${placeholder}" ${required}>
                `;
                break;
            
            case 'date':
                inputElement = `
                    <input type="date" name="param_${param.name}" 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent" 
                           value="${defaultValue}" ${required}>
                `;
                break;
            
            case 'datetime':
                inputElement = `
                    <input type="datetime-local" name="param_${param.name}" 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent" 
                           value="${defaultValue}" ${required}>
                `;
                break;
            
            case 'array':
                inputElement = `
                    <textarea name="param_${param.name}" rows="3" 
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent" 
                              placeholder="Enter values separated by commas${placeholder ? '. ' + placeholder : ''}" ${required}>${defaultValue}</textarea>
                    <p class="text-xs text-gray-500 mt-1">Enter multiple values separated by commas</p>
                `;
                break;
            
            case 'object':
                inputElement = `
                    <textarea name="param_${param.name}" rows="4" 
                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent font-mono text-sm" 
                              placeholder="Enter JSON object${placeholder ? '. ' + placeholder : ''}" ${required}>${defaultValue}</textarea>
                    <p class="text-xs text-gray-500 mt-1">Enter a valid JSON object</p>
                `;
                break;
            
            default: // string
                inputElement = `
                    <input type="text" name="param_${param.name}" 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent" 
                           value="${defaultValue}" placeholder="${placeholder}" ${required}>
                `;
                break;
        }

        return $(`
            <div class="parameter-input-group">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    ${escapeHtml(param.name)}${requiredLabel}
                    ${param.description ? `<span class="text-gray-500 font-normal"> - ${escapeHtml(param.description)}</span>` : ''}
                </label>
                ${inputElement}
            </div>
        `);
    }

    // Execute tool with parameters
    function executeToolWithParameters() {
        const parameters = getExecutionParameters();
        
        if (parameters === null) {
            return; // Validation failed
        }

        const $executeBtn = $('#confirmExecute');
        const originalText = $executeBtn.html();
        $executeBtn.html('<i class="fas fa-spinner fa-spin mr-2"></i>Executing...').prop('disabled', true);

        makeApiRequest({
            url: `${API_BASE_URL}/tools/execute/${currentToolId}`,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ parameters: parameters }),
            dataType: 'json',
            success: function(response) {
                if (response.success && response.data) {
                    // Check if the inner data indicates success or failure
                    if (response.data.success) {
                        const data = response.data;
                        displayExecutionResults(data);
                    } else {
                        // Handle error from the inner data
                        const errorMessage = response.data.error || 'Tool execution failed';
                        showNotification(`Execution failed: ${errorMessage}`, 'error');
                    }
                } else {
                    const errorMessage = response.errors?.[0]?.msg || 'Tool execution failed';
                    showNotification(errorMessage, 'error');
                }
            },
            error: function(xhr) {
                let errorMessage = 'Tool execution failed';
                if (xhr.responseJSON && xhr.responseJSON.errors && xhr.responseJSON.errors.length > 0) {
                    errorMessage = xhr.responseJSON.errors[0].msg || errorMessage;
                } else if (xhr.responseText) {
                    try {
                        const errorData = JSON.parse(xhr.responseText);
                        errorMessage = errorData.detail || errorMessage;
                    } catch (e) {
                        // Use default error message
                    }
                }
                showNotification(errorMessage, 'error');
            },
            complete: function() {
                $executeBtn.html(originalText).prop('disabled', false);
            }
        });
    }

    // Get parameters from execution form
    function getExecutionParameters() {
        const parameters = {};
        const toolData = getCurrentToolData();
        let hasErrors = false;

        // Clear previous errors
        $('.border-red-300').removeClass('border-red-300').addClass('border-gray-300');

        toolData.parameters.forEach(paramConfig => {
            const $input = $(`[name="param_${paramConfig.name}"]`);
            let value = $input.val();

            // Handle required validation
            if (paramConfig.required && (!value || value.trim() === '')) {
                $input.removeClass('border-gray-300').addClass('border-red-300');
                showNotification(`${paramConfig.name} is required`, 'error');
                hasErrors = true;
                return;
            }

            // Skip if empty and not required
            if (!value || value.trim() === '') {
                return;
            }

            // Type conversion and validation
            try {
                switch (paramConfig.type) {
                    case 'integer':
                        value = parseInt(value);
                        if (isNaN(value)) {
                            throw new Error('Invalid integer');
                        }
                        break;
                    
                    case 'float':
                        value = parseFloat(value);
                        if (isNaN(value)) {
                            throw new Error('Invalid number');
                        }
                        break;
                    
                    case 'boolean':
                        value = value.toLowerCase() === 'true';
                        break;
                    
                    case 'array':
                        value = value.split(',').map(item => item.trim()).filter(item => item);
                        break;
                    
                    case 'object':
                        value = JSON.parse(value);
                        break;
                    
                    default: // string, date, datetime
                        value = value.trim();
                        break;
                }
                
                parameters[paramConfig.name] = value;
            } catch (error) {
                $input.removeClass('border-gray-300').addClass('border-red-300');
                showNotification(`Invalid value for ${paramConfig.name}: ${error.message}`, 'error');
                hasErrors = true;
            }
        });

        return hasErrors ? null : parameters;
    }

    // Display execution results
    function displayExecutionResults(data) {
        const rowCount = data.row_count || 0;
        const executionTime = data.execution_time_ms || 0;
        
        // Update summary
        $('#executionSummary').html(`${rowCount} rows returned in ${executionTime}ms`);
        
        console.log(data)
        // Display results table
        if (data.data && data.data.length > 0) {
            displayResultsTable(data.data);
            $('#resultsTableContainer').removeClass('hidden');
            $('#noResultsMessage').addClass('hidden');
        } else {
            $('#resultsTableContainer').addClass('hidden');
            $('#noResultsMessage').removeClass('hidden');
        }
        
        // Switch to results section
        showResultsSection();
        
        // Show success notification
        showNotification(`Tool executed successfully! ${rowCount} rows returned`, 'success');
    }

    // Display results in table format
    function displayResultsTable(results) {
        const $table = $('#resultsTable');
        const $thead = $table.find('thead');
        const $tbody = $table.find('tbody');
        
        console.log(results)
        // Clear existing content
        $thead.empty();
        $tbody.empty();
        
        if (results.length === 0) {
            return;
        }
        
        // Get column names from first row
        const columns = Object.keys(results[0]);
        
        // Create header row
        const headerRow = $('<tr></tr>');
        columns.forEach(column => {
            const th = $(`<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-200">${escapeHtml(column)}</th>`);
            headerRow.append(th);
        });
        $thead.append(headerRow);
        
        // Create data rows
        results.forEach((row, rowIndex) => {
            const dataRow = $(`<tr class="${rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-blue-50"></tr>`);
            
            columns.forEach(column => {
                const value = row[column];
                const formattedValue = formatCellValue(value);
                const td = $(`<td class="px-4 py-3 text-sm text-gray-900 border-b border-gray-200">${formattedValue}</td>`);
                dataRow.append(td);
            });
            
            $tbody.append(dataRow);
        });
    }

    // Format cell value for display
    function formatCellValue(value) {
        if (value === null || value === undefined) {
            return '<span class="text-gray-400 italic">NULL</span>';
        }
        
        if (typeof value === 'boolean') {
            return value ? '<span class="text-green-600 font-semibold">TRUE</span>' : '<span class="text-red-600 font-semibold">FALSE</span>';
        }
        
        if (typeof value === 'number') {
            // Format numbers with appropriate precision
            return value % 1 === 0 ? value.toString() : value.toFixed(2);
        }
        
        if (typeof value === 'object') {
            return `<code class="bg-gray-100 px-1 rounded text-xs">${escapeHtml(JSON.stringify(value))}</code>`;
        }
        
        // String values - truncate if too long
        const stringValue = String(value);
        if (stringValue.length > 100) {
            return `<span title="${escapeHtml(stringValue)}">${escapeHtml(stringValue.substring(0, 100))}...</span>`;
        }
        
        return escapeHtml(stringValue);
    }

    // Export results to CSV
    function exportResultsToCSV() {
        const $table = $('#resultsTable');
        const $thead = $table.find('thead tr');
        const $tbody = $table.find('tbody tr');
        
        if ($thead.length === 0 || $tbody.length === 0) {
            showNotification('No data to export', 'warning');
            return;
        }
        
        let csv = '';
        
        // Add headers
        const headers = [];
        $thead.find('th').each(function() {
            headers.push($(this).text().trim());
        });
        csv += headers.map(header => `"${header.replace(/"/g, '""')}"`).join(',') + '\n';
        
        // Add data rows
        $tbody.each(function() {
            const row = [];
            $(this).find('td').each(function() {
                let cellText = $(this).text().trim();
                // Clean up formatted values
                if (cellText === 'NULL') cellText = '';
                if (cellText === 'TRUE') cellText = 'true';
                if (cellText === 'FALSE') cellText = 'false';
                row.push(cellText);
            });
            csv += row.map(cell => `"${cell.replace(/"/g, '""')}"`).join(',') + '\n';
        });
        
        // Create download link
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        
        const toolName = $('#executeToolName').text().replace(/[^a-zA-Z0-9]/g, '_');
        const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '');
        link.setAttribute('download', `${toolName}_results_${timestamp}.csv`);
        
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showNotification('Results exported to CSV', 'success');
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

        // Check for unsupported tool types
        if (data.type === 'http' || data.type === 'code') {
            $('#type').removeClass('border-gray-300').addClass('border-red-300');
            showNotification('Tool type "' + data.type.charAt(0).toUpperCase() + data.type.slice(1) + '" is not supported yet. Please select a different tool type.', 'error');
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