import board
import displayio
import terminalio
import vectorio
import asyncio
import busio
from adafruit_display_text import label
from gc9a01 import GC9A01
import adafruit_cst8xx
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
ctp = adafruit_cst8xx.Adafruit_CST8XX(screen_i2c)
events = adafruit_cst8xx.EVENTS

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

# Event label
event = "nerds"
event_area = label.Label(terminalio.FONT, text=event, scale=1)
event_area.x = 20
event_area.y = 116
group.append(event_area)

# Touch label
touchid = "nerds"
touchid_area = label.Label(terminalio.FONT, text=touchid, scale=1)
touchid_area.x = 20
touchid_area.y = 132
group.append(touchid_area)

# Show the display group
display.root_group = group


async def touch_wait():
    while True:
        if ctp.touched:
            for touch_id, touch in enumerate(ctp.touches):
                x = touch["x"]
                y = touch["y"]
                event = events[touch["event_id"]]
                position_area.text = f"Position: {x},{y}"
                event_area.text = f"Event: {event}"
                touchid_area.text = f"Touch ID: {touch_id}"
        await asyncio.sleep(0)


async def main():
    enable()
    touch_task = asyncio.create_task(touch_wait())
    await asyncio.gather(touch_task)


if __name__ == "__main__":
    asyncio.run(main())
