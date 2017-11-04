const defaultRange = 'week'

function requestData() {
    $.get('records' + '?range=' + defaultRange, function (data) {
        processData(data)
    })
}

function processData(res) {
    const data = {
        labels: [],
        datasets: [ {
            title: defaultRange,
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

        if (min < 5)
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


requestData()