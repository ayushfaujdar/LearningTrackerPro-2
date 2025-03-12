/**
 * Update charts based on optimization results
 * @param {Object} result - The optimization result data
 */
function updateCharts(result) {
    updateCostChart(result);
    updateTimeChart(result);
}

/**
 * Update the cost distribution chart
 * @param {Object} result - The optimization result data
 */
function updateCostChart(result) {
    const ctx = document.getElementById('cost-chart').getContext('2d');

    // Destroy existing chart if it exists
    if (window.costChart) {
        window.costChart.destroy();
    }

    // Group costs by project
    const projectCosts = {};

    result.assignments.forEach(assignment => {
        if (!projectCosts[assignment.project]) {
            projectCosts[assignment.project] = 0;
        }

        projectCosts[assignment.project] += assignment.cost;
    });

    // Prepare labels and data
    const labels = Object.keys(projectCosts);
    const data = Object.values(projectCosts);

    // Create color array
    const colors = generateColors(labels.length);

    // Create the chart
    window.costChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Cost ($)',
                data: data,
                backgroundColor: colors,
                borderColor: colors.map(c => darkenColor(c, 20)),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `$${context.raw.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Cost ($)'
                    }
                }
            }
        }
    });
}

/**
 * Update the time distribution chart
 * @param {Object} result - The optimization result data
 */
function updateTimeChart(result) {
    const ctx = document.getElementById('time-chart').getContext('2d');

    // Destroy existing chart if it exists
    if (window.timeChart) {
        window.timeChart.destroy();
    }

    // Group hours by project
    const projectHours = {};

    result.assignments.forEach(assignment => {
        if (!projectHours[assignment.project]) {
            projectHours[assignment.project] = 0;
        }

        projectHours[assignment.project] += assignment.hours;
    });

    // Convert hours to days (assuming 8-hour workdays)
    const projectDays = {};
    Object.entries(projectHours).forEach(([project, hours]) => {
        projectDays[project] = hours / 8;
    });

    // Prepare labels and data
    const labels = Object.keys(projectDays);
    const data = Object.values(projectDays);

    // Create color array
    const colors = generateColors(labels.length, true);

    // Create the chart
    window.timeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Days',
                data: data,
                backgroundColor: colors,
                borderColor: colors.map(c => darkenColor(c, 20)),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 0 // Disable animations
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.raw.toFixed(1)} days`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Days'
                    }
                }
            }
        }
    });
}

/**
 * Generate a set of colors for the charts
 * @param {Number} count - Number of colors needed
 * @param {Boolean} alternate - Whether to use alternate color scheme
 * @returns {Array} Array of color strings
 */
function generateColors(count, alternate = false) {
    const primaryColors = [
        'rgba(74, 111, 199, 0.7)',
        'rgba(88, 199, 165, 0.7)',
        'rgba(243, 156, 18, 0.7)',
        'rgba(231, 76, 60, 0.7)',
        'rgba(52, 152, 219, 0.7)',
        'rgba(155, 89, 182, 0.7)',
        'rgba(46, 204, 113, 0.7)',
        'rgba(230, 126, 34, 0.7)',
        'rgba(52, 73, 94, 0.7)',
        'rgba(149, 165, 166, 0.7)'
    ];

    const secondaryColors = [
        'rgba(46, 204, 113, 0.7)',
        'rgba(52, 152, 219, 0.7)',
        'rgba(155, 89, 182, 0.7)',
        'rgba(231, 76, 60, 0.7)',
        'rgba(230, 126, 34, 0.7)',
        'rgba(243, 156, 18, 0.7)',
        'rgba(149, 165, 166, 0.7)',
        'rgba(52, 73, 94, 0.7)',
        'rgba(88, 199, 165, 0.7)',
        'rgba(74, 111, 199, 0.7)'
    ];

    const colors = alternate ? secondaryColors : primaryColors;

    // If we need more colors than available, repeat with different opacity
    if (count <= colors.length) {
        return colors.slice(0, count);
    } else {
        const result = [...colors];
        const iterations = Math.ceil(count / colors.length) - 1;

        for (let i = 0; i < iterations; i++) {
            const opacity = 0.7 - (i + 1) * 0.15;
            const additionalColors = colors.map(color => color.replace('0.7', opacity.toFixed(2)));
            result.push(...additionalColors);
        }

        return result.slice(0, count);
    }
}

/**
 * Darken a color by a specified amount
 * @param {String} color - CSS color string (rgba format)
 * @param {Number} amount - Amount to darken (0-100)
 * @returns {String} Darkened color string
 */
function darkenColor(color, amount) {
    // Extract the RGBA values
    const match = color.match(/rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)/);
    if (!match) return color;

    let r = parseInt(match[1]);
    let g = parseInt(match[2]);
    let b = parseInt(match[3]);
    const a = parseFloat(match[4]);

    // Darken the RGB values
    const darkenFactor = 1 - amount / 100;
    r = Math.max(0, Math.floor(r * darkenFactor));
    g = Math.max(0, Math.floor(g * darkenFactor));
    b = Math.max(0, Math.floor(b * darkenFactor));

    return `rgba(${r}, ${g}, ${b}, ${a})`;
}