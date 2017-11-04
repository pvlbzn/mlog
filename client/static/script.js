const data = {
    labels: ["12am-3am", "3am-6pm", "6am-9am", "9am-12am",
        "12pm-3pm", "3pm-6pm", "6pm-9pm", "9am-12am"
    ],
    datasets: [
        {
            title: "Some Data",
            color: "light-blue",
            values: [25, 40, 30, 35, 8, 52, 17, -4]
        },
        {
            title: "Another Set",
            color: "violet",
            values: [25, 50, -10, 15, 18, 32, 27, 14]
        }
]
}

const chart = new Chart({
    parent: '#chart',
    title: "My Awesome Chart",
    data: data,
    type: 'bar', // or 'line', 'scatter', 'pie', 'percentage'
    height: 250
})

console.log('hey??')