#!/usr/bin/env python3

import datetime
import logging

import dateutil.parser


class Time:
    def __init__(self, s: str) -> None:
        logger = logging.getLogger(__name__)
        if "@" in s:
            s = s.replace("@", " ")
        self.s = s
        try:
            logger.info(f"Trying to parse {s} as a datetime")
            now = datetime.datetime.now()
            self.datetime = self._parse_future(s)
            self.seconds = int((self.datetime - now).total_seconds())
            if self.datetime - now < datetime.timedelta(days=1):
                # Just print like 10:00am
                self.str = self.datetime.strftime("at %I:%M%P")
            else:
                # Full date string
                self.str = self.datetime.strftime("at %Y-%m-%d %I:%M%P")
            logger.info(f"Parsed to {self.str} ({self.datetime})")
        except Exception:
            self.datetime = None
            self.seconds = self._old_style_seconds(s)
            self.str = f"in {self.s} ({self.seconds} seconds)"
            logger.info(f"Parsed to {self.str} -- could not parse as datetime")

    # Adapted from https://stackoverflow.com/a/13430049
    def _parse_future(self, s: str) -> datetime.datetime:
        """Same as dateutil.parser.parse() but only returns future dates."""
        now = datetime.datetime.now()
        default = now
        for _ in range(365):
            dt = dateutil.parser.parse(s, default=default)
            if dt > now:
                return dt
            default += datetime.timedelta(days=1)
            default = default.replace(hour=0, minute=0, second=0, microsecond=0)
        raise ValueError("Could not parse future date")

    def _old_style_seconds(self, s: str) -> int:
        units = {}
        units["s"] = 1
        units["m"] = units["s"] * 60
        units["h"] = units["m"] * 60
        units["d"] = units["h"] * 24
        units["y"] = units["d"] * 365

        seconds = 0
        idx = 0
        while idx < len(s):
            builder = 0
            # Get value
            while idx < len(s) and s[idx].isdigit():
                builder = builder * 10 + int(s[idx])
                idx += 1
            # Now get unit
            unit_value = units[s[idx]]
            # Consume until end of units or string
            while idx < len(s) and not s[idx].isdigit():
                idx += 1
            # Add to total
            seconds += builder * unit_value
        return seconds

    def __str__(self) -> str:
        return self.str

    def __repr__(self) -> str:
        return str(self)
