import lvgl as lv, time, gc


def setup_stopwatch_tab(tab, montserrat_28):
    lbl = lv.label(tab)
    lbl.set_text("00:00.0")
    lbl.align(lv.ALIGN.CENTER, 0, -30)
    lbl.set_style_text_font(montserrat_28,0)

    state = {"running": False, "start": 0}

    btn = lv.btn(tab); lv.label(btn).set_text("Start/Stop")
    btn.align(lv.ALIGN.CENTER, 0, 40)
    def _toggle(evt):
        if not state["running"]:
            state["start"] = time.ticks_ms()
        state["running"] = not state["running"]
        gc.collect()
    btn.add_event_cb(_toggle, lv.EVENT.CLICKED, None)

    def _update(tmr):
        if state["running"]:
            dt = time.ticks_diff(time.ticks_ms(), state["start"])
            s = dt//1000; t = (dt%1000)//100
            lbl.set_text(f"{s//60:02d}:{s%60:02d}.{t}")
    lv.timer_create(_update, 100, None)
    gc.collect()
