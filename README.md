# mlog

`mlog` is an automated timetracker for Mac OS X (10.6+) with focus on complete
autonomy and inconspicuous resource consumption.

While running in the background `mlog` consumes from `0.0` to `0.1` CPU.


### Architecture

`mlog` explicitly designed to be "hackable". It has two main components:

* backend
* frontend

Backend service collects usage statistics, based on currently active window,
and writes it to a persistent storage. Frontend renders statistics from
the persistent storage.


#### Backend

`mlog` takes a data about running apps using `AppKit`s `NSWorkspace` for locating
currently active application, and `Quartz` for finding a window name of this app.
For browsers `mlog` uses `AppleScript` [script](https://github.com/pvlbzn/mlog/blob/master/scripts/browser.applescript)
which returns currently active URL.

Each `n` seconds, currently set `n` is defined to be `60`, `Container` is dumped
into the persistent storage.

Backend has 3 main entities:

1. Container
2. Block
3. Window


##### `Container`

`Container` represents current *time frame*. You can think of a time frame
as of a data wrapper for last `n` seconds data. `Container`'s name is an *epoch*
timestamp, such as `1506443613`. `Container` contains `Block`s.


##### `Block`

`Block` represents an application, however with time management we are interested
not in application itself, but in details about its windows. Let me explain
using a web browser example.

Google Chrome application is a `Block`. Imagine that you spent 90 minutes on Imgur
and 8 minutes on Coursera. In total you spent 98 minutes in one `Block`, however
these 98 minutes doesn't say much without detalization. Thats why last piece
of a data structure is `Window`.


##### `Window`

`Window` represents a window of some application. Continuing with our web browser
example `coursera.org` is a window as `imgur.com` is `Window` too.


Therefore full data structure might look like:

```
Container(
    name: 1506444094,
    blocks: 
        Block(
            name: Code,
            windows: [name: README.md — mlog, time: 55],)
        Block(
            name: Google Chrome,
            windows: [name: encrypted.google.com, time: 5],)
)
```

`Container` contains one or more `Block`s each of which contains one or more
`Window`s.


#### Frontend

`mlog` may have more than one frontends because final product of the backend part
is the data in persistent storage. Frontend have to work with this storage,
therefore there are no limitations for frontend by design.

##### `CLI`

*work in progress*


### Why

`mlog` was born in need of autonomous time tracking. Manual timetracking
is not a great thing because there are plenty of things which you will never
track, especially things which are related bad habbits like reading news
or facebook.

For example Toggl's mac os application consumes 1% of CPU and it has a habbit
to occasionaly hang or crash with some exception. Damn kitchen timer with labels
consumes more CPU then `Slack` in idle and it may crash.


### Side Notes

Initially `mlog` was made in 2 evenings and was intended only for a personal use.
It needs to be refactored and stuff. Consider this project as pretty much "work
in progress". Later when all stuff will be fixed and nice this note will be deleted.
