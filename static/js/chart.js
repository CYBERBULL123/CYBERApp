// Register the datalabels plugin
Chart.register(ChartDataLabels);

document.addEventListener('DOMContentLoaded', () => {
    // Function to generate random data
    function getRandomData(length, min, max) {
        return Array.from({ length }, () => Math.floor(Math.random() * (max - min + 1)) + min);
    }

    // Vulnerability Chart (Bar)
    const vulnerabilityCtx = document.getElementById('vulnerabilityChart').getContext('2d');
    const vulnerabilityChart = new Chart(vulnerabilityCtx, {
        type: 'bar',
        data: {
            labels: ['Critical', 'High', 'Medium', 'Low'],
            datasets: [{
                label: 'Vulnerability Severity',
                data: getRandomData(4, 5, 25),
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                    'rgba(255, 206, 86, 0.8)'
                ],
                borderColor: '#fff',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#fff',
                    borderWidth: 1
                },
                datalabels: {
                    anchor: 'end',
                    align: 'top',
                    color: '#fff',
                    font: { weight: 'bold', size: 12 },
                    formatter: (value) => value
                }
            },
            scales: {
                y: { beginAtZero: true, grid: { color: '#444' } },
                x: { grid: { color: '#444' } }
            },
            animation: { duration: 1500, easing: 'easeInOutQuad' }
        }
    });

    // Threat Distribution Chart (Pie)
    const threatCtx = document.getElementById('threatChart').getContext('2d');
    const threatChart = new Chart(threatCtx, {
        type: 'pie',
        data: {
            labels: ['Phishing', 'Ransomware', 'Malware', 'DDoS'],
            datasets: [{
                label: 'Threat Distribution',
                data: getRandomData(4, 10, 50),
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                    'rgba(255, 206, 86, 0.8)'
                ],
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#fff',
                    borderWidth: 1
                },
                datalabels: {
                    color: '#fff',
                    font: { weight: 'bold', size: 12 },
                    formatter: (value) => value
                }
            },
            animation: { duration: 1500, easing: 'easeInOutQuad' }
        }
    });

    // Incident Trends Chart (Line)
    const incidentTrendsCtx = document.getElementById('incidentTrendsChart').getContext('2d');
    const incidentTrendsChart = new Chart(incidentTrendsCtx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Incident Trends',
                data: getRandomData(6, 5, 30),
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#fff',
                    borderWidth: 1
                },
                datalabels: {
                    color: '#fff',
                    font: { weight: 'bold', size: 12 },
                    formatter: (value) => value
                }
            },
            scales: {
                y: { beginAtZero: true, grid: { color: '#444' } },
                x: { grid: { color: '#444' } }
            },
            animation: { duration: 1500, easing: 'easeInOutQuad' }
        }
    });

    // Risk Levels Chart (Doughnut)
    const riskLevelsCtx = document.getElementById('riskLevelsChart').getContext('2d');
    const riskLevelsChart = new Chart(riskLevelsCtx, {
        type: 'doughnut',
        data: {
            labels: ['High', 'Medium', 'Low'],
            datasets: [{
                label: 'Risk Levels',
                data: getRandomData(3, 10, 60),
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 206, 86, 0.8)'
                ],
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#fff',
                    borderWidth: 1
                },
                datalabels: {
                    color: '#fff',
                    font: { weight: 'bold', size: 12 },
                    formatter: (value) => value
                }
            },
            animation: { duration: 1500, easing: 'easeInOutQuad' }
        }
    });

    // Attack Types Radar Chart
    const attackTypesRadarCtx = document.getElementById('attackTypesRadarChart').getContext('2d');
    const attackTypesRadarChart = new Chart(attackTypesRadarCtx, {
        type: 'radar',
        data: {
            labels: ['Phishing', 'Ransomware', 'Malware', 'DDoS', 'Brute Force'],
            datasets: [{
                label: 'Attack Types',
                data: getRandomData(5, 10, 50),
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#fff',
                    borderWidth: 1
                },
                datalabels: {
                    color: '#fff',
                    font: { weight: 'bold', size: 12 },
                    formatter: (value) => value
                }
            },
            animation: { duration: 1500, easing: 'easeInOutQuad' }
        }
    });

    // Security Events Polar Area Chart
    const securityEventsPolarCtx = document.getElementById('securityEventsPolarChart').getContext('2d');
    const securityEventsPolarChart = new Chart(securityEventsPolarCtx, {
        type: 'polarArea',
        data: {
            labels: ['Login Attempts', 'Firewall Alerts', 'Malware Detections', 'Data Breaches'],
            datasets: [{
                label: 'Security Events',
                data: getRandomData(4, 10, 50),
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                    'rgba(255, 206, 86, 0.8)'
                ],
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#fff',
                    borderWidth: 1
                },
                datalabels: {
                    color: '#fff',
                    font: { weight: 'bold', size: 12 },
                    formatter: (value) => value
                }
            },
            animation: { duration: 1500, easing: 'easeInOutQuad' }
        }
    });
});