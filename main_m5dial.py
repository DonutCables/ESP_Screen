print("imports")
import board
import displayio
import terminalio
import vectorio
import asyncio
import pwmio
import adafruit_focaltouch
from digitalio import DigitalInOut, Pull
from adafruit_display_text import label
from gc import enable, mem_free

# Display release
print("displayio release")
# displayio.release_displays()

# FT3267 touch init: 0x28, 0x38, 0x51
print("init touch")
screen_i2c = board.I2C()
irq = DigitalInOut(board.TOUCH_IRQ)
irq.switch_to_input(pull=Pull.UP)
ft = adafruit_focaltouch.Adafruit_FocalTouch(i2c=screen_i2c)

# Display init
print("init display")
display = board.DISPLAY

# Beeper init
print("init beeper")
beeper = pwmio.PWMOut(
    board.SPEAKER, duty_cycle=0, frequency=440, variable_frequency=True
)

# Create a display group
print("init group")
group = displayio.Group()

# Create a background fill
print("init bg")
palette = displayio.Palette(1)
palette[0] = 0x125690
circle = vectorio.Circle(pixel_shader=palette, radius=120, x=120, y=120)
group.append(circle)

# Position label
print("init position label")
position = "nerds"
position_area = label.Label(terminalio.FONT, text=position, scale=2)
position_area.x = 20
position_area.y = 100
group.append(position_area)

# Touch label
print("init touch label")
touchid = "nerds"
touchid_area = label.Label(terminalio.FONT, text=touchid, scale=1)
touchid_area.x = 20
touchid_area.y = 116
group.append(touchid_area)

# Show the display group
print("show group")
display.root_group = group


async def touch_wait():
    print("entering loop")
    while True:
        while ft.touched:
            beeper.duty_cycle = 65535 // 3
            for touch_id, touch in enumerate(ft.touches):
                x = touch["x"]
                y = touch["y"]
                position_area.text = f"Position: {x},{y}"
                touchid_area.text = f"Touch ID: {touch_id}"
                beeper.frequency = (x + y) * 2
        beeper.duty_cycle = 0
        await asyncio.sleep(0)


async def main():
    print("enable")
    enable()
    print("touch_task")
    touch_task = asyncio.create_task(touch_wait())
    print("gather")
    await asyncio.gather(touch_task)


if __name__ == "__main__":
    asyncio.run(main())
