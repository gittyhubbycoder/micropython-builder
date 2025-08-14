import lvgl as lv, time, gc

def setup_timer_tab(tab, show_popup, threshold=5000):
    r1 = lv.roller(tab); r1.set_options("\n".join(f"{i:02d}" for i in range(60)), lv.roller.MODE.NORMAL)
    r1.align(lv.ALIGN.CENTER, -60, -30)
    r2 = lv.roller(tab); r2.set_options(r1.get_options(), lv.roller.MODE.NORMAL)
    r2.align(lv.ALIGN.CENTER, 60, -30)

    lbl = lv.label(tab)
    lbl.align(lv.ALIGN.CENTER, 0, 20)
    lbl.set_text("")

    state = {"running": False, "target": 0, "start": 0}

    btn = lv.btn(tab); lv.label(btn).set_text("Start")
    btn.align(lv.ALIGN.CENTER, 0, 60)
    def _start(evt):
        gc.collect()

        # Use separate buffers for each roller
        buf_m = bytearray(10)
        r1.get_selected_str(buf_m, len(buf_m))
        raw_m = buf_m.decode().replace('\x00', '').strip()

        buf_s = bytearray(10)
        r2.get_selected_str(buf_s, len(buf_s))
        raw_s = buf_s.decode().replace('\x00', '').strip()

        # Validate and convert
        if raw_m.isdigit() and raw_s.isdigit():
            m = int(raw_m)
            s = int(raw_s)
            state["target"] = m * 60 + s
            state["start"] = time.ticks_ms()
            state["running"] = True
            print(f"⏱️ Timer started: {m:02d}:{s:02d}")
        else:
            print(f"❌ Invalid roller values: m={repr(raw_m)}, s={repr(raw_s)}")

        gc.collect()
    btn.add_event_cb(_start, lv.EVENT.CLICKED, None)

    def _update(tmr):
        if state["running"]:
            elapsed = time.ticks_diff(time.ticks_ms(), state["start"])//1000
            rem = max(0, state["target"] - elapsed)
            lbl.set_text(f"{rem//60:02d}:{rem%60:02d}")
            if rem == 0:
                state["running"] = False
                if gc.mem_free()>threshold:
                    show_popup("Time's up!")
    lv.timer_create(_update, 500, None)
    gc.collect()
