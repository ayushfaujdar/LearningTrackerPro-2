document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initApp();
});

/**
 * Initialize the application
 */
function initApp() {
    // Initialize form event listeners
    initFormEventListeners();
    
    // Initialize history from localStorage
    loadHistoryFromStorage();
    
    // Pre-fill form with sample data for demo purposes
    // Uncomment to enable demo mode
    // fillSampleData();
}

/**
 * Initialize all form event listeners
 */
function initFormEventListeners() {
    // Add developer button
    document.getElementById('add-developer').addEventListener('click', addDeveloperRow);
    
    // Add project button
    document.getElementById('add-project').addEventListener('click', addProjectRow);
    
    // Form submission
    document.getElementById('optimization-form').addEventListener('submit', handleFormSubmit);
    
    // Reset button
    document.getElementById('reset-btn').addEventListener('click', resetForm);
    
    // Data import button
    document.getElementById('import-data-btn').addEventListener('click', toggleImportOptions);
    
    // Sample data button
    document.getElementById('sample-data-btn').addEventListener('click', loadSampleData);
    
    // CSV/Excel import button
    document.getElementById('csv-import-btn').addEventListener('click', triggerFileUpload);
    
    // File upload change
    document.getElementById('file-upload').addEventListener('change', handleFileUpload);
    
    // Enable remove buttons when there's more than one row
    updateRemoveButtons();
}

/**
 * Add a new developer row to the form
 */
function addDeveloperRow() {
    const devContainer = document.getElementById('developers-container');
    const newRow = document.createElement('div');
    newRow.className = 'developer-row';
    
    newRow.innerHTML = `
        <div class="form-row">
            <div class="form-group">
                <label>Name</label>
                <input type="text" class="dev-name" required>
            </div>
            <div class="form-group">
                <label>Rate ($/hour)</label>
                <input type="number" class="dev-rate" min="1" required>
            </div>
            <div class="form-group">
                <label>Hours/day</label>
                <input type="number" class="dev-hours" min="1" max="24" required>
            </div>
            <div class="form-group">
                <label>Skills (comma separated)</label>
                <input type="text" class="dev-skills" placeholder="Python, UI, Database">
            </div>
            <button type="button" class="remove-btn" title="Remove"><i data-feather="x-circle"></i></button>
        </div>
    `;
    
    devContainer.appendChild(newRow);
    
    // Initialize the feather icon
    feather.replace();
    
    // Add event listener to remove button
    newRow.querySelector('.remove-btn').addEventListener('click', function() {
        devContainer.removeChild(newRow);
        updateRemoveButtons();
    });
    
    // Enable/disable remove buttons
    updateRemoveButtons();
}

/**
 * Add a new project row to the form
 */
function addProjectRow() {
    const projContainer = document.getElementById('projects-container');
    const newRow = document.createElement('div');
    newRow.className = 'project-row';
    
    newRow.innerHTML = `
        <div class="form-row">
            <div class="form-group">
                <label>Name</label>
                <input type="text" class="proj-name" required>
            </div>
            <div class="form-group">
                <label>Hours</label>
                <input type="number" class="proj-hours" min="1" required>
            </div>
            <div class="form-group">
                <label>Priority (1-5)</label>
                <input type="number" class="proj-priority" min="1" max="5" value="3" required>
            </div>
            <div class="form-group">
                <label>Dependencies</label>
                <input type="text" class="proj-deps" placeholder="Project1, Project2">
            </div>
            <div class="form-group">
                <label>Required Skills</label>
                <input type="text" class="proj-skills" placeholder="Python, UI">
            </div>
            <button type="button" class="remove-btn" title="Remove"><i data-feather="x-circle"></i></button>
        </div>
    `;
    
    projContainer.appendChild(newRow);
    
    // Initialize the feather icon
    feather.replace();
    
    // Add event listener to remove button
    newRow.querySelector('.remove-btn').addEventListener('click', function() {
        projContainer.removeChild(newRow);
        updateRemoveButtons();
    });
    
    // Enable/disable remove buttons
    updateRemoveButtons();
}

/**
 * Update the state of remove buttons
 * Disable if there's only one row, enable otherwise
 */
function updateRemoveButtons() {
    // Developers
    const devRows = document.querySelectorAll('#developers-container .developer-row');
    const devButtons = document.querySelectorAll('#developers-container .remove-btn');
    
    devButtons.forEach(btn => {
        btn.disabled = devRows.length <= 1;
    });
    
    // Projects
    const projRows = document.querySelectorAll('#projects-container .project-row');
    const projButtons = document.querySelectorAll('#projects-container .remove-btn');
    
    projButtons.forEach(btn => {
        btn.disabled = projRows.length <= 1;
    });
}

/**
 * Handle form submission
 */
async function handleFormSubmit(event) {
    event.preventDefault();
    
    try {
        // Show loading state
        const optimizeBtn = document.getElementById('optimize-btn');
        const originalBtnText = optimizeBtn.innerHTML;
        optimizeBtn.innerHTML = '<i data-feather="loader"></i> Processing...';
        optimizeBtn.disabled = true;
        feather.replace();
        
        // Collect form data
        const formData = collectFormData();
        
        // Validate form data
        if (!validateFormData(formData)) {
            throw new Error('Please check your inputs and try again.');
        }
        
        // Send data to server
        const response = await fetch('/optimize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        // Check for errors
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Optimization failed');
        }
        
        // Process response
        const result = await response.json();
        
        // Display results
        displayResults(result, formData);
        
        // Save to history
        saveToHistory(formData, result);
        
        // Scroll to results
        document.getElementById('results-section').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        console.error('Error:', error);
        alert(error.message || 'An error occurred during optimization');
    } finally {
        // Restore button state
        const optimizeBtn = document.getElementById('optimize-btn');
        optimizeBtn.innerHTML = '<i data-feather="cpu"></i> Optimize Now';
        optimizeBtn.disabled = false;
        feather.replace();
    }
}

/**
 * Collect all form data into a structured object
 */
function collectFormData() {
    // Get budget and deadline
    const budget = parseFloat(document.getElementById('budget').value);
    const deadline = parseFloat(document.getElementById('deadline').value);
    
    // Get developers
    const developers = [];
    const devNames = document.querySelectorAll('.dev-name');
    const devRates = document.querySelectorAll('.dev-rate');
    const devHours = document.querySelectorAll('.dev-hours');
    const devSkills = document.querySelectorAll('.dev-skills');
    
    for (let i = 0; i < devNames.length; i++) {
        if (devNames[i].value.trim()) {
            developers.push({
                name: devNames[i].value.trim(),
                rate: parseFloat(devRates[i].value),
                hours_per_day: parseFloat(devHours[i].value),
                skills: devSkills[i].value.split(',').map(s => s.trim()).filter(s => s)
            });
        }
    }
    
    // Get projects
    const projects = [];
    const projNames = document.querySelectorAll('.proj-name');
    const projHours = document.querySelectorAll('.proj-hours');
    const projPriorities = document.querySelectorAll('.proj-priority');
    const projDeps = document.querySelectorAll('.proj-deps');
    const projSkills = document.querySelectorAll('.proj-skills');
    
    for (let i = 0; i < projNames.length; i++) {
        if (projNames[i].value.trim()) {
            projects.push({
                name: projNames[i].value.trim(),
                hours: parseFloat(projHours[i].value),
                priority: parseInt(projPriorities[i].value),
                dependencies: projDeps[i].value.split(',').map(d => d.trim()).filter(d => d),
                required_skills: projSkills[i].value.split(',').map(s => s.trim()).filter(s => s)
            });
        }
    }
    
    return {
        budget,
        deadline,
        developers,
        projects
    };
}

/**
 * Validate the form data
 */
function validateFormData(data) {
    // Check if we have at least one developer and one project
    if (data.developers.length === 0) {
        alert('Please add at least one developer');
        return false;
    }
    
    if (data.projects.length === 0) {
        alert('Please add at least one project');
        return false;
    }
    
    // Check for unique developer names
    const devNames = new Set();
    for (const dev of data.developers) {
        if (devNames.has(dev.name)) {
            alert(`Duplicate developer name: ${dev.name}`);
            return false;
        }
        devNames.add(dev.name);
    }
    
    // Check for unique project names
    const projNames = new Set();
    for (const proj of data.projects) {
        if (projNames.has(proj.name)) {
            alert(`Duplicate project name: ${proj.name}`);
            return false;
        }
        projNames.add(proj.name);
    }
    
    // Check for valid dependencies
    for (const proj of data.projects) {
        for (const dep of proj.dependencies) {
            if (!projNames.has(dep)) {
                alert(`Dependency "${dep}" in project "${proj.name}" doesn't exist`);
                return false;
            }
            
            // Check for circular dependencies
            if (dep === proj.name) {
                alert(`Project "${proj.name}" cannot depend on itself`);
                return false;
            }
        }
    }
    
    return true;
}

/**
 * Reset the form to its initial state
 */
function resetForm() {
    // Reset budget and deadline
    document.getElementById('budget').value = '';
    document.getElementById('deadline').value = '';
    
    // Reset developers (keep one empty row)
    const devContainer = document.getElementById('developers-container');
    while (devContainer.firstChild) {
        devContainer.removeChild(devContainer.firstChild);
    }
    addDeveloperRow();
    
    // Reset projects (keep one empty row)
    const projContainer = document.getElementById('projects-container');
    while (projContainer.firstChild) {
        projContainer.removeChild(projContainer.firstChild);
    }
    addProjectRow();
    
    // Hide results
    document.getElementById('results-section').style.display = 'none';
}

/**
 * Display the optimization results
 */
function displayResults(result, formData) {
    // Show results section
    document.getElementById('results-section').style.display = 'block';
    
    // Update metrics
    document.getElementById('total-cost').textContent = result.total_cost.toFixed(2);
    document.getElementById('budget-value').textContent = formData.budget.toFixed(2);
    document.getElementById('budget-remaining').textContent = result.budget_remaining.toFixed(2);
    document.getElementById('completion-time').textContent = result.completion_time.toFixed(1);
    document.getElementById('deadline-value').textContent = formData.deadline.toFixed(1);
    document.getElementById('time-buffer').textContent = result.time_buffer.toFixed(1);
    
    // Update risks
    const risksList = document.getElementById('risks-list');
    risksList.innerHTML = '';
    
    if (result.risks && result.risks.length > 0) {
        result.risks.forEach(risk => {
            const li = document.createElement('li');
            li.className = `risk-${risk.severity}`;
            li.textContent = risk.message;
            risksList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'No risks identified';
        risksList.appendChild(li);
    }
    
    // Update assignments table
    const assignmentsBody = document.getElementById('assignments-body');
    assignmentsBody.innerHTML = '';
    
    result.assignments.forEach(assignment => {
        const tr = document.createElement('tr');
        
        tr.innerHTML = `
            <td>${assignment.developer}</td>
            <td>${assignment.project}</td>
            <td>${assignment.hours}</td>
            <td>$${assignment.cost.toFixed(2)}</td>
            <td>${assignment.skill_match}%</td>
        `;
        
        assignmentsBody.appendChild(tr);
    });
    
    // Update AI explanation
    document.getElementById('ai-explanation').textContent = result.explanation;
    
    // Update recommendations
    const recommendationsList = document.getElementById('recommendations-list');
    recommendationsList.innerHTML = '';
    
    if (result.recommendations && result.recommendations.length > 0) {
        result.recommendations.forEach(recommendation => {
            const li = document.createElement('li');
            li.textContent = recommendation;
            recommendationsList.appendChild(li);
        });
    }
    
    // Update charts
    updateCharts(result);
}

/**
 * Save the optimization to history
 */
function saveToHistory(formData, result) {
    // Get existing history from localStorage
    let history = JSON.parse(localStorage.getItem('aqwseHistory')) || [];
    
    // Create a history entry
    const historyEntry = {
        id: Date.now(), // Use timestamp as ID
        timestamp: new Date().toISOString(),
        formData: formData,
        result: result
    };
    
    // Add to history (limit to 10 entries)
    history.unshift(historyEntry);
    if (history.length > 10) {
        history = history.slice(0, 10);
    }
    
    // Save to localStorage
    localStorage.setItem('aqwseHistory', JSON.stringify(history));
    
    // Update history display
    loadHistoryFromStorage();
}

/**
 * Load and display optimization history from localStorage
 */
function loadHistoryFromStorage() {
    const history = JSON.parse(localStorage.getItem('aqwseHistory')) || [];
    const historyList = document.getElementById('history-list');
    const emptyState = document.getElementById('history-empty-state');
    
    // Clear existing items
    historyList.innerHTML = '';
    
    if (history.length === 0) {
        emptyState.style.display = 'block';
        return;
    }
    
    // Hide empty state and show history
    emptyState.style.display = 'none';
    
    // Add history items
    history.forEach(entry => {
        const historyItem = document.createElement('li');
        historyItem.className = 'history-item';
        historyItem.dataset.id = entry.id;
        
        // Format date
        const date = new Date(entry.timestamp);
        const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        
        // Create title from the data
        const devCount = entry.formData.developers.length;
        const projCount = entry.formData.projects.length;
        
        historyItem.innerHTML = `
            <div class="history-item-header">
                <div class="history-item-title">${devCount} Developers, ${projCount} Projects</div>
                <div class="history-item-date">${formattedDate}</div>
            </div>
            <div class="history-item-metrics">
                <div class="history-item-metric">
                    <i data-feather="dollar-sign"></i> $${entry.result.total_cost.toFixed(2)}
                </div>
                <div class="history-item-metric">
                    <i data-feather="clock"></i> ${entry.result.completion_time.toFixed(1)} days
                </div>
                <div class="history-item-metric">
                    <i data-feather="alert-triangle"></i> ${entry.result.risks ? entry.result.risks.length : 0} risks
                </div>
            </div>
        `;
        
        // Add click event to reload this optimization
        historyItem.addEventListener('click', () => {
            loadOptimizationFromHistory(entry);
        });
        
        historyList.appendChild(historyItem);
    });
    
    // Initialize feather icons
    feather.replace();
}

/**
 * Load an optimization from history
 */
function loadOptimizationFromHistory(historyEntry) {
    // Populate form with data from history
    document.getElementById('budget').value = historyEntry.formData.budget;
    document.getElementById('deadline').value = historyEntry.formData.deadline;
    
    // Reset developers and projects containers
    const devContainer = document.getElementById('developers-container');
    const projContainer = document.getElementById('projects-container');
    
    while (devContainer.firstChild) {
        devContainer.removeChild(devContainer.firstChild);
    }
    
    while (projContainer.firstChild) {
        projContainer.removeChild(projContainer.firstChild);
    }
    
    // Add developers from history
    historyEntry.formData.developers.forEach(dev => {
        const newRow = document.createElement('div');
        newRow.className = 'developer-row';
        
        newRow.innerHTML = `
            <div class="form-row">
                <div class="form-group">
                    <label>Name</label>
                    <input type="text" class="dev-name" value="${dev.name}" required>
                </div>
                <div class="form-group">
                    <label>Rate ($/hour)</label>
                    <input type="number" class="dev-rate" value="${dev.rate}" min="1" required>
                </div>
                <div class="form-group">
                    <label>Hours/day</label>
                    <input type="number" class="dev-hours" value="${dev.hours_per_day}" min="1" max="24" required>
                </div>
                <div class="form-group">
                    <label>Skills (comma separated)</label>
                    <input type="text" class="dev-skills" value="${dev.skills.join(', ')}" placeholder="Python, UI, Database">
                </div>
                <button type="button" class="remove-btn" title="Remove"><i data-feather="x-circle"></i></button>
            </div>
        `;
        
        devContainer.appendChild(newRow);
        
        // Add event listener to remove button
        newRow.querySelector('.remove-btn').addEventListener('click', function() {
            devContainer.removeChild(newRow);
            updateRemoveButtons();
        });
    });
    
    // Add projects from history
    historyEntry.formData.projects.forEach(proj => {
        const newRow = document.createElement('div');
        newRow.className = 'project-row';
        
        newRow.innerHTML = `
            <div class="form-row">
                <div class="form-group">
                    <label>Name</label>
                    <input type="text" class="proj-name" value="${proj.name}" required>
                </div>
                <div class="form-group">
                    <label>Hours</label>
                    <input type="number" class="proj-hours" value="${proj.hours}" min="1" required>
                </div>
                <div class="form-group">
                    <label>Priority (1-5)</label>
                    <input type="number" class="proj-priority" value="${proj.priority}" min="1" max="5" required>
                </div>
                <div class="form-group">
                    <label>Dependencies</label>
                    <input type="text" class="proj-deps" value="${proj.dependencies.join(', ')}" placeholder="Project1, Project2">
                </div>
                <div class="form-group">
                    <label>Required Skills</label>
                    <input type="text" class="proj-skills" value="${proj.required_skills ? proj.required_skills.join(', ') : ''}" placeholder="Python, UI">
                </div>
                <button type="button" class="remove-btn" title="Remove"><i data-feather="x-circle"></i></button>
            </div>
        `;
        
        projContainer.appendChild(newRow);
        
        // Add event listener to remove button
        newRow.querySelector('.remove-btn').addEventListener('click', function() {
            projContainer.removeChild(newRow);
            updateRemoveButtons();
        });
    });
    
    // Initialize feather icons
    feather.replace();
    
    // Update remove buttons
    updateRemoveButtons();
    
    // Display results
    displayResults(historyEntry.result, historyEntry.formData);
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Toggle import options visibility
 */
function toggleImportOptions() {
    const importOptions = document.getElementById('import-options');
    if (importOptions.classList.contains('hidden')) {
        importOptions.classList.remove('hidden');
    } else {
        importOptions.classList.add('hidden');
    }
}

/**
 * Trigger file upload dialog
 */
function triggerFileUpload() {
    document.getElementById('file-upload').click();
}

/**
 * Handle file upload
 */
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    try {
        // Show loading state
        const importBtn = document.getElementById('csv-import-btn');
        const originalBtnText = importBtn.innerHTML;
        importBtn.innerHTML = '<i data-feather="loader"></i> Importing...';
        importBtn.disabled = true;
        feather.replace();
        
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        
        // Send to server
        const response = await fetch('/import-file', {
            method: 'POST',
            body: formData
        });
        
        // Check for errors
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'File import failed');
        }
        
        // Process response
        const result = await response.json();
        
        // Fill form with imported data
        fillFormWithImportedData(result);
        
        // Hide import options
        document.getElementById('import-options').classList.add('hidden');
        
        // Show success message
        alert(`Successfully imported data from ${file.name}`);
        
    } catch (error) {
        console.error('Error importing file:', error);
        alert(error.message || 'An error occurred during file import');
    } finally {
        // Reset file input
        event.target.value = '';
        
        // Restore button state
        const importBtn = document.getElementById('csv-import-btn');
        importBtn.innerHTML = '<i data-feather="upload"></i> Import CSV/Excel';
        importBtn.disabled = false;
        feather.replace();
    }
}

/**
 * Fill form with imported data
 */
function fillFormWithImportedData(data) {
    // Set budget and deadline
    document.getElementById('budget').value = data.budget;
    document.getElementById('deadline').value = data.deadline;
    
    // Reset developers and projects containers
    const devContainer = document.getElementById('developers-container');
    const projContainer = document.getElementById('projects-container');
    
    while (devContainer.firstChild) {
        devContainer.removeChild(devContainer.firstChild);
    }
    
    while (projContainer.firstChild) {
        projContainer.removeChild(projContainer.firstChild);
    }
    
    // Add developers
    data.developers.forEach(dev => {
        const newRow = document.createElement('div');
        newRow.className = 'developer-row';
        
        newRow.innerHTML = `
            <div class="form-row">
                <div class="form-group">
                    <label>Name</label>
                    <input type="text" class="dev-name" value="${dev.name}" required>
                </div>
                <div class="form-group">
                    <label>Rate ($/hour)</label>
                    <input type="number" class="dev-rate" value="${dev.rate}" min="1" required>
                </div>
                <div class="form-group">
                    <label>Hours/day</label>
                    <input type="number" class="dev-hours" value="${dev.hours_per_day}" min="1" max="24" required>
                </div>
                <div class="form-group">
                    <label>Skills (comma separated)</label>
                    <input type="text" class="dev-skills" value="${dev.skills.join(', ')}" placeholder="Python, UI, Database">
                </div>
                <button type="button" class="remove-btn" title="Remove"><i data-feather="x-circle"></i></button>
            </div>
        `;
        
        devContainer.appendChild(newRow);
        
        // Add event listener to remove button
        newRow.querySelector('.remove-btn').addEventListener('click', function() {
            devContainer.removeChild(newRow);
            updateRemoveButtons();
        });
    });
    
    // Add projects
    data.projects.forEach(proj => {
        const newRow = document.createElement('div');
        newRow.className = 'project-row';
        
        newRow.innerHTML = `
            <div class="form-row">
                <div class="form-group">
                    <label>Name</label>
                    <input type="text" class="proj-name" value="${proj.name}" required>
                </div>
                <div class="form-group">
                    <label>Hours</label>
                    <input type="number" class="proj-hours" value="${proj.hours}" min="1" required>
                </div>
                <div class="form-group">
                    <label>Priority (1-5)</label>
                    <input type="number" class="proj-priority" value="${proj.priority}" min="1" max="5" required>
                </div>
                <div class="form-group">
                    <label>Dependencies</label>
                    <input type="text" class="proj-deps" value="${(proj.dependencies || []).join(', ')}" placeholder="Project1, Project2">
                </div>
                <div class="form-group">
                    <label>Required Skills</label>
                    <input type="text" class="proj-skills" value="${(proj.required_skills || []).join(', ')}" placeholder="Python, UI">
                </div>
                <button type="button" class="remove-btn" title="Remove"><i data-feather="x-circle"></i></button>
            </div>
        `;
        
        projContainer.appendChild(newRow);
        
        // Add event listener to remove button
        newRow.querySelector('.remove-btn').addEventListener('click', function() {
            projContainer.removeChild(newRow);
            updateRemoveButtons();
        });
    });
    
    // Initialize feather icons
    feather.replace();
    
    // Update remove buttons
    updateRemoveButtons();
}

/**
 * Load sample data from server
 */
async function loadSampleData() {
    try {
        // Show loading state
        const sampleBtn = document.getElementById('sample-data-btn');
        const originalBtnText = sampleBtn.innerHTML;
        sampleBtn.innerHTML = '<i data-feather="loader"></i> Loading...';
        sampleBtn.disabled = true;
        feather.replace();
        
        // Fetch sample CSV file
        const response = await fetch('/static/sample_data/sample_workflow.csv');
        
        // Check for errors
        if (!response.ok) {
            throw new Error('Failed to load sample data');
        }
        
        // Convert to blob
        const blob = await response.blob();
        
        // Create file object
        const file = new File([blob], 'sample_workflow.csv', { type: 'text/csv' });
        
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        
        // Send to server for parsing
        const parseResponse = await fetch('/import-file', {
            method: 'POST',
            body: formData
        });
        
        // Check for errors
        if (!parseResponse.ok) {
            const errorData = await parseResponse.json();
            throw new Error(errorData.error || 'Sample data import failed');
        }
        
        // Process response
        const result = await parseResponse.json();
        
        // Fill form with sample data
        fillFormWithImportedData(result);
        
        // Hide import options
        document.getElementById('import-options').classList.add('hidden');
        
    } catch (error) {
        console.error('Error loading sample data:', error);
        alert(error.message || 'An error occurred loading sample data');
        
        // Fallback to hard-coded sample data
        fillSampleData();
    } finally {
        // Restore button state
        const sampleBtn = document.getElementById('sample-data-btn');
        sampleBtn.innerHTML = '<i data-feather="clipboard"></i> Load Sample Data';
        sampleBtn.disabled = false;
        feather.replace();
    }
}

/**
 * Fill form with hard-coded sample data (fallback if server sample fails)
 */
function fillSampleData() {
    // Set budget and deadline
    document.getElementById('budget').value = 50000;
    document.getElementById('deadline').value = 30;
    
    // Reset developers and projects containers
    const devContainer = document.getElementById('developers-container');
    const projContainer = document.getElementById('projects-container');
    
    while (devContainer.firstChild) {
        devContainer.removeChild(devContainer.firstChild);
    }
    
    while (projContainer.firstChild) {
        projContainer.removeChild(projContainer.firstChild);
    }
    
    // Add sample developers
    const sampleDevs = [
        { name: 'John Dev', rate: 75, hours: 8, skills: 'Python, Database, Backend' },
        { name: 'Sarah UI', rate: 85, hours: 6, skills: 'UI, UX, Frontend, JavaScript' },
        { name: 'Mike Full', rate: 95, hours: 8, skills: 'Python, JavaScript, DevOps, Database' },
        { name: 'Lisa Test', rate: 65, hours: 7, skills: 'QA, Testing, Documentation' },
        { name: 'Dave Ops', rate: 90, hours: 6, skills: 'DevOps, AWS, Security' }
    ];
    
    sampleDevs.forEach(dev => {
        const newRow = document.createElement('div');
        newRow.className = 'developer-row';
        
        newRow.innerHTML = `
            <div class="form-row">
                <div class="form-group">
                    <label>Name</label>
                    <input type="text" class="dev-name" value="${dev.name}" required>
                </div>
                <div class="form-group">
                    <label>Rate ($/hour)</label>
                    <input type="number" class="dev-rate" value="${dev.rate}" min="1" required>
                </div>
                <div class="form-group">
                    <label>Hours/day</label>
                    <input type="number" class="dev-hours" value="${dev.hours}" min="1" max="24" required>
                </div>
                <div class="form-group">
                    <label>Skills (comma separated)</label>
                    <input type="text" class="dev-skills" value="${dev.skills}" placeholder="Python, UI, Database">
                </div>
                <button type="button" class="remove-btn" title="Remove"><i data-feather="x-circle"></i></button>
            </div>
        `;
        
        devContainer.appendChild(newRow);
        
        // Add event listener to remove button
        newRow.querySelector('.remove-btn').addEventListener('click', function() {
            devContainer.removeChild(newRow);
            updateRemoveButtons();
        });
    });
    
    // Add sample projects
    const sampleProjs = [
        { name: 'API Development', hours: 80, priority: 5, deps: '', skills: 'Python, Backend, Database' },
        { name: 'User Interface', hours: 60, priority: 4, deps: '', skills: 'UI, UX, Frontend, JavaScript' },
        { name: 'Testing', hours: 40, priority: 3, deps: 'API Development, User Interface', skills: 'QA, Testing' },
        { name: 'Deployment', hours: 30, priority: 2, deps: 'Testing', skills: 'DevOps, AWS' },
        { name: 'Documentation', hours: 20, priority: 1, deps: 'API Development, User Interface', skills: 'Documentation' }
    ];
    
    sampleProjs.forEach(proj => {
        const newRow = document.createElement('div');
        newRow.className = 'project-row';
        
        newRow.innerHTML = `
            <div class="form-row">
                <div class="form-group">
                    <label>Name</label>
                    <input type="text" class="proj-name" value="${proj.name}" required>
                </div>
                <div class="form-group">
                    <label>Hours</label>
                    <input type="number" class="proj-hours" value="${proj.hours}" min="1" required>
                </div>
                <div class="form-group">
                    <label>Priority (1-5)</label>
                    <input type="number" class="proj-priority" value="${proj.priority}" min="1" max="5" required>
                </div>
                <div class="form-group">
                    <label>Dependencies</label>
                    <input type="text" class="proj-deps" value="${proj.deps}" placeholder="Project1, Project2">
                </div>
                <div class="form-group">
                    <label>Required Skills</label>
                    <input type="text" class="proj-skills" value="${proj.skills}" placeholder="Python, UI">
                </div>
                <button type="button" class="remove-btn" title="Remove"><i data-feather="x-circle"></i></button>
            </div>
        `;
        
        projContainer.appendChild(newRow);
        
        // Add event listener to remove button
        newRow.querySelector('.remove-btn').addEventListener('click', function() {
            projContainer.removeChild(newRow);
            updateRemoveButtons();
        });
    });
    
    // Initialize feather icons
    feather.replace();
    
    // Update remove buttons
    updateRemoveButtons();
}
