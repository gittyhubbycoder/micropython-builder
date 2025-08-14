import lvgl as lv, gc, time

def setup_monitor(parent, wlan):
    """
    Show free RAM, uptime, RSSI on `parent`.
    """
    mem = lv.label(parent); mem.set_pos(10,20)
    up  = lv.label(parent); up.set_pos(10,50)
    rssi= lv.label(parent); rssi.set_pos(10,80)

    def _update(timer):
        gc.collect()
        mem.set_text(f"RAM: {gc.mem_free()} B")
        up.set_text(f"Up: {time.ticks_ms()//1000}s")
        try:
            r = wlan.status("rssi")
        except:
            r = "N/A"
        rssi.set_text(f"RSSI: {r}")

    lv.timer_create(_update, 1000, None)
    gc.collect()
