import time

def test_func(a, b):
    BXE.ui.text_box("test {0} {1}".format(a, b))
    temp = BXE.audio.play_sfx("beep-221.wav")
    BXE.audio.play_music("A_Travellers_Tale.oga")
    time.sleep(2)
    BXE.audio.stop_music()
