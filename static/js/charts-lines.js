/**
 * For usage, visit Chart.js docs https://www.chartjs.org/docs/latest/
 */

const chartLabels = typeof window.chartLabels !== 'undefined' ? window.chartLabels : ['Día 1', 'Día 2', 'Día 3', 'Día 4', 'Día 5', 'Día 6', 'Día 7'];
const chartVisitantes = typeof window.chartVisitantes !== 'undefined' ? window.chartVisitantes : [0, 0, 0, 0, 0, 0, 0];
const chartRespuestas = typeof window.chartRespuestas !== 'undefined' ? window.chartRespuestas : [0, 0, 0, 0, 0, 0, 0];

const lineConfig = {
  type: 'line',
  data: {
    labels: chartLabels,
    datasets: [
      {
        label: 'Visitantes',
        /**
         * These colors come from Tailwind CSS palette
         * https://tailwindcss.com/docs/customizing-colors/#default-color-palette
         */
        backgroundColor: '#0694a2',
        borderColor: '#0694a2',
        data: chartVisitantes,
        fill: false,
      },
      {
        label: 'Respuestas',
        fill: false,
        /**
         * These colors come from Tailwind CSS palette
         * https://tailwindcss.com/docs/customizing-colors/#default-color-palette
         */
        backgroundColor: '#7e3af2',
        borderColor: '#7e3af2',
        data: chartRespuestas,
      },
    ],
  },
  options: {
    responsive: true,
    /**
     * Default legends are ugly and impossible to style.
     * See examples in charts.html to add your own legends
     *  */
    legend: {
      display: false,
    },
    tooltips: {
      mode: 'index',
      intersect: false,
    },
    hover: {
      mode: 'nearest',
      intersect: true,
    },
    scales: {
      x: {
        display: true,
        scaleLabel: {
          display: true,
          labelString: 'Month',
        },
      },
      y: {
        display: true,
        scaleLabel: {
          display: true,
          labelString: 'Value',
        },
      },
    },
  },
}

// change this to the id of your chart element in HMTL
const lineCtx = document.getElementById('line')
window.myLine = new Chart(lineCtx, lineConfig)
