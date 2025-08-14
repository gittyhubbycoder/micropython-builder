import machine, time, ntptime, gc

def sync_rtc(use_bst):
    """
    Sync RTC via NTP and apply BST if requested.
    """
    try:
        ntptime.settime()
    except:
        pass
    offset = 3600 if use_bst else 0
    tm = time.localtime(time.time() + offset)
    machine.RTC().datetime((tm[0],tm[1],tm[2],tm[6],tm[3],tm[4],tm[5],0))
    print("RTC set to:", time.localtime())
    gc.collect()

def get_adjusted_time(use_bst):
    """
    Return localtime tuple with optional BST offset.
    """
    offset = 3600 if use_bst else 0
    return time.localtime(time.time() + offset)

def start_clock_update(label_time, label_date):
    """
    Update time/date labels every second.
    """
    import lvgl as lv

    def _update(timer):
        tm = time.localtime()
        label_time.set_text("{:02d}:{:02d}".format(tm[3], tm[4]))
        label_date.set_text("{} {:d}, {:04d}".format(
            ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][tm[1]-1],
            tm[2], tm[0]
        ))
        gc.collect()

    lv.timer_create(_update, 1000, None)
    gc.collect()
