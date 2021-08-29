import time

def test_func(a, b):
    BXE.ui.text_box("test {0} {1}".format(a, b))
    temp = BXE.audio.play_sfx("beep-221.wav")
    BXE.database.put("test", "teststring")
    print(BXE.database.get("test"))
    BXE.database.remove("test")
    BXE.database.put("test2", "teststring")
    print(BXE.path)
    print(BXE.dir)
    print(BXE.resource.load_raw("README.md", rootdir=True))
    rsrc = BXE.resource.load_image("common/arrow_backward.png", rootdir=True)
    overlay = BXE.overlay.insert_overlay(rsrc, (50, 50), (400, 400))
    time.sleep(2)
    BXE.overlay.rescale_overlay(overlay, (300, 300))
