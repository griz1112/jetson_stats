# -*- coding: UTF-8 -*-
# Copyright (C) 2019, Raffaello Bonghi <raffaello@rnext.it>
# All rights reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# control command line
import curses
from curses.textpad import rectangle
# Math functions
from math import ceil
# Functions and decorators
from functools import wraps


def check_size(height_max, width_max):
    """ Check curses size window """
    def check_size_window(func):
        @wraps(func)
        def wrapped(self, *args, **kwargs):
            # Extract window size
            height, width = self.stdscr.getmaxyx()
            # Check size window
            if width >= width_max and height >= height_max:
                return func(self, *args, **kwargs)
            else:
                string_warning = "jtop"
                string_warning_msg = "Change size window!"
                size_window_width = "Width: " + str(width) + " >= " + str(width_max)
                size_window_height = "Height: " + str(height) + " >= " + str(height_max)
                try:
                    height_c = int(height / 2)
                    self.stdscr.addstr(height_c - 2, int((width - len(string_warning)) / 2), string_warning, curses.A_BOLD)
                    self.stdscr.addstr(height_c - 1, int((width - len(string_warning_msg)) / 2), string_warning_msg, curses.A_BOLD)
                    # Show size window
                    if width < width_max:
                        self.stdscr.addstr(height_c, int((width - len(size_window_width)) / 2), str(size_window_width), curses.color_pair(1))
                    else:
                        size_window_width = "Width OK!"
                        self.stdscr.addstr(height_c, int((width - len(size_window_width)) / 2), size_window_width, curses.A_BOLD)
                    if height < height_max:
                        self.stdscr.addstr(height_c + 1, int((width - len(size_window_height)) / 2), str(size_window_height), curses.color_pair(1))
                    else:
                        size_window_height = "Height OK!"
                        self.stdscr.addstr(height_c + 1, int((width - len(size_window_height)) / 2), str(size_window_height), curses.A_BOLD)
                    # Set background for all menu line
                    self.stdscr.addstr(height - 1, 0, ("{0:<" + str(width - 1) + "}").format(" "), curses.A_REVERSE)
                    # Add close option menu
                    self.stdscr.addstr(height - 1, 1, "Q to close", curses.A_REVERSE)
                except curses.error:
                    pass
        return wrapped
    return check_size_window


def check_curses(func):
    """ Check curses write """
    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except curses.error:
            pass
    return wrapped


def strfdelta(tdelta, fmt):
    """ Print delta time
        - https://stackoverflow.com/questions/8906926/formatting-python-timedelta-objects
    """
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


@check_curses
def box_keyboard(stdscr, x, y, letter, key):
    # Draw background rectangle
    rectangle(stdscr, y, x, y + 2, x + 4)
    # Default status
    status = curses.A_NORMAL if key != ord(letter) else curses.A_REVERSE
    # Write letter
    stdscr.addstr(y + 1, x + 2, letter, status)
    # Return the status of key
    return True if key == ord(letter) else False


@check_curses
def box_status(stdscr, x, y, name, status=False, color=curses.A_REVERSE):
    # Draw background rectangle
    rectangle(stdscr, y, x, y + 2, x + 3 + len(name))
    # Default status
    status = color if status else curses.A_NORMAL
    # Write letter
    stdscr.addstr(y + 1, x + 2, name, status)


@check_curses
def box_list(stdscr, x, y, data, selected, status=[], max_width=-1, numbers=False):
    len_prev = 0
    line = 0
    skip_line = False if max_width == -1 else True
    for idx, name in enumerate(data):
        if status:
            color = curses.A_REVERSE if status[idx] else curses.color_pair(1)
            status_selected = True if selected == idx else not status[idx]
        else:
            status_selected = True if selected == idx else False
        # Add number idx if required
        str_name = name if not numbers else str(idx) + " " + name
        # Find next position
        if skip_line and len_prev + len(str_name) + 4 >= max_width:
            line += 3
            len_prev = 0
        # Plot box
        box_status(stdscr, x + len_prev, y + line, str_name, status=status_selected, color=color)
        len_prev += len(str_name) + 4
    # Draw background rectangle
    # rectangle(stdscr, y, x, y + 2, x + 3 + len(name))
    return line


@check_curses
def draw_chart(stdscr, size_x, size_y, value, line="*", color=curses.A_NORMAL):
    # Get Max value and unit from value to draw
    max_val = 100 if "max_val" not in value else value["max_val"]
    unit = "%" if "max_val" not in value else value["unit"]
    # Evaluate Diplay X, and Y size
    displayX = size_x[1] - size_x[0] + 1
    displayY = size_y[1] - size_y[0] - 1
    val = float(displayX - 2) / float(len(value["idle"]))
    points = []
    for n in value["idle"]:
        points += [n] * int(ceil(val))
    # Plot chart shape and labels
    for point in range(displayY):
        if displayY != point:
            value_n = max_val / float(displayY - 1) * float(displayY - point - 1)
            try:
                stdscr.addstr(1 + size_y[0] + point, size_x[1], "-")
                stdscr.addstr(1 + size_y[0] + point, size_x[1] + 2,
                              "{value:3d}{unit}".format(value=int(value_n), unit=unit),
                              curses.A_BOLD)
            except curses.error:
                pass
    for point in range(displayX):
        try:
            stdscr.addstr(size_y[1], size_x[0] + point, "-")
        except curses.error:
            pass
    # Text label
    info_string = value["name"] if "name" in value else ""
    stdscr.addstr(size_y[0], size_x[0], info_string, curses.A_BOLD)
    if "percent" in value:
        stdscr.addstr(size_y[0], size_x[0] + len(info_string) + 1, value["percent"], color)
    # Plot values
    for idx, point in enumerate(reversed(points)):
        y_val = int((float(displayY - 1) / max_val) * point)
        x_val = size_x[1] - 1 - idx
        if x_val >= size_x[0]:
            try:
                stdscr.addstr(size_y[1] - 1 - y_val, x_val, line, color)
            except curses.error:
                pass


def make_gauge_from_percent(data):
    gauge = {'name': data['name'], 'status': data['status']}
    if "ON" in data["status"]:
        gauge['value'] = int(data['idle'][-1])
    if data["status"] == "ON":
        freq = data['frequency'][-1]
        if freq >= 1000:
            gauge['label'] = "{0:2.1f}GHz".format(freq / 1000.0)
        else:
            gauge['label'] = str(int(freq)) + "MHz"
    return gauge


@check_curses
def linear_percent_gauge(stdscr, gauge, max_bar, offset=0, start=0, type_bar="|", color_name=6):
    # Evaluate size withuout short name
    name_size = len(gauge['name'])
    size_bar = max_bar - name_size - 4
    # Show short name linear gauge
    stdscr.addstr(offset, start, ("{short_name:" + str(name_size) + "}").format(short_name=gauge['name']), curses.color_pair(color_name))
    if 'value' in gauge:
        # Check if the list of value is list or value
        if isinstance(gauge['value'], list):
            value = gauge['value'][-1]
        else:
            value = gauge['value']
        # Show bracket linear gauge and label and evaluate size withuout size labels and short name
        size_bar -= (len(gauge['label']) + 1) if 'label' in gauge else 0
        stdscr.addstr(offset, start + name_size + 1, "[" + " " * size_bar + "]", curses.A_BOLD)
        if 'label' in gauge:
            stdscr.addstr(offset, start + name_size + 1 + size_bar + 3, gauge['label'])
        # Show progress value linear gauge
        n_bar = int(float(value) * float(size_bar) / 100.0)
        if n_bar >= 0:
            progress_bar = type_bar * n_bar
            # Build progress barr string
            str_progress_bar = ("{n_bar:" + str(size_bar) + "}").format(n_bar=progress_bar)
            percent_label = gauge['percent'] if 'percent' in gauge else str(value) + "%"
            str_progress_bar = str_progress_bar[:size_bar - len(percent_label)] + percent_label
            # Split string in green and grey part
            green_part = str_progress_bar[:n_bar]
            grey_part = str_progress_bar[n_bar:]
            stdscr.addstr(offset, start + name_size + 2, green_part, curses.color_pair(2))
            stdscr.addstr(offset, start + name_size + 2 + size_bar - len(grey_part), grey_part, curses.A_DIM)
    else:
        # Show bracket linear gauge and label
        stdscr.addstr(offset, start + name_size + 1, ("[{value:>" + str(size_bar) + "}]").format(value=" "))
        # Show bracket linear gauge and label
        status = gauge["status"] if "status" in gauge else "OFF"
        stdscr.addstr(offset, start + name_size + 4, status, curses.color_pair(1))


@check_curses
def plot_dictionary(stdscr, offset, data, name, start=0):
    # Plot title
    stdscr.addstr(offset, start, name + ":", curses.A_BOLD)
    counter = 1
    for key, value in data.items():
        if 'text' in value:
            stdscr.addstr(offset + counter, start, " {0:<10} {1}".format(key, value['text']))
        else:
            stdscr.addstr(offset + counter, start, " {0:<10} {1}".format(key, value))
        counter += 1


@check_curses
def plot_name_info(stdscr, offset, start, name, value, color=curses.A_NORMAL):
    stdscr.addstr(offset, start, name + ":", curses.A_BOLD)
    stdscr.addstr(offset, start + len(name) + 2, value, color)
# EOF