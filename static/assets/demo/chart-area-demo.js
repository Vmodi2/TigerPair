// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';

// Area Chart Example
function handleResponse(response) {
    let days = response.split(';');
    numbers = [];
    for (let i = 0; i < 5 - days.length + 1; i++) {
	numbers.push(0);
    }
    let max = 0;
    for (let i = 0; i < days.length - 1; i++) {
	let num = (parseInt(days[i].split(',')[1].trim().split('(')[0]));
	numbers.push(num);
	if (num > max) {
	    max = num;
	}
  }
  let ctx = document.getElementById("myAreaChart");
  let today = new Date();
  let myLineChart = new Chart(ctx, {
    type: 'line',
    data: {
	labels: ['4 days ago', '3 days ago', '2 days ago', 'yesterday', 'today'],
      datasets: [{
        label: "Registrations",
        lineTension: 0.3,
        backgroundColor: "rgba(2,117,216,0.2)",
        borderColor: "rgba(2,117,216,1)",
        pointRadius: 5,
        pointBackgroundColor: "rgba(2,117,216,1)",
        pointBorderColor: "rgba(255,255,255,0.8)",
        pointHoverRadius: 5,
        pointHoverBackgroundColor: "rgba(2,117,216,1)",
        pointHitRadius: 50,
        pointBorderWidth: 2,
          data: numbers,
      }],
    },
    options: {
      scales: {
        xAxes: [{
          time: {
            unit: 'date'
          },
          gridLines: {
            display: false
          },
          ticks: {
            maxTicksLimit: 7
          }
        }],
        yAxes: [{
          ticks: {
            min: 0,
            max: max,
            maxTicksLimit: 5
          },
          gridLines: {
            color: "rgba(0, 0, 0, .125)",
          }
        }],
      },
      legend: {
        display: false
      }
    }
  });
}

let request = null;

function getRegistrations() {
  let today = new Date();
  let date = today.getFullYear() + '-' + (today.getMonth() + 1) + '-' + today.getDate();
  let url = '/admin/get-registrations';
  if (request != null)
    request.abort();
  request = $.ajax(
    {
      type: "GET",
      url: url,
      success: handleResponse
    }
  );
}

$('document').ready(getRegistrations);
