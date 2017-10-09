# mlog

`mlog` is an automated time tracker for Mac OS X (10.6+) with focus on complete
autonomy and inconspicuous resource consumption. It tracks user's active windows,
wraps them into a data structure and periodically writes them into a persistent
storage.

`mlog` aimed to be able to run for years while having a minimal CPU and space footprint.
Currently, it consumes `0.1` CPU while writing a data, `0.0` on idle,
and `38.8` KB of space per day.


- [mlog](#mlog)
    - [Instalation](#instalation)
    - [Usage](#usage)
        - [mlog](#mlog)
        - [frontend](#frontend)
    - [Architecture](#architecture)
        - [Backend](#backend)
            - [`Container`](#container)
            - [`Block`](#block)
            - [`Window`](#window)
        - [Data](#data)
            - [Layout](#layout)
            - [Space Complexity](#space-complexity)
            - [Frontend](#frontend)
        - [Frontend](#frontend)
            - [`CLI`](#cli)
    - [Why](#why)
    - [Side Notes](#side-notes)


## Instalation

Using `setup.py`

```
python3 setup.py install
```

or manually install required dependencies, which are listed in `setup.py`
and create a convenience alias in your `.bashrc` or `.zshrc` or `.whateverrc`.


## Usage

### mlog

`mlog` itself is a logger, therefore it should be run separately, for example

```
python3 mlog.py
```

Or as a separate process using some process manager.

`mlog` running it's processes in threads, therefore failure of a single thread
won't affect any other thread or data.


### frontend

In the current implementation frontend represented by `cli.py` script,
which can be called as follows:

```
python3 cli.py -h

usage: cli.py [-h] [-p] [-pt] [-py] [-pw] [-pm] [-t THRESHOLD]

Automatic time tracker client-side command line interface

optional arguments:
  -h, --help            show this help message and exit
  -p, --print           calculate and print today's usage
  -pt, --print_today    calculate and print today's usage
  -py, --print_yesterday
                        calculate and print yesterday's usage
  -pw, --print_week     calculate and print week's usage
  -pm, --print_month    calculate and print month's usage
  -t THRESHOLD, --threshold THRESHOLD
                        set threshold value in seconds
```


## Architecture

`mlog` explicitly designed to be *"hackable"*. It has two main components

* *backend*
* *frontend*

And a *data layout*.

Backend service collects usage statistics, based on a currently active window,
and writes it to a persistent storage. Frontend renders statistics from
the persistent storage.


### Backend

`mlog` takes a data about running apps using `AppKit`s `NSWorkspace` for locating
currently active application, and `Quartz` for finding a window name of this app.
For browsers `mlog` uses `AppleScript` [script](https://github.com/pvlbzn/mlog/blob/master/scripts/browser.applescript)
which returns currently active URL.

Each `n` seconds, currently `n` is defined to be `60` secods, `Container` is dumped
into the persistent storage. Each `m` seconds an active window is captured,
currently `m` is defined as `5` seconds.

The backend has 3 main entities:

1. Container
2. Block
3. Window


#### `Container`

`Container` represents current *time frame*. You can think of a time frame
as of a data wrapper for last `n` seconds data. `Container`'s name is an *epoch*
timestamp, such as `1506443613`. `Container` contains `Block`s.


#### `Block`

`Block` represents an application, however, with time management we are interested
not in the application itself, but in details about its windows. Let me explain
using a web browser example.

Google Chrome application is a `Block`. Imagine that you spent 90 minutes on Imgur
and 8 minutes on Coursera. In total you spent 98 minutes in one `Block`, however,
these 98 minutes doesn't say much without detailing. That's why the last piece
of a data structure is `Window`.


#### `Window`

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



### Data

Data layout is important because `mlog` consists of two separate parts, where
the *bridge* between them is a persistent storage. The only job of `mlog`
is to log activity into the database.


#### Layout

```
CREATE TABLE containers (
            container_id    integer primary key autoincrement,
            name            integer
);

CREATE TABLE blocks (
            block_id        integer primary key autoincrement,
            container_id    integer,
            name            text,
            foreign key (container_id) references containers (container_id)
);

CREATE TABLE windows (
            window_id   integer primary key autoincrement,
            block_id    integer,
            name        text,
            time        integer,
            foreign key (block_id) references blocks (block_id)
);
```


#### Space Complexity

While we can't estimate the upper bound of a space complexity, we may estimate
lower bound, Ω, assuming that we are given some constrains.

`mlog` has two crucial settings for data layer usage: `interval` and `iteration`.
`interval` defines how often `mlog` will call its procedures to track user's
activity. `iteration` defines how often `mlog` will write collected data from
a memory into a database. Both are measured in seconds.

If `interval = 5`, and `iteration = 60`, which we can interpret as: "Hey, `mlog`,
capture my activity each 5 seconds, store this data in memory and each 60 seconds
dump my data into the database.".

At a minimum user, per `Container`, uses one `Block` with one active `Window`.
Which can be read as: "User uses one window of some application per a given
time block".

That how data log looks like with debugging mode:

```
// Container updated and printed out each iteration. Each minute container
// is dumped into db and deallocated. New container created. Repeat.

Container(name: 1506927744, blocks:
    Block(name: Google Chrome, windows:
        Window([name: encrypted.google.com, time: 5],
        Window([name: www.quora.com, time: 10]), )
    Block(name: Code, windows:
        Window([name: README.md — mlog, time: 45]), ))

Container(name: 1506927804, blocks: 
    Block(name: Code, windows: 
        Window([name: README.md — mlog, time: 5]), ))

Container(name: 1506927804, blocks:
    Block(name: Code, windows:
        Window([name: README.md — mlog, time: 10]), ))
```

Therefore, each minute following events are expected:

1. One container record added
2. One block record added
3. One window record added

Theorethical space consumption of one construct is `712` bits, or `89` bytes,
based on the following calculations:

```
container:  int + int           = (64 + 64) / 8           = 16 bytes
block:      int + int + text    = (64 + 64 + 256) / 8     = 48 bytes
window:     int + int + text    = (64 + 64 + 256 + 8) / 8 = 49 bytes
```

*Note: size of the text isn't fixed, therefore it may be from 1 byte to n*

Practical space consumption of one construct is `576` bits or `72` bytes,
based on a personal usage statistics:

```
containers: 1775 items 28672 bytes      ->  16 bytes
blocks:     2413 items 53248 bytes      ->  22 bytes
windows:    3122 items 106396 bytes     ->  34 bytes
```

How well data growth predictable?

Using SQL queries to find average 

```SQL
select
   (select sum (length (name)) from blocks) / (select count(name) from blocks)
as block_name_avg;

-> 8

select
   (select sum (length (name)) from windows) / (select count(name) from windows)
as window_name_avg;

-> 18
```

On my data, I got `8` characters on average per `Block` (app name), and `18`
characters on average per `Window` (application's window).
By a simple calculations, using the following
[documentation](https://www.sqlite.org/datatype3.html) one may
assume that SQLite3 is using `UTF-8` and theoretical **estimations are correct**.



| Time    | Space Estimate (bytes) |
| ------- | ---------------------- |
| 1 hour  | `4 320`                |
| 1 day   | `103 680`              |
| 1 week  | `725 760`              |
| 1 month | `2 903 040`            |
| 1 year  | `34 836 480`           |



#### Frontend


| Time    | Space Estimate: Upper Bound (bytes) | Space Estimate: Average (bytes) |
| ------- | ----------------------------------- | ------------------------------- |
| 1 hour  | `4 320`                             | `4 320`                         |
| 1 day   | `103 680`                           | `38 880`                        |
| 1 week  | `725 760`                           | `272 160`                       |
| 1 month | `2 903 040`                         | `1 088 640`                     |
| 1 year  | `34 836 480`                        | `13 063 680`                    |


Note that average time estimation based on assumption that user uses computer
for `9` hours per day, therefore `38 880` bytes, or `38.8`KB per day, while
the upper bound is continuous, which is, normally, not the case.


### Frontend

`mlog` may have more than one frontends because final product of the backend part
is the data in persistent storage. The frontend has to work with this storage,
therefore there are no limitations for frontend by design.


#### `CLI`

*work in progress*



## Why

`mlog` was born in need of autonomous time tracking. Manual time tracking
is not a great thing because there are plenty of things which you will never
track, especially things which are related bad habits like reading news
or facebook. Other concern is a resource consumption.

For example, Toggl's mac os application consumes 1% of CPU and it has a habit
to occasionally hang or crash with some exception. A kitchen timer with labels
consumes more CPU then `Slack` in idle and it may even crash.


## Side Notes

Initially `mlog` was made in 2 evenings and was intended only for a personal use.
It needs to be refactored and stuff. Consider this project as pretty much "work
in progress". Later when all stuff will be fixed and nice this note will be deleted.

However, it works well and I use it on a daily basis and tweak it little by little.
