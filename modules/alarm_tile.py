import lvgl as lv, ujson, gc, time

def setup_alarm_tab(tab, alarm_file, show_popup, gc_threshold=5000):
    # State
    alarms = []

    # File I/O
    def load_alarms():
        nonlocal alarms
        try:
            with open(alarm_file, "r") as f:
                alarms = ujson.load(f)
        except:
            alarms = []

    def save_alarms():
        try:
            with open(alarm_file, "w") as f:
                ujson.dump(alarms, f)
        except:
            pass

    # UI Elements
    hr = lv.roller(tab)
    hr.set_options("\n".join(f"{i:02d}" for i in range(24)), lv.roller.MODE.NORMAL)
    hr.align(lv.ALIGN.LEFT_MID, 20, -15)

    mn = lv.roller(tab)
    mn.set_options("\n".join(f"{i:02d}" for i in range(60)), lv.roller.MODE.NORMAL)
    mn.align(lv.ALIGN.CENTER, -5, -15)

    dy = lv.roller(tab)
    dy.set_options("Mon\nTue\nWed\nThu\nFri\nSat\nSun", lv.roller.MODE.NORMAL)
    dy.align(lv.ALIGN.RIGHT_MID, -15, -15)

    btn = lv.btn(tab)
    lv.label(btn).set_text("Add")
    btn.align(lv.ALIGN.BOTTOM_MID, 0, 5)

    lst = lv.obj(tab)
    lst.set_size(300,100)
    lst.align(lv.ALIGN.BOTTOM_MID, 0, 120)
    lst.add_flag(lv.obj.FLAG.SCROLLABLE)
    lst.set_scroll_dir(lv.DIR.VER)

    # Refresh list
    def refresh():
        lst.clean()
        for i, (h, m, d) in enumerate(alarms):
            row = lv.obj(lst); row.set_size(280,40)
            lbl = lv.label(row)
            lbl.set_text(f"{d} {h:02d}:{m:02d}")
            lbl.align(lv.ALIGN.LEFT_MID, 0, 0)
            dbtn = lv.btn(row); dbtn.set_size(24,24)
            dbtn.align(lv.ALIGN.RIGHT_MID, -2,0)
            lv.label(dbtn).set_text("X")
            def _del(e, idx=i):
                alarms.pop(idx); save_alarms(); refresh()
            dbtn.add_event_cb(_del, lv.EVENT.CLICKED, None)
        gc.collect()

    # Add callback
    def _add(e):
        gc.collect()

        # Hour roller → use a clean buffer
        buf_hr = bytearray(10)
        hr.get_selected_str(buf_hr, len(buf_hr))
        raw_hr = buf_hr.decode().replace('\x00', '').strip()

        # Minute roller → separate buffer
        buf_mn = bytearray(10)
        mn.get_selected_str(buf_mn, len(buf_mn))
        raw_mn = buf_mn.decode().replace('\x00', '').strip()

        # Day roller → separate buffer
        buf_day = bytearray(10)
        dy.get_selected_str(buf_day, len(buf_day))
        day = buf_day.decode().replace('\x00', '').strip()

        # Validate and convert
        if raw_hr.isdigit() and raw_mn.isdigit() and day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            hh = int(raw_hr)
            mm = int(raw_mn)
            alarms.append((hh, mm, day))
            print(f"✅ Alarm added: {day} {hh:02d}:{mm:02d}")
            save_alarms(); refresh()
        else:
            print("❌ Invalid roller input — alarm not added.")

    btn.add_event_cb(_add, lv.EVENT.CLICKED, None)

    # Check alarms
    def _check(tmr):
        tm = time.localtime()
        cd = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][tm[6]]
        for h,mn_,d in alarms:
            if h==tm[3] and mn_==tm[4] and d==cd:
                if gc.mem_free()>gc_threshold:
                    show_popup(f"Alarm: {d} {h:02d}:{mn_:02d}")

    lv.timer_create(_check, 60000, None)

    # Init
    load_alarms(); refresh(); gc.collect()
    return alarms
