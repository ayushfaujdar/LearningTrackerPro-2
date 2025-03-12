
// Chart configuration and setup
let costChart, timeChart, skillChart;
let charts = {};

// Initialize the charts
function initializeCharts() {
    const costChartCtx = document.getElementById('cost-chart')?.getContext('2d');
    const timeChartCtx = document.getElementById('time-chart')?.getContext('2d');
    
    // Check if elements exist before initializing
    if (!costChartCtx || !timeChartCtx) {
        console.warn("Chart elements not found in the DOM yet. Charts will be initialized when needed.");
        return;
    }

    // Common chart settings for reduced size and horizontal flow
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 1000
        },
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                enabled: true
            }
        },
        layout: {
            padding: {
                left: 5,
                right: 5,
                top: 10,
                bottom: 10
            }
        }
    };

    // Cost Chart
    costChart = new Chart(costChartCtx, {
        type: 'bar',
        data: {
            labels: ['Budget', 'Current Cost'],
            datasets: [{
                label: 'Cost',
                data: [10000, 0],
                backgroundColor: [
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 99, 132, 0.5)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Cost ($)',
                        font: {
                            size: 10
                        }
                    },
                    ticks: {
                        font: {
                            size: 9
                        }
                    }
                },
                x: {
                    ticks: {
                        font: {
                            size: 9
                        }
                    }
                }
            }
        }
    });

    // Time Chart
    timeChart = new Chart(timeChartCtx, {
        type: 'bar',
        data: {
            labels: ['Deadline', 'Current Time'],
            datasets: [{
                label: 'Time',
                data: [30, 0],
                backgroundColor: [
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 99, 132, 0.5)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Days',
                        font: {
                            size: 10
                        }
                    },
                    ticks: {
                        font: {
                            size: 9
                        }
                    }
                },
                x: {
                    ticks: {
                        font: {
                            size: 9
                        }
                    }
                }
            }
        }
    });

    // Store charts in an object for easy access
    charts = { costChart, timeChart };
}

// Update charts with new data
function updateCharts(result) {
    // Make sure the chart elements exist
    const costChartEl = document.getElementById('cost-chart');
    const timeChartEl = document.getElementById('time-chart');

    if (!costChartEl || !timeChartEl) {
        console.warn("Chart elements not found. Skipping chart update.");
        
        // Update benefit metrics even if charts aren't available
        const budget = parseFloat(document.getElementById('budget')?.value) || 10000;
        const deadline = parseFloat(document.getElementById('deadline')?.value) || 30;
        const totalCost = result.total_cost || 0;
        const completionTime = result.completion_time || 0;
        
        let avgSkillMatch = 0;
        if (result.assignments && result.assignments.length > 0) {
            avgSkillMatch = result.assignments.reduce((sum, a) => sum + a.skill_match, 0) / result.assignments.length;
        }
        
        // Update benefit metrics
        const costSavingsPercentage = (budget > 0) ? Math.round((1 - totalCost / budget) * 100) : 0;
        const timeEfficiencyPercentage = (deadline > 0) ? Math.round((1 - completionTime / deadline) * 100) : 0;
        const skillUtilizationPercentage = Math.round(avgSkillMatch);

        document.getElementById('cost-savings').textContent = costSavingsPercentage + '%';
        document.getElementById('time-efficiency').textContent = timeEfficiencyPercentage + '%';
        document.getElementById('skill-match').textContent = skillUtilizationPercentage + '%';
        
        return;
    }

    // Initialize charts if they don't exist yet
    if (!costChart || !timeChart) {
        initializeCharts();
        
        // If charts still couldn't be initialized, exit
        if (!costChart || !timeChart) {
            console.warn("Charts couldn't be initialized. Skipping chart update.");
            return;
        }
    }

    // Update cost chart
    const budget = parseFloat(document.getElementById('budget').value) || 10000;
    const totalCost = result.total_cost || 0;

    costChart.data.datasets[0].data = [budget, totalCost];
    costChart.update();

    // Update time chart
    const deadline = parseFloat(document.getElementById('deadline').value) || 30;
    const completionTime = result.completion_time || 0;

    timeChart.data.datasets[0].data = [deadline, completionTime];
    timeChart.update();

    // Calculate skill match
    let avgSkillMatch = 0;
    if (result.assignments && result.assignments.length > 0) {
        avgSkillMatch = result.assignments.reduce((sum, a) => sum + a.skill_match, 0) / result.assignments.length;
    }

    // Update benefit metrics
    const costSavingsPercentage = (budget > 0) ? Math.round((1 - totalCost / budget) * 100) : 0;
    const timeEfficiencyPercentage = (deadline > 0) ? Math.round((1 - completionTime / deadline) * 100) : 0;
    const skillUtilizationPercentage = Math.round(avgSkillMatch);

    document.getElementById('cost-savings').textContent = costSavingsPercentage + '%';
    document.getElementById('time-efficiency').textContent = timeEfficiencyPercentage + '%';
    document.getElementById('skill-match').textContent = skillUtilizationPercentage + '%';
}

// Update chart when window is resized
window.addEventListener('resize', function() {
    if (costChart) costChart.resize();
    if (timeChart) timeChart.resize();
});

// Ensure charts are initialized when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Wait for the results section to be displayed before initializing charts
    const resultsSection = document.getElementById('results-section');
    if (resultsSection && window.getComputedStyle(resultsSection).display !== 'none') {
        initializeCharts();
    }
});
