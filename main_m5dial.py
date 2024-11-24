print("imports")
import board
import displayio
import terminalio
import vectorio
import asyncio
import pwmio
from digitalio import DigitalInOut, Pull
from rotaryio import IncrementalEncoder
import adafruit_focaltouch
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
ft = adafruit_focaltouch.Adafruit_FocalTouch(i2c=screen_i2c)  # , irq_pin=irq)

# Encoder init
print("init encoder")
encoder = IncrementalEncoder(board.ENC_A, board.ENC_B)
enc_button = DigitalInOut(board.KNOB_BUTTON)
enc_button.switch_to_input(pull=Pull.UP)

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

# Encoder label
print("init encoder label")
enc_label = "nerds"
enc_area = label.Label(terminalio.FONT, text=enc_label, scale=1)
enc_area.x = 20
enc_area.y = 132
group.append(enc_area)

# Encoder button label
print("init encoder button label")
enc_button_label = "nerds"
enc_button_area = label.Label(terminalio.FONT, text=enc_button_label, scale=1)
enc_button_area.x = 20
enc_button_area.y = 148
group.append(enc_button_area)

# Show the display group
print("show group")
display.root_group = group


class ENCStates:
    """Manages encoder rotation"""

    def __init__(self, encoder):
        self.encoder = encoder
        self.last_position = self.encoder.position
        self._was_rotated = asyncio.Event()

    async def update(self):
        """Updates the pressed state of the encoder"""
        while True:
            if (
                self.encoder.position != self.last_position
                and not self._was_rotated.is_set()
            ):
                self._was_rotated.set()
            await asyncio.sleep(0)

    def encoder_handler(self):
        """Handles encoder rotation"""
        if self.encoder.position > self.last_position:
            self.last_position = self.encoder.position
            self._was_rotated.clear()
            return "CCW"
        elif self.encoder.position < self.last_position:
            self.last_position = self.encoder.position
            self._was_rotated.clear()
            return "CW"


async def touch_wait():
    "Primary loop to wait for inputs"
    print("entering loop")
    button_presses = 0
    while True:
        # print("prerotate")
        if ENCS._was_rotated.is_set():
            print("rotated")
            enc_area.text = f"Encoder: {ENCS.encoder_handler()}"
        if not enc_button.value:
            print("button")
            button_presses += 1
            enc_button_area.text = f"Pressed:{button_presses}"
        # print("pretouch")
        try:
            if ft.touched > 0:
                print("touched")
                beeper.duty_cycle = 65535 // 3
                for touch_id, touch in enumerate(ft.touches):
                    x = touch["x"]
                    y = touch["y"]
                    position_area.text = f"Position: {x},{y}"
                    touchid_area.text = f"Touch ID: {touch_id}"
                    beeper.frequency = (x + y) * 2
                await asyncio.sleep(0)
                beeper.duty_cycle = 0
        except OSError:
            pass
        await asyncio.sleep(0)


ENCS = ENCStates(encoder)


async def main():
    "Function to setup async tasks"
    print("enable")
    enable()
    print("touch_task")
    touch_task = asyncio.create_task(touch_wait())
    encoder_task = asyncio.create_task(ENCS.update())
    print("gather")
    await asyncio.gather(touch_task, encoder_task)


if __name__ == "__main__":
    asyncio.run(main())
