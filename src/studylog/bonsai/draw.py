# PyBonsai - vendored from https://github.com/Ben-Edwards44/PyBonsai
# Copyright 2024 Ben Edwards - MIT License
# Modified: updated import of utils to package-relative.
import math
import random
from sys import stdout
from time import sleep

from studylog.bonsai import utils


#ANSI escape codes (https://en.wikipedia.org/wiki/ANSI_escape_code)
END_COLOUR = "\033[00m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"

CHAR_THRESHOLD = 0.3


class TerminalWindow:
    CHAR_WIDTH = 1
    CHAR_HEIGHT = 2

    BACKGROUND_CHAR = " "

    def __init__(self, width, height, options):
        self.width = width
        self.height = height

        self.options = options

        self.chars = [[TerminalWindow.BACKGROUND_CHAR for _ in range(width)] for _ in range(height)]

    def colour_char(self, char, r, g, b):
        if stdout.isatty():
            return f"\033[38;2;{r};{g};{b}m{char}{END_COLOUR}"
        else:
            return char

    def extract_colour(self, coloured_char):
        splitted = coloured_char.split(";")

        r = int(splitted[2])
        g = int(splitted[3])

        b = ""
        for i in splitted[4]:
            if i == "m":
                break
            else:
                b += i

        b = int(b)

        return r, g, b

    def clear_chars(self):
        self.chars = [[TerminalWindow.BACKGROUND_CHAR for _ in range(self.width)] for _ in range(self.height)]

    def draw(self):
        if stdout.isatty():
            print(HIDE_CURSOR, end="")

        for i in self.chars:
            print("".join(i))

        if stdout.isatty():
            print(f"\033[{self.height}A", end="")
            print(SHOW_CURSOR, end="")

        self.needs_clear = True

    def reset_cursor(self):
        if stdout.isatty():
            print(f"\033[{self.height}B", end="")

    def plane_to_screen(self, x, y):
        scaled_x = x / TerminalWindow.CHAR_WIDTH
        scaled_y = y / TerminalWindow.CHAR_HEIGHT

        inx1 = round(self.height - scaled_y)
        inx2 = round(scaled_x)

        return inx1, inx2

    def screen_to_plane(self, x, y):
        swapped_x = y
        swapped_y = self.height - x

        scaled_x = swapped_x * TerminalWindow.CHAR_WIDTH
        scaled_y = swapped_y * TerminalWindow.CHAR_HEIGHT

        return scaled_x, scaled_y

    def increase_height(self, delta_height):
        if self.options.fixed_window:
            return False

        self.height += delta_height

        for _ in range(delta_height):
            self.chars.insert(0, [TerminalWindow.BACKGROUND_CHAR for _ in range(self.width)])

        return True

    def set_char_instant(self, x, y, char, colour, is_screen_coords):
        if not is_screen_coords:
            x, y = self.plane_to_screen(x, y)

        if x < 0:
            height_changed = self.increase_height(abs(x))

            if height_changed:
                x = 0

        if not 0 <= x < self.height or not 0 <= y < self.width:
            return

        coloured = self.colour_char(char, colour[0], colour[1], colour[2])
        self.chars[x][y] = coloured

    def set_char_wait(self, x, y, char, colour, is_screen_coords, wait_time):
        self.set_char_instant(x, y, char, colour, is_screen_coords)

        self.draw()
        sleep(wait_time)

    def get_line_char(self, line):
        theta = line.get_theta()

        upper = math.pi / 2 * (2 / 3)
        lower = math.pi / 2 * (1 / 3)

        if abs(theta) > upper:
            return "|"
        elif abs(theta) < lower:
            return "_"
        elif theta > 0:
            return "/"
        else:
            return "\\"

    def choose_colour(self, colour):
        if type(colour[0]) == int:
            return colour
        elif len(colour[0]) == 2:
            rand_colour = []
            for lower, upper in colour:
                value = random.randint(lower, upper)
                rand_colour.append(value)

            return rand_colour
        else:
            raise Exception("Invalid colour argument")

    def draw_steep_line(self, start, end, colour, width, char, mid_line):
        start_inx, _ = self.plane_to_screen(*start)
        end_inx, _ = self.plane_to_screen(*end)

        step = 1 if end_inx > start_inx else -1

        for inx1 in range(start_inx, end_inx + step, step):
            dists = []
            for inx2 in range(self.width):
                x, y = self.screen_to_plane(inx1, inx2)

                desired_x = mid_line.get_x(y)
                dist = abs(desired_x - x)

                dists.append([dist, inx2])

            dists.sort()
            for i in range(width):
                if i >= len(dists):
                    break

                if random.uniform(0, 1) < CHAR_THRESHOLD:
                    chosen_char = random.choice(self.options.branch_chars)
                else:
                    chosen_char = char

                chosen_colour = self.choose_colour(colour)

                if self.options.instant:
                    self.set_char_instant(inx1, dists[i][1], chosen_char, chosen_colour, True)
                else:
                    self.set_char_wait(inx1, dists[i][1], chosen_char, chosen_colour, True, self.options.wait_time)

    def draw_shallow_line(self, start, end, colour, width, char, mid_line):
        _, start_inx = self.plane_to_screen(*start)
        _, end_inx = self.plane_to_screen(*end)

        step = 1 if end_inx > start_inx else -1

        for inx2 in range(start_inx, end_inx + step, step):
            dists = []
            for inx1 in range(self.height):
                x, y = self.screen_to_plane(inx1, inx2)

                desired_y = mid_line.get_y(x)
                dist = abs(desired_y - y)

                dists.append([dist, inx1])

            dists.sort()
            for i in range(width):
                if i >= len(dists):
                    break

                if random.uniform(0, 1) < CHAR_THRESHOLD:
                    chosen_char = random.choice(self.options.branch_chars)
                else:
                    chosen_char = char

                chosen_colour = self.choose_colour(colour)

                if self.options.instant:
                    self.set_char_instant(dists[i][1], inx2, chosen_char, chosen_colour, True)
                else:
                    self.set_char_wait(dists[i][1], inx2, chosen_char, chosen_colour, True, self.options.wait_time)

    def check_line_bounds(self, start, end):
        h1, _ = self.plane_to_screen(*start)
        h2, _ = self.plane_to_screen(*end)

        room_from_top = min(h1, h2)

        if room_from_top < 0:
            self.increase_height(abs(room_from_top))

    def draw_line(self, start, end, colour, width):
        mid_line = utils.Line()
        mid_line.set_end_points(start, end)

        char = self.get_line_char(mid_line)

        self.check_line_bounds(start, end)

        if mid_line.is_vertical or abs(mid_line.m) >= 1:
            self.draw_steep_line(start, end, colour, width, char, mid_line)
        else:
            self.draw_shallow_line(start, end, colour, width, char, mid_line)
