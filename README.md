# ical Fixer

Working on Linux or Android can make it hard to connect with .ics calendars. 
I got problems when trying so and wrote an proxy with applies my needed fixes.

## Fixes

### Multiline Summary

Some events had one or multiple empty or newlines in the summary. Some clients like Thunderbird 128.3.0esr (64-bit) couldn't parse it.

```
...
DESCRIPTION:
SUMMARY:Arbeit: 

Frei
STATUS:CONFIRMED
...
```

I remove the empty lines to 

```
...
DESCRIPTION:
SUMMARY:Arbeit: Frei
STATUS:CONFIRMED
...
```

### Broken Timezone

The dates started at the wrong time after importing even if the timezone was set correctly. Even if the timezone was set correctly.

```
BEGIN:VCALENDAR
VERSION:2.0
METHOD:PUBLISH
X-WR-TIMEZONE:Europe/Berlin
...
BEGIN:VEVENT
DTSTART;TZID=Europe/Berlin:20241101T090000Z
DTEND;TZID=Europe/Berlin:20241101T180000Z
UID:2024-10-27-xxxx-xxxx-xxx
...
```

I fixed it by removing the `Z` at the end of the dates.

```
...
BEGIN:VEVENT
DTSTART;TZID=Europe/Berlin:20241101T090000
DTEND;TZID=Europe/Berlin:20241101T180000
UID:2024-10-27-xxxx-xxxx-xxx
...
```

### Allday Events

Events that doesn't have a time or should be allday events are not detected correctly.

```
...
DTSTART;TZID=Europe/Berlin:20241101T000000Z
DTEND;TZID=Europe/Berlin:2024110101T00000Z
...
```

I fixed it by removing the time and set the `DTEND` to set next day.

```
...
DTSTART;TZID=Europe/Berlin:20241101
DTEND;TZID=Europe/Berlin:2024110102
...
```

## Process

1. Checks if there is a local copy of the original .ics file
2. Asks remote server if the .ics file was updated and download it if needed
3. Apply fixes
4. Return new .ics file

## Idea

The idea is to host this simple server and use it link as calendar import.

This service is supposed to run behind a reverse proxy that handles TLS encryption!
