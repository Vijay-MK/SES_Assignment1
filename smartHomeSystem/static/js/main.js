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
    function loadRealTimeChart() {
        fetch('/api/real_time')
            .then(response => response.json())
            .then(data => {
                const labels = data.map(d => d.applianceName);
                const values = data.map(d => d.powerConsumption);
    
                // Normalize bar colors: min is green, max is red
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
            })
            .catch(err => console.error("Chart Load Error:", err));
    }
    
    loadRealTimeChart();
    setInterval(loadRealTimeChart, 5000); // auto-refresh every 5 seconds

});
