import requests
import re
import os
from datetime import datetime, timezone
from icalendar import Calendar


class IcalFixer:
    url = ""
    file_name = ""
    path_tmp_ics = ""
    path_fixed_ics = ""
    last_modified = None

    def __init__(self, url):
        self.url = url
        assert url.startswith("https://") or url.startswith("http://"), "Url is not a valid link"
        assert url.endswith(".ics"), "Url does not link to an .ics file"

        url_splits = self.url.split('/')
        assert len(url_splits) > 0, "Url does not contain valid link"

        self.file_name = url_splits[-1]
        assert self.file_name.endswith('.ics'), "Failed to extract file name"

        self.path_tmp_ics = f"tmp_{self.file_name}"

    def convert(self):
        data = self.fetch_ics()
        if not data:
            with open(self.path_tmp_ics, "r") as f:
                data = "".join(f.readlines())

        converted_data = self.apply_fixes(data)
        self.is_valid_ics(converted_data)
        return converted_data

    def get_last_modified_from_file(self):
        if os.path.exists(self.path_tmp_ics):
            mtime = os.path.getmtime(self.path_tmp_ics)
            return datetime.fromtimestamp(mtime, tz=timezone.utc)
        return None

    def fetch_ics(self):
        self.last_modified = self.get_last_modified_from_file()
        headers = {}
        if self.last_modified:
            headers["If-Modified-Since"] = self.last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")
        response = requests.get(self.url, headers=headers)

        ics_data = ""
        if response.status_code == 200:
            ics_data = response.text.replace('\n', '\r\n')
            with open(self.path_tmp_ics, "w") as f:
                f.write(ics_data)
        elif response.status_code == 304:
            print("File hasn't change! Skip download..")
        else:
            print("ERROR: Failed to download .ics file from url - Status Code: %s" % response.status_code)

        return ics_data

    def apply_fixes(self, data):
        pattern_multiline = re.compile(r"(SUMMARY:.+?)$\n*(^.+$)+\n(STATUS:.+$)", re.MULTILINE)
        pattern_timezone = re.compile(r"^(DTSTART|DTEND|CREATED|LAST-MODIFIED|DTSTAMP)(.+?)Z$", re.MULTILINE)
        pattern_allday_start = re.compile(r"(DTSTART;VALUE=DATE:)(\d{8})T000000Z")
        pattern_allday_end = re.compile(r"(DTEND;VALUE=DATE:)(\d{8})T000000Z")

        fixed_data = pattern_allday_start.sub(r"\1\2", data)
        fixed_data = pattern_allday_end.sub(lambda m: f"{m.group(1)}{m.group(2)}", fixed_data)
        fixed_data = re.sub(r"(DTEND;VALUE=DATE:)(\d{8})", lambda m: f"{m.group(1)}{int(m.group(2)) + 1:08d}", fixed_data)

        fixed_data = pattern_timezone.sub(r"\1\2", fixed_data)
        fixed_data = pattern_multiline.sub(r"\1\2\n\3", fixed_data)

        return fixed_data

    def is_valid_ics(self, data):
        try:
            Calendar.from_ical(data)
            print("INFO: data is valid ical data!")
            return True
        except Exception as e:
            print("ERROR: while checking ical data validity. %s" % e)
            return False

    def store_fixed_file(self, data):
        with open("converted.ics", "w") as f:
            f.write(data)


if __name__ == "__main__":
    url = "https://my-url/calendar.ics"
    ical_fixer = IcalFixer(url)
    ical_fixer.convert()
