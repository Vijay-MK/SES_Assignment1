document.addEventListener("DOMContentLoaded", function () {
    const tableBody = document.getElementById('latest-entries-body');
    const loader = document.getElementById('loading-spinner');
    const ctx = document.getElementById('realTimeChart').getContext('2d');

    const iconMap = {
        'Smart-AirConditioner': 'fa-wind',
        'Smart-WaterHeater': 'fa-hot-tub',
        'Smart-Refrigerator': 'fa-snowflake',
        'Smart-WashingMachine': 'fa-soap'
    };

 
    const latestLoader = document.getElementById('latest-loading');

    // Load latest table entries
    function loadLatestEntries() {
        if (loader) loader.style.display = 'inline-block';

        fetch('/api/latest')
            .then(response => response.json())
            .then(data => {
                tableBody.innerHTML = '';
		data.slice(0, 5).forEach(entry => {
		const iconClass = iconMap[entry.applianceName] || 'fa-plug';

		const row = document.createElement('tr');
		row.innerHTML = `
		    <td><i class="fas ${iconClass} icon-left"></i> ${entry.applianceName}</td>
		    <td>${entry.timeStamp}</td>
		    <td>${entry.powerConsumption}</td>
		`;
		    tableBody.appendChild(row);
		});


                if (loader) loader.style.display = 'none';
            })
            .catch(error => {
                console.error('Error fetching latest entries:', error);
                if (loader) loader.style.display = 'none';
            });
    }

    // Initial loads
    loadLatestEntries();

    // Refresh every 5 seconds
    setInterval(() => {
        loadLatestEntries();
    }, 5000);



    let chartInstance = null;
    const chartLoader = document.getElementById('chart-loading');
    function loadRealTimeChart() {
	if (chartLoader) chartLoader.style.display = 'inline-block';

        fetch('/api/real_time')
            .then(response => response.json())
            .then(data => {
                console.log("Chart Data:", data); // Keep this for debugging
                const labels = data.map(d => d.applianceName);
                const values = data.map(d => d.totalPowerConsumption); // FIXED here
    
                const max = Math.max(...values);
                const min = Math.min(...values);
                const barColors = values.map(v => {
                    if (v === max) return '#e74c3c'; // red
                    if (v === min) return '#2ecc71'; // green
                    return '#f1c40f';               // yellow
                });
    
                const ctx = document.getElementById('realTimeChart').getContext('2d');
    
                if (chartInstance) {
                    chartInstance.data.labels = labels;
                    chartInstance.data.datasets[0].data = values;
                    chartInstance.data.datasets[0].backgroundColor = barColors;
                    chartInstance.update();
                } else {
                    chartInstance = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: labels,
                            datasets: [{
                                label: 'Power (W)',
                                data: values,
                                backgroundColor: barColors,
                                borderRadius: 8,
                                barPercentage: 0.6,
                                categoryPercentage: 1.0
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: { display: false },
                                tooltip: { enabled: true }
                            },
                            scales: {
                                x: {
                                    title: { display: true, text: 'Appliance' }
                                },
                                y: {
                                    beginAtZero: true,
                                    title: { display: true, text: 'Watts' }
                                }
                            }
                        }
                    });
                }
            if (chartLoader) chartLoader.style.display = 'none';

            })
            .catch(err => console.error("Chart Load Error:", err));
    }
    
    loadRealTimeChart();
    setInterval(loadRealTimeChart, 5000);


});

function updatePeakUsage() {
    fetch('/api/peak')
        .then(response => response.json())
        .then(data => {
            document.getElementById('peakTime').textContent = formatDateTime(data.peakTime);
            document.getElementById('peakPower').textContent = formatPower(data.peakPower);
        })
        .catch(error => console.error('Error fetching peak usage:', error));
}

// Helper functions for formatting
function formatDateTime(timestamp) {
    return timestamp ? new Date(timestamp).toLocaleString() : 'N/A';
}

function formatPower(power) {
    return power ? `${power.toFixed(2)} W` : 'N/A';
}

// Add this to your initialization code
document.addEventListener('DOMContentLoaded', function() {
    updatePeakUsage();
    // Update every 5 minutes
    setInterval(updatePeakUsage, 300000);
});

let averageTrendChart = null;

function updateAverageTrendChart() {
    const loadingIcon = document.getElementById('average-trend-loading');
    loadingIcon.style.display = 'inline-block';

    fetch('/api/average_trend')
        .then(response => response.json())
        .then(data => {
            const labels = data.map(item => item.timestamp);
            const values = data.map(item => item.averagePower);

            const ctx = document.getElementById('averageTrendChart').getContext('2d');
            
            if (averageTrendChart) {
                averageTrendChart.destroy();
            }

            averageTrendChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Average Power Consumption (W)',
                        data: values,
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: '24-Hour Average Power Consumption'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Power (Watts)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Time'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error fetching average trend data:', error))
        .finally(() => {
            loadingIcon.style.display = 'none';
        });
}

// Add to your initialization code
document.addEventListener('DOMContentLoaded', function() {
    // ...existing initialization code...
    updateAverageTrendChart();
    // Update every 5 minutes
    setInterval(updateAverageTrendChart, 10000);
});
