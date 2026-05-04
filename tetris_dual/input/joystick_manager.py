import arcade

class JoystickManager:
    """
    Управляет двумя джойстиками (геймпадами).
    Поддерживает PS4-контроллеры как замену «КиберМишкам».
    """
    def __init__(self):
        joysticks = arcade.get_joysticks()
        self.joysticks = []
        for j in joysticks[:2]:  # Берём максимум 2
            j.open()
            j.push_handlers(self)
            self.joysticks.append(j)

        # Если контроллеров < 2 — работаем в режиме заглушки
        while len(self.joysticks) < 2:
            self.joysticks.append(None)

    def get_input(self, player_id: int):
        """
        Возвращает словарь команд для игрока (player_id: 0 или 1).
        Формат: {'left': bool, 'right': bool, 'rotate': bool, 'drop': bool}
        """
        if player_id not in (0, 1):
            raise ValueError("player_id must be 0 or 1")

        joy = self.joysticks[player_id]
        if joy is None:
            return {'left': False, 'right': False, 'rotate': False, 'drop': False}

        # Оси: x = влево/вправо, y = вверх/вниз (триггеры)
        x_axis = joy.x
        # Кнопки: 0=A, 1=B, 2=X, 3=Y (стандарт SDL)
        buttons = joy.buttons

        return {
            'left': x_axis < -0.5,
            'right': x_axis > 0.5,
            'rotate': len(buttons) > 2 and buttons[2],  # X
            'drop': len(buttons) > 0 and buttons[0]     # A
        }

    def on_joybutton_press(self, joystick, button):
        pass

    def on_joybutton_release(self, joystick, button):
        pass

    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        pass