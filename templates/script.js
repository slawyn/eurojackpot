        const x1_values   = {{ x1_values | safe }};
		const y1_values1 = {{ y1_values1 | safe }};
		const y1_values2 = {{ y1_values2 | safe }};
		const y1_values3 = {{ y1_values3 | safe }};
		const y1_values4 = {{ y1_values4 | safe }};
		const y1_values5 = {{ y1_values5 | safe }};
		const y1_accumulative1 = {{ y1_accumulative1 | safe }};
		const y1_accumulative2 = {{ y1_accumulative2 | safe }};
		
		const y2_values1 = {{y2_values1 |safe}};
		const y2_values2 = {{y2_values2 |safe}};
        
        const numbers_ratio = {{numbers_ratio|safe}};

        const matched = {{matched|safe}}
        let numbers_ratio_x =Object.keys(numbers_ratio);

        
        // Data for the bar chart with offsets
        var data_bar = {
            labels: ['1st', '2nd', '3rd', '4th', '5th'],
            datasets: [{
                label: 'Range',
                data:
                    [{{ range1 }}, {{ range2 }}, {{ range3 }}, {{ range4 }}, {{ range5 }}],
			backgroundColor: 'rgba(255, 99, 132, 0.7)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
        }]
        };

        var options_bar = {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: [{
                    ticks: {
                        beginAtZero: true
                    }
                }],
                y: [{
                    ticks: {
                        beginAtZero: true
                    }
				
                }]
            }
        };

        var options = {
            scales: {
                x: {
                    max: 100,
                    ticks: {
                        stepSize: 1
                    },
		
                },
                y: {
					position: 'left'
                }
            },
            plugins: {

                zoom: {

                    pan: {
                        enabled: true,
                        mode: 'x',

                    },
                    zoom: {
                        mode: 'x',
                        wheel: {
                            enabled: true,
                            modifierKey: 'ctrl',
                        },
                    },
                }
            }
        };
		

		
        var data1 =
        {   
labels: x1_values,
			datasets: [
            {
                label: 'accumulative 1st',
                data: y1_accumulative1 ,
				borderColor: 'rgba(50, 50, 50, 0.3)',
				fill: true,
				borderWidth: 1,
				backgroundColor: 'rgba(50, 50, 50, 0.3)',
            },
            {
                label: 'accumulative 2nd',
                data: y1_accumulative2 ,
				borderColor: 'rgba(50, 50, 50, 0.3)',
				fill: true,
				borderWidth: 1,
				backgroundColor: 'rgba(50, 50, 50, 0.3)',
            },
            {
                label: '1st',
                data: y1_values1 ,
				borderColor: 'rgba(50, 50, 50)',
				fill: true,
				borderWidth: 1,
				backgroundColor: 'rgba(255, 99, 132)',
            },
            {
                label: '2nd',
                data: y1_values2 ,
				borderColor: 'rgba(50, 50, 50)',
				fill: true,
				borderWidth: 1,
				backgroundColor: 'rgba(54, 162, 235)',
            },
            {
                label: '3rd',
                data: y1_values3 ,
				borderColor: 'rgba(50, 50, 50)',
				fill: true,
				borderWidth: 1,
				backgroundColor: 'rgba(50, 150, 50)',
            },
            {
                label: '4th',
                data: y1_values4 ,
				borderColor: 'rgba(50, 50, 50)',
				fill: true,
				borderWidth: 1,
				backgroundColor: 'rgba(75, 192, 192)',
            },
            {
                label: '5th',
                data: y1_values5 ,
				borderColor: 'rgba(50, 50, 50)',
				fill: true,
				borderWidth: 1,
				backgroundColor: 'rgba(153, 102, 255)',
            }
        ]
            };


        var data2 =
        {
            labels: x1_values,
			datasets: [
            {
                label: '1. Euro',
                data: y2_values1 ,
				borderColor: 'rgba(255, 99, 132)',
				fill: true,
				borderWidth: 1
            },
            {
                label: '2. Euro',
                data: y2_values2 ,
				borderColor: 'rgba(54, 162, 235)',
				fill: true,
				borderWidth: 1,
				backgroundColor: 'rgba(255, 99, 132, 0.2)'
            },

        ]
            };
        var ctx1 = document.getElementById('idChartFiveNumbers').getContext('2d');
        var myChart = new Chart(ctx1, {
            type: 'line',
            data: data1,
            options: options
        });

        var ct2x = document.getElementById('idChartTwoNumbers').getContext('2d');
        var idChartTwoNumbers = new Chart(ct2x, {
            type: 'line',
            data: data2,
            options: options
        });

        var ctx = document.getElementById('idBarChart').getContext('2d');
        var idBarChart = new Chart(ctx, {
            type: 'bar',
            data: data_bar,
            options: options_bar
        });


    var data = {
      labels: numbers_ratio_x,
      datasets: [{
        data: numbers_ratio_x.map((x) => (numbers_ratio[x])),
        backgroundColor: getRandomColors(numbers_ratio_x.length),
      }]
    };

    // Create the pie chart
    var ctx = document.getElementById('idPieChart').getContext('2d');
    var idPieChart = new Chart(ctx, {
      type: 'pie',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                var label = context.label || '';
                var value = context.formattedValue;
                return label + ': ' + value + '%';
              }
            }
          }
        }
      }
    });

        function getRandomColors(count) {
            var colors = [];
            for (var i = 0; i < count; i++) {
              colors.push(`rgba(${Math.floor(Math.random() * 256)}, ${Math.floor(Math.random() * 256)}, ${Math.floor(Math.random() * 256)}, 0.7)`);
            }
            return colors;
         }

    //
    var table = document.getElementById('idMatched')
    
    for(let timestamp in matched)
    {
        // 
        let row = document.createElement("tr")
        
        // timestamp
        let td = document.createElement("td")
        td.innerHTML = timestamp;
        row.appendChild(td)
        
        let lotto_numbers = matched[timestamp][0];
        let tipped_correctly = matched[timestamp][1];
        for (let number of lotto_numbers) {
            let td = document.createElement("td")
            td.innerHTML = number

            if(tipped_correctly.includes(number))
            {
                td.className = "green-bg"
            }
            else
            {
                td.className = "beige-bg"
            }
            row.appendChild(td)
        }
        table.appendChild(row)
    }
