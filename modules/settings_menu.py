import lvgl as lv, gc
from network_utils import connect_wifi
from time_utils import sync_rtc

settings_screen = None

def open_settings(home_scr, settings, pwm):
    """
    Build & show settings screen.
    """
    global settings_screen
    try:
        settings_screen.delete()
    except:
        pass

    settings_screen = lv.obj()
    scroll = lv.obj(settings_screen)
    scroll.set_size(320,240)
    scroll.add_flag(lv.obj.FLAG.SCROLLABLE)
    scroll.set_scroll_dir(lv.DIR.VER)
    scroll.set_style_pad_all(10,0)

    y = 10
    def add_heading(txt):
        nonlocal y
        lbl = lv.label(scroll)
        lbl.set_text(txt)
        lbl.set_style_text_font(lv.font_montserrat_16,0)
        lbl.set_x(0); lbl.set_y(y)
        y += 24

    def add_text_area(placeholder, key):
        nonlocal y
        ta = lv.textarea(scroll)
        ta.set_placeholder_text(placeholder)
        ta.set_size(300,30)
        ta.set_x(0); ta.set_y(y)
        def _on_change(evt):
            settings[key] = ta.get_text()
        ta.add_event_cb(_on_change, lv.EVENT.VALUE_CHANGED, None)
        y += 40
        return ta

    def add_switch(label, key):
        nonlocal y
        l = lv.label(scroll); l.set_text(label); l.set_x(10); l.set_y(y+5)
        sw = lv.switch(scroll); sw.set_x(250); sw.set_y(y)
        if settings.get(key):
            sw.add_state(lv.STATE.CHECKED)
        def _toggle(evt):
            settings[key] = sw.has_state(lv.STATE.CHECKED)
        sw.add_event_cb(_toggle, lv.EVENT.VALUE_CHANGED, None)
        y += 40
        return sw

    add_heading("Network")
    add_text_area("SSID",      "ssid")
    add_text_area("Password",  "password")

    add_heading("Display")
    # Brightness slider
    sl = lv.slider(scroll)
    sl.set_size(250,20)
    sl.set_x(10); sl.set_y(y)
    sl.set_value(settings["brightness"], lv.ANIM.OFF)
    def _slide(evt):
        v = sl.get_value()
        pwm.duty(int(v * 1023 / 100))
        settings["brightness"] = v
    sl.add_event_cb(_slide, lv.EVENT.VALUE_CHANGED, None)
    y += 50

    add_switch("Use BST", "use_bst")

    # Exit button
    btn = lv.btn(settings_screen)
    btn.align(lv.ALIGN.TOP_RIGHT, -10, 10)
    lv.label(btn).set_text("X")
    def _exit(evt):
        lv.scr_load(home_scr)
        connect_wifi(settings["ssid"], settings["password"])
        sync_rtc(settings["use_bst"])
        settings_screen.delete()
        gc.collect()
    btn.add_event_cb(_exit, lv.EVENT.CLICKED, None)

    lv.scr_load(settings_screen)
    gc.collect()
