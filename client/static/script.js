class BarChart {
    constructor(parent) {
        this.chart          = undefined
        this.data           = undefined

        this.labels         = []
        this.values         = []

        this.parent         = parent
        this.type           = 'bar'
        this.height         = 250
        this.is_navigable   = 1
        this.is_series      = 1

        this.createDataLayout()
    }

    assignLabels(labels) {
        if (this.data == undefined)
            throw 'data is undefined, failed to add labels'
        
        this.data.labels = labels

        return this
    }

    addLabels(labels) {
        if (this.data == undefined)
            throw 'data is undefined, failed to add labels'
        
        this.data.labels = this.data.labels.concat(labels)

        return this
    }

    assignValues(values, datasetIndex) {
        if (this.data == undefined)
            throw 'data is undefined, failed to add values'
        
        if (datasetIndex > this.data.datasets.length)
            throw 'index out of datasets bound'

        this.data.datasets[datasetIndex].values = values

        return this
    }

    addValues(values, datasetIndex) {
        if (this.data == undefined)
            throw 'data is undefined, failed to add values'
    
        if (datasetIndex > this.data.datasets.length)
            throw 'index out of datasets bound'
        
        this.data.datasets[datasetIndex].values = this.data.datasets[datasetIndex].values.concat(values)

        return this
    }

    createDataLayout() {
        this.data = {
            labels: this.labels,
            datasets: [{
                title: 'Minutes',
                color: 'light-blue',
                values: this.values
            }]
        }

        return this
    }

    create() {
        if (this.data == undefined || this.parent == undefined)
            // throw exception or whatever
            throw 'data is undefined, failed to create a chart'
        this.chart = new Chart({
            parent:         this.parent,
            data:           this.data,
            type:           this.type,
            height:         this.height,
            is_navigable:   this.is_navigable,
            is_series:      this.is_series
        })

        return this
    }

    update() {
        this.chart.update_values()

        return this
    }

    refresh() {
        this.chart.refresh()

        return this
    }

    deleteData() {
        this.data.labels = []
        this.data.datasets.forEach(dataset => dataset.values = [])

        return this
    }

    addEventListener(event, fn) {
        this.chart.parent.addEventListener(event, fn)
    }
}

function makeChart(parent, labels, values) {
    $(parent).replaceWith($(parent).clone());
    return new BarChart(parent)
            .assignLabels(labels)
            .assignValues(values, 0)
            .create()
}

function updateChart(c, labels, values) {
    return c.deleteData()
            .assignLabels(labels)
            .assignValues(values)
            .create()
}

function assignButtonCallbacks(buttons) {
    buttons.today.click(function () {
        $('.ui .item').removeClass('active');
        $(this).addClass('active');
        buttonCallback('today')
    })

    buttons.yesterday.click(function () {
        $('.ui .item').removeClass('active');
        $(this).addClass('active');
        buttonCallback('yesterday')
    })

    buttons.lastWeek.click(function () {
        $('.ui .item').removeClass('active');
        $(this).addClass('active');
        buttonCallback('week')
    })

    buttons.lastMonth.click(function () {
        $('.ui .item').removeClass('active');
        $(this).addClass('active');
        buttonCallback('month')
    })

    return buttons
}

/**
 * Button callback requests relevant data from API and calls consequent
 * routines to display a primary chart.
 * 
 * @param {*} range 
 */
function buttonCallback(range) {
    showLoadingMessage()
    requestPrimaryData(range)
}

function requestPrimaryData(range) {
    const endpoint = 'records/'
    const query = endpoint + range
    
    $.get(query, (data) => {
        // Wait until data is ready
    }).done((data) => {
        removeLoadingMessage()
        createPrimaryChart(data, range)
    })
}

function requestSecondaryData(range, label) {
    const endpoint = 'records/'
    const query = endpoint + range + '?name=' + label

    $.get(query, (data) => {
        // Wait until data is ready
    }).done((data) => {
        removeLoadingMessage()
        createSecondaryChart(data, range)
    })
}

function showLoadingMessage() {
    $('#message-box').removeClass('hidden')
}

function removeLoadingMessage() {
    $('#message-box').transition({
        animation: 'scale',
        duration: '300',
        onComplete: function() {
            $(this).addClass('hidden')
        }
    })
}

function createPrimaryChart(data, range) {
    const json = JSON.parse(data)
    const frames = json.frames
    const threshold = 5

    const labels = []
    const values = []

    frames.forEach((item) => {
        const val = Math.floor(item.time / 60)

        if (val > threshold) {
            labels.push(item.name)
            values.push(val)
        }
    })

    const primaryChart = makeChart('#primary-chart', labels, values)

    primaryChart.addEventListener('data-select', (event) => {
        showLoadingMessage()
        requestSecondaryData(range, event.label)
    })
}

function createSecondaryChart(data, range) {
    const json = JSON.parse(data)
    const windows = json.frames[0].windows
    const threshold = 5

    const labels = []
    const values = []

    const swindows = windows.sort((x, y) => { return y.time - x.time})

    swindows.forEach((item) => {
        const val = Math.floor(item.time / 60)

        if (val > threshold) {
            labels.push(item.name)
            values.push(val)
        }
    })
    
    const secondaryChart = makeChart('#secondary-chart', labels, values)
}

$(document).ready(() => {
    const buttons = {
        today: $('#today-btn'),
        yesterday: $('#yesterday-btn'),
        lastWeek: $('#last-week-btn'),
        lastMonth: $('#last-month-btn')
    }

    assignButtonCallbacks(buttons)
    buttons.today.click()
})
