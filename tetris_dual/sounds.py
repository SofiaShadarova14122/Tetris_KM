import arcade
from .config import SOUND_DROP, SOUND_ROTATE, SOUND_LINE_CLEAR, SOUNDS_ENABLED

_sounds_enabled = SOUNDS_ENABLED
_drop_sound = None
_rotate_sound = None
_line_clear_sound = None

def _load_sound(path):
    try:
        return arcade.load_sound(path)
    except:
        print(f"Не удалось загрузить звук: {path}")
        return None

def set_sounds_enabled(enabled):
    global _sounds_enabled
    _sounds_enabled = enabled

def is_sounds_enabled():
    return _sounds_enabled

def play_drop():
    if not _sounds_enabled: return
    global _drop_sound
    if _drop_sound is None: _drop_sound = _load_sound(SOUND_DROP)
    if _drop_sound: arcade.play_sound(_drop_sound, volume=0.5)

def play_rotate():
    if not _sounds_enabled: return
    global _rotate_sound
    if _rotate_sound is None: _rotate_sound = _load_sound(SOUND_ROTATE)
    if _rotate_sound: arcade.play_sound(_rotate_sound, volume=0.4)

def play_line_clear():
    if not _sounds_enabled: return
    global _line_clear_sound
    if _line_clear_sound is None: _line_clear_sound = _load_sound(SOUND_LINE_CLEAR)
    if _line_clear_sound: arcade.play_sound(_line_clear_sound, volume=0.6)