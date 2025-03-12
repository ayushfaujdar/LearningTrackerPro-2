/**
 * Quantum Workflow Visualization for AQWSE
 * Shows a visual representation of the quantum optimization process
 */

// Initialize the quantum visualization
function initQuantumVisualization() {
    // Create the canvas for visualization if it doesn't exist
    if (!document.getElementById('quantum-canvas')) {
        const container = document.getElementById('quantum-visualization');
        if (container) {
            const canvas = document.createElement('canvas');
            canvas.id = 'quantum-canvas';
            canvas.width = container.offsetWidth;
            canvas.height = 200; // Reduced height
            container.appendChild(canvas);
            
            // Add description
            const description = document.createElement('div');
            description.className = 'quantum-description';
            description.innerHTML = `
                <h4>Quantum-Inspired Optimization Process</h4>
                <p>This visualization demonstrates how we use quantum computing principles to explore the optimization space 
                and find the optimal resource allocation.</p>
            `;
            container.appendChild(description);
        }
    }
}

// Animate the quantum optimization process based on result data
function animateQuantumProcess(result) {
    const canvas = document.getElementById('quantum-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Get quantum status
    const isQuantumPowered = result.quantum_powered || false;
    
    // Draw background grid
    drawQuantumGrid(ctx, width, height);
    
    // Draw optimization progress
    drawOptimizationPath(ctx, width, height, result, isQuantumPowered);
    
    // Show quantum state if using quantum computing
    if (isQuantumPowered) {
        drawQuantumStates(ctx, width, height, result);
    }
    
    // Draw the optimal solution highlight
    drawOptimalSolution(ctx, width, height, result);
    
    // Update the description based on whether quantum was used
    updateQuantumDescription(result);
}

// Draw the quantum grid background
function drawQuantumGrid(ctx, width, height) {
    ctx.strokeStyle = 'rgba(100, 100, 255, 0.2)';
    ctx.lineWidth = 1;
    
    // Draw vertical grid lines
    for (let x = 0; x <= width; x += 20) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
    }
    
    // Draw horizontal grid lines
    for (let y = 0; y <= height; y += 20) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
    }
}

// Draw the optimization path
function drawOptimizationPath(ctx, width, height, result, isQuantumPowered) {
    const assignments = result.assignments || [];
    const totalAssignments = assignments.length;
    
    if (totalAssignments === 0) return;
    
    // Create animation points based on the assignments
    const points = [];
    const margin = 40;
    const usableWidth = width - (2 * margin);
    const usableHeight = height - (2 * margin);
    
    // Generate some points for the optimization path
    const pathPoints = 50; // Number of points in the path
    for (let i = 0; i < pathPoints; i++) {
        const progress = i / (pathPoints - 1);
        
        // For quantum, create interference pattern
        if (isQuantumPowered) {
            const amplitude = 30 * Math.sin(progress * Math.PI * 6);
            const x = margin + (progress * usableWidth);
            const y = (height / 2) + amplitude * Math.sin(progress * Math.PI * 4);
            points.push({ x, y, alpha: 0.5 + (progress * 0.5) });
        } else {
            // For classical, create a more direct path with some noise
            const noise = 20 * (Math.random() - 0.5);
            const x = margin + (progress * usableWidth);
            const y = (height / 2) - (progress * (usableHeight / 3)) + noise;
            points.push({ x, y, alpha: 0.3 + (progress * 0.7) });
        }
    }
    
    // Draw the path
    ctx.lineWidth = 2;
    ctx.strokeStyle = isQuantumPowered ? 'rgba(75, 0, 130, 0.7)' : 'rgba(0, 128, 255, 0.7)';
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    
    for (let i = 1; i < points.length; i++) {
        // Use bezier curves for smoother path
        const cp1x = points[i-1].x + (points[i].x - points[i-1].x) / 3;
        const cp1y = points[i-1].y;
        const cp2x = points[i].x - (points[i].x - points[i-1].x) / 3;
        const cp2y = points[i].y;
        ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, points[i].x, points[i].y);
    }
    
    ctx.stroke();
    
    // Draw points along the path
    for (let i = 0; i < points.length; i += 5) {
        const point = points[i];
        ctx.fillStyle = isQuantumPowered ? 
            `rgba(75, 0, 130, ${point.alpha})` : 
            `rgba(0, 128, 255, ${point.alpha})`;
        ctx.beginPath();
        ctx.arc(point.x, point.y, 3, 0, Math.PI * 2);
        ctx.fill();
    }
}

// Draw quantum states (for quantum-powered optimization)
function drawQuantumStates(ctx, width, height, result) {
    const margin = 40;
    const usableWidth = width - (2 * margin);
    const centerY = height / 2;
    
    // Draw quantum waves
    ctx.strokeStyle = 'rgba(128, 0, 128, 0.3)';
    ctx.lineWidth = 1;
    
    for (let wave = 0; wave < 5; wave++) {
        const amplitude = 10 + (wave * 5);
        const frequency = 0.1 - (wave * 0.015);
        
        ctx.beginPath();
        for (let x = 0; x <= usableWidth; x++) {
            const xPos = margin + x;
            const yPos = centerY + (amplitude * Math.sin(x * frequency * Math.PI));
            
            if (x === 0) {
                ctx.moveTo(xPos, yPos);
            } else {
                ctx.lineTo(xPos, yPos);
            }
        }
        ctx.stroke();
    }
    
    // Draw quantum particles
    const particleCount = 10;
    ctx.fillStyle = 'rgba(148, 0, 211, 0.7)';
    
    for (let i = 0; i < particleCount; i++) {
        const x = margin + (Math.random() * usableWidth);
        const y = centerY + (40 * Math.sin(x / width * Math.PI * 2)) * Math.random();
        const size = 2 + (Math.random() * 3);
        
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fill();
    }
}

// Draw the optimal solution point
function drawOptimalSolution(ctx, width, height, result) {
    const margin = 40;
    const optimalX = width - margin;
    const optimalY = height / 3;
    
    // Draw a pulsating circle around the optimal solution
    const glowSize = 15;
    const gradient = ctx.createRadialGradient(
        optimalX, optimalY, 0,
        optimalX, optimalY, glowSize
    );
    gradient.addColorStop(0, 'rgba(255, 215, 0, 0.8)');
    gradient.addColorStop(1, 'rgba(255, 215, 0, 0)');
    
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(optimalX, optimalY, glowSize, 0, Math.PI * 2);
    ctx.fill();
    
    // Draw the optimal point
    ctx.fillStyle = '#FFD700';
    ctx.beginPath();
    ctx.arc(optimalX, optimalY, 6, 0, Math.PI * 2);
    ctx.fill();
    
    // Add a label
    ctx.fillStyle = '#333';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Optimal Solution', optimalX, optimalY - 15);
    
    // Draw lines to the metrics
    drawMetricLines(ctx, optimalX, optimalY, width, height, result);
}

// Draw lines connecting the optimal solution to key metrics
function drawMetricLines(ctx, x, y, width, height, result) {
    const metrics = [
        { label: `Budget Efficiency: ${result.metrics?.budget_efficiency || 0}%`, y: y + 40 },
        { label: `Time Efficiency: ${result.metrics?.time_efficiency || 0}%`, y: y + 60 },
        { label: `Skill Match: ${result.metrics?.avg_skill_match || 0}%`, y: y + 80 }
    ];
    
    ctx.strokeStyle = 'rgba(255, 215, 0, 0.5)';
    ctx.fillStyle = '#333';
    ctx.font = '11px Arial';
    ctx.textAlign = 'right';
    
    metrics.forEach(metric => {
        // Draw connecting line
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x - 30, metric.y);
        ctx.lineTo(x - 150, metric.y);
        ctx.stroke();
        
        // Add label
        ctx.fillText(metric.label, x - 35, metric.y + 4);
    });
}

// Update the quantum description based on the result
function updateQuantumDescription(result) {
    const description = document.querySelector('.quantum-description');
    if (!description) return;
    
    const isQuantumPowered = result.quantum_powered || false;
    const aiPowered = result.ai_powered || false;
    
    let html = `<h4>${isQuantumPowered ? 'Quantum-Powered' : 'Quantum-Inspired'} Optimization</h4>`;
    
    if (isQuantumPowered) {
        html += `
            <p>This optimization was performed using real quantum computing techniques via IBM Qiskit. 
            The quantum algorithm explored multiple solution paths simultaneously to find the optimal 
            resource allocation.</p>
        `;
    } else {
        html += `
            <p>This optimization used quantum-inspired classical algorithms to find efficient resource 
            allocation. For even better results, consider providing an IBM Quantum token.</p>
        `;
    }
    
    if (aiPowered) {
        html += `<p>The insights were enhanced with AI-powered analysis for deeper understanding.</p>`;
    }
    
    description.innerHTML = html;
}