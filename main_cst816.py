import board
import displayio
import terminalio
import vectorio
import asyncio
import busio
from adafruit_display_text import label
from gc9a01 import GC9A01
from cst816 import CST816
from gc import enable, mem_free

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

# Position label
position = "nerds"
position_area = label.Label(terminalio.FONT, text=position, scale=2)
position_area.x = 20
position_area.y = 100
group.append(position_area)

# Create a text label
gesture = "nerds"
gesture_area = label.Label(terminalio.FONT, text=gesture, scale=1)
gesture_area.x = 20
gesture_area.y = 116
group.append(gesture_area)

# Create a text label
pressed = "nerds"
pressed_area = label.Label(terminalio.FONT, text=pressed, scale=1)
pressed_area.x = 20
pressed_area.y = 132
group.append(pressed_area)

# Create a text label
distance = "nerds"
distance_area = label.Label(terminalio.FONT, text=distance, scale=1)
distance_area.x = 20
distance_area.y = 148
group.append(distance_area)

# Show the display group
display.root_group = group


async def touch_wait():
    while True:
        point = touch.get_point()
        gesture = touch.get_gesture()
        press = touch.get_touch()
        distance = touch.get_distance()
        if press > 0:
            position = f"Position: {point.x_point},{point.y_point}"
            gesture = f"Gesture: {gesture}"
            pressed = f"Pressed? {press}"
            distance = f"Distance: {distance.x_dist},{distance.y_dist}"
            position_area.text = position
            gesture_area.text = gesture
            pressed_area.text = pressed
            distance_area.text = distance
        await asyncio.sleep(0)


async def main():
    enable()
    touch_task = asyncio.create_task(touch_wait())
    await asyncio.gather(touch_task)


asyncio.run(main())
