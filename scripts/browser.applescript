-- Get a currently active tab URL 
--
-- Contribution to this file are very welcome:
-- There should be a way to make it nicer, however it does it's job
--
-- Tested on osx 10.12.5

-- In all system processes
tell application "System Events"
    -- Find a matching name
	if application process "Google Chrome" exists then
        -- and return a URL of a currently active tab
		tell application "Google Chrome" to get URL of active tab of first window
	else if application process "Safari" exists then
		tell application "Google Chrome" to get URL of active tab of first window
	else if application process "Firefox" exists then
		tell application "Google Chrome" to get URL of active tab of first window
	else
		return ""
	end if
end tell
