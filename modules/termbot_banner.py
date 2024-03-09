import math

termbot_logo = r"""
  _______                  _           _     ____   ___   ___   ___
 |__   __|                | |         | |   |___ \ / _ \ / _ \ / _ \
    | | ___ _ __ _ __ ___ | |__   ___ | |_    __) | | | | | | | | | |
    | |/ _ \ '__| '_ ` _ \| '_ \ / _ \| __|  |__ <| | | | | | | | | |
    | |  __/ |  | | | | | | |_) | (_) | |_   ___) | |_| | |_| | |_| |
    |_|\___|_|  |_| |_| |_|_.__/ \___/ \__| |____/ \___/ \___/ \___/

"""

# Define the gradient colors
blue = (0, 0, 255)  # RGB value for blue
pink = (255, 105, 180)  # RGB value for pink

# Split the ASCII art into lines
lines = termbot_logo.strip().split('\n')

# Determine the number of color steps based on the number of lines
num_steps = len(lines)

# Apply color formatting and display the ASCII art with gradient
colored_ascii_art = ''
for i, line in enumerate(lines):
    # Calculate the interpolation factor for the gradient
    factor = i / (num_steps - 1)

    # Interpolate the RGB values between blue and pink
    r = math.floor(blue[0] * (1 - factor) + pink[0] * factor)
    g = math.floor(blue[1] * (1 - factor) + pink[1] * factor)
    b = math.floor(blue[2] * (1 - factor) + pink[2] * factor)

    # Convert the RGB values to ANSI escape code for the corresponding color
    color_code = f'\033[38;2;{r};{g};{b}m'

    # Apply the color code to the line and append to the output
    colored_ascii_art += color_code + line + '\n'

# Reset the color to default
colored_ascii_art += '\033[0m'

# Define color codes
purple = '\033[95m'
blue = '\033[94m'
reset = '\033[0m'


# AUTH

# COLORS
GRAY = "\033[90m"
LIGHT_BLUE = "\033[94m"
PINK = "\033[95m"
RESET = "\033[0m"
