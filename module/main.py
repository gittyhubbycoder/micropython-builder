import lvgl as lv, machine, fs_driver, display_driver, gc

from network_utils    import connect_wifi
from time_utils       import sync_rtc, start_clock_update
from settings_menu    import open_settings
from weather_tile     import setup_weather_tile
from news_tile        import setup_news_tile
from facts_tile       import setup_facts_tile
from monitor_tille     import setup_monitor
from alarm_tile       import setup_alarm_tab
from stopwatch_tile   import setup_stopwatch_tab
from timer_tile       import setup_timer_tab

#–– Settings & Backlight ––
ALARM_FILE = "alarms.json"
settings = {
    "ssid":"EE-M6CXC5","password":"ApKpJtf4CmQh6r",
    "brightness":100,"use_bst":True
}
pwm = machine.PWM(machine.Pin(21), freq=1000)
pwm.duty(int(settings["brightness"]*1023/100))

#–– Connect + Sync ––
wlan = connect_wifi(settings["ssid"], settings["password"])
sync_rtc(settings["use_bst"])

gc.collect()

# Register filesystem
fs_drv = lv.fs_drv_t()
fs_driver.fs_register(fs_drv, "S")  # "S" is your drive prefix

# Load fonts
montserrat_24 = lv.font_load("S:fonts/montserrat_24.bin")
montserrat_28 = lv.font_load("S:fonts/montserrat_28.bin")
montserrat_32 = lv.font_load("S:fonts/montserrat_32.bin")
weather_fonts_52 = lv.font_load("S:fonts/weather_fonts_52.bin")
LCD_font = lv.font_load("S:fonts/LCD_Font_120.bin")


#–– Build Screen & TileView ––
scr = lv.scr_act()
scr.set_style_bg_color(lv.color_white(), lv.PART.MAIN)
tv  = lv.tileview(scr)

#–– Home Tile ––
home = tv.add_tile(0,0,lv.DIR.RIGHT)
lbl_time = lv.label(home); lbl_time.set_style_text_font(LCD_font,0); lbl_time.center()
lbl_date = lv.label(home); lbl_date.set_pos(120, 180)
btn_set  = lv.btn(home)
lv.label(btn_set).set_text(lv.SYMBOL.SETTINGS)
btn_set.set_pos(270, 5)
btn_set.add_event_cb(lambda e: open_settings(scr, settings, pwm), lv.EVENT.CLICKED,None)
start_clock_update(lbl_time, lbl_date)

#–– Weather Tile ––
w_tile = tv.add_tile(1,0,lv.DIR.LEFT|lv.DIR.RIGHT)
weather_labels = setup_weather_tile(
    w_tile,
    {"temp":montserrat_32,"cond":montserrat_28,"symbol":weather_fonts_52}
)

#–– News Tile ––
n_tile = tv.add_tile(2,0,lv.DIR.LEFT|lv.DIR.RIGHT)
setup_news_tile(n_tile, "http://dadesktopwidget.atwebpages.com/bbc.json", scr)

#–– Facts Tile ––
f_tile = tv.add_tile(3,0,lv.DIR.LEFT|lv.DIR.RIGHT)
setup_facts_tile(f_tile, "http://dadesktopwidget.atwebpages.com/deploy/facts.json", scr)

#–– Alarm/Stopwatch/Timer Tile ––
t_tile = tv.add_tile(4,0,lv.DIR.LEFT|lv.DIR.RIGHT)
tab = lv.tabview(t_tile, lv.DIR.TOP, 50)
tab_alarms    = tab.add_tab("Alarms")
tab_stopwatch = tab.add_tab("Stopwatch")
tab_timer     = tab.add_tab("Timer")

# Precreate hidden popup

def show_alarm_popup(msg):
    popup = lv.msgbox(lv.scr_act(), "Alert", msg, "", True)
    popup.set_size(200,100); popup.center()
    def on_close(evt):
        nonlocal popup
        try:
            popup.add_flag(lv.obj.FLAG.HIDDEN)
            popup = None
        except:
            pass

    popup.add_event_cb(on_close, lv.EVENT.DELETE, None)


# Lazy-load tabs
def on_tab_change(evt):
    idx = tabview.get_tab_act()

    if idx == 0 and not hasattr(tabview, "_alarm_built"):
        setup_alarm_tab(tab_alarms, ALARM_FILE, show_alarm_popup)
        tabview._alarm_built = True

    elif idx == 1 and not hasattr(tabview, "_stopwatch_built"):
        setup_stopwatch_tab(tab_stopwatch, montserrat_28)
        tabview._stopwatch_built = True

    elif idx == 2 and not hasattr(tabview, "_timer_built"):
        setup_timer_tab(tab_timer, show_alarm_popup)
        tabview._timer_built = True

setup_alarm_tab(tab_alarms, ALARM_FILE, show_alarm_popup)
setup_stopwatch_tab(tab_stopwatch, montserrat_28)
setup_timer_tab(tab_timer, show_alarm_popup)
#tab.add_event_cb(on_tab_change, lv.EVENT.VALUE_CHANGED, None)

#–– Monitor Tile ––
m_tile = tv.add_tile(5,0,lv.DIR.LEFT)
setup_monitor(m_tile, wlan)

gc.collect()
print("Free RAM:", gc.mem_free())
