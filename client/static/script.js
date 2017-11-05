const defaultRange = 'week'

/**
 * Request data from the server.
 * 
 * @param {string} timePeriod could be one of 'today', 'yesterday', 'week', 'month'
 * @param {int} threshold data below threshold is ignored and not rendered, in minutes
 */
function requestData(timePeriod, threshold) {
    $.get('records/' + timePeriod, (data) => {
        processData(data, threshold)
    })
}


function processData(res, threshold) {
    const data = {
        labels: [],
        datasets: [ {
            title: defaultRange,
            color: 'light-gray',
            values: []
        }]
    }

    let jres = JSON.parse(res)

    const labels = []
    const values = []

    const frames = {}

    for (let i = 0; i < jres.frames.length; i++) {
        let min = Math.floor(jres.frames[i].time / 60)

        if (min < threshold)
            continue

        frames[jres.frames[i].name] = min
    }

    const sorted = sortFrames(frames)
    
    data.labels = Object.keys(sorted)
    data.datasets[0].values = Object.values(sorted)

    renderChart(data)
}


function sortFrames(frames) {
    let keys = Object.keys(frames)
    keys.sort((x, y) => { return frames[y] - frames[x]})
    
    let res = {}
    for (let i = 0; i < keys.length; i++) {
        res[keys[i]] = frames[keys[i]]
    }

    return res
}


function renderChart(data) {
    let chart = new Chart({
        parent: '#chart',
        title: 'Usage Statistics',
        data: data,
        type: 'bar',
        height: 250
    })
}


const buttons = {
    today: $('#today-btn'),
    yesterday: $('#yesterday-btn'),
    lastWeek: $('#last-week-btn'),
    lastMonth: $('#last-month-btn')
}


buttons.today.click(function () {
    $('.ui .item').removeClass('active');
    $(this).addClass('active');
    requestData('today', 1)
})


buttons.yesterday.click(function () {
    $('.ui .item').removeClass('active');
    $(this).addClass('active');
    requestData('yesterday', 1)
})


buttons.lastWeek.click(function () {
    $('.ui .item').removeClass('active');
    $(this).addClass('active');
    requestData('week', 1)
})


buttons.lastMonth.click(function () {
    $('.ui .item').removeClass('active');
    $(this).addClass('active');
    requestData('month', 1)
})

$(document).ready(() => {
    buttons.today.click()
})