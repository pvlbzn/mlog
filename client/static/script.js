// Public pointers to charts
let primaryChart = undefined
let secondaryChart = undefined


/**
 * Request data from the server.
 * 
 * @param {string} timePeriod could be one of 'today', 'yesterday', 'week', 'month'
 * @param {int} threshold data below threshold is ignored and not rendered, in minutes
 */
function requestData(timePeriod, threshold) {
    showMessage()
    $.get('records/' + timePeriod, (data) => {
        processData(data, threshold, timePeriod)
    }).done(() => { removeMessage() })
}

function showMessage() {
    $('#message-box').removeClass('hidden')
}

function removeMessage() {
    // $('#message-box').addClass('hidden')
    $('#message-box').transition({
        animation: 'scale',
        duration: '300',
        onComplete: function() {
            $(this).addClass('hidden')
        }
    })
}


function processData(res, threshold, timePeriod) {
    const data = {
        labels: [],
        datasets: [ {
            title: 'Minutes',
            color: 'light-blue',
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

    renderChart(data, timePeriod)
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


function renderChart(data, timePeriod) {
    primaryChart = new Chart({
        parent: '#chart',
        data: data,
        type: 'bar',
        height: 250,
        is_navigable: 1,
        is_series: 1
    })

    primaryChart.parent.addEventListener('data-select', (event) => {
        $.get('records/' + timePeriod + '?name=' + event.label, (data) => {
            createSecondaryChart(timePeriod, event.label, data)
        })
    })
}


function createSecondaryChart(timePeriod, label, data) {
    let jdata = JSON.parse(data)
    let app = jdata.frames[0]
    let windows = app.windows

    let detalizationData = {
        labels: [],
        datasets: [ {
            title: 'Minutes',
            color: 'light-green',
            values: []
        }]
    }

    windows = convertWindows(windows, 1)
    windows = sortWindows(windows)

    for (let i = 0; i < windows.length; i++) {
        let labelName = windows[i].name
        if (labelName == undefined) {
            labelName = 'Unnamed'
        }

        detalizationData.labels.push(labelName)
        detalizationData.datasets[0].values.push(windows[i].time)
    }

    secondaryChart = new Chart({
        parent: '#secondary-chart',
        data: detalizationData,
        type: 'bar',
        height: 250,
        is_series: 1
    })
}


function sortWindows(windows) {
    return windows.sort((x, y) => { return y.time - x.time})
}


/**
 * Convert windows values to minutes. Values below threshold are ignored.
 * 
 * @param {*} windows 
 * @param {*} threshold 
 */
function convertWindows(windows, threshold) {
    for (let i = 0; i < windows.length; i++) {
        let min = Math.floor(windows[i].time / 60)

        if (min < threshold)
            continue

        windows[i].time = min
    }

    return windows
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
    requestData('week', 10)
})


buttons.lastMonth.click(function () {
    $('.ui .item').removeClass('active');
    $(this).addClass('active');
    requestData('month', 30)
})


$(document).ready(() => {
    buttons.today.click()
})
