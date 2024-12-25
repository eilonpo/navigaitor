from server.external import McLumk_Wheel_Sports as bot

DEFAULT_SPEED = 5

def move(command_received: dict):
    if list(command_received.keys())[0] == "released":
        bot.stop_robot()
        return

    pressed_key = command_received["pressed"]

    if pressed_key == "forward":
        bot.move_forward(DEFAULT_SPEED)
    
    elif pressed_key == "backward":
        bot.move_backward(DEFAULT_SPEED)

    elif pressed_key == "left":
        bot.rotate_left(DEFAULT_SPEED)

    elif pressed_key == "right":
        bot.rotate_right(DEFAULT_SPEED)
