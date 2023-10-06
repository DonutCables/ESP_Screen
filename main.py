import board
import displayio
import terminalio
import vectorio
import asyncio
import busio
from adafruit_display_text import label
from gc9a01 import GC9A01
from cst816 import CST816

displayio.release_displays()

# Initialize the display
tft_spi = busio.SPI(clock=board.IO6, MOSI=board.IO7)
tft_cs = board.IO10  # GPIO pin for the CS (Chip Select) of the display
tft_dc = board.IO2  # GPIO pin for the DC (Data/Command) of the display
tft_rst = board.IO1  # GPIO pin for the RESET of the display
tft_bl = board.IO3

# cst816
screen_i2c = busio.I2C(scl=board.IO5, sda=board.IO4)
touch = CST816(screen_i2c)

# touch.reset()
# screen_int = board.IO0
# screen_reset = board.IO1

display_bus = displayio.FourWire(
    spi_bus=tft_spi,
    command=tft_dc,
    chip_select=tft_cs,
    reset=tft_rst,
    baudrate=40000000,
)

display = GC9A01(display_bus, width=240, height=240, backlight_pin=tft_bl)

# Create a display group
group = displayio.Group()

# Create a background fill
palette = displayio.Palette(1)
palette[0] = 0x125690
circle = vectorio.Circle(pixel_shader=palette, radius=120, x=120, y=120)
group.append(circle)

# Create a text label
text = "nerds"
text_area = label.Label(terminalio.FONT, text=text, color=0x000000)
text_area.x = 30
text_area.y = 120
group.append(text_area)

# Show the display group
display.root_group = group


async def touch_wait():
    while True:
        point = touch.get_point()
        gesture = touch.get_gesture()
        press = touch.get_touch()
        distance = touch.get_distance()
        if press > 0:
            text = f"Position: {point.x_point},{point.y_point} - Gesture: {gesture} - Pressed? {press} - Distance: {distance.x_dist},{distance.y_dist}"
            text_area = label.Label(terminalio.FONT, text=text, color=0x000000)
            text_area.x = 10
            text_area.y = 120
            group.append(text_area)
        await asyncio.sleep(0)


async def main():
    touch_task = asyncio.create_task(touch_wait())
    await asyncio.gather(touch_task)


asyncio.run(main())
