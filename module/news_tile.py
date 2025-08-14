import lvgl as lv, urequests, ujson, gc

def setup_news_tile(parent, url, scr, max_items=5):

    """
    Fetch JSON `{ titles: [...] }`, display as scrollable cards.
    """
    def _clean():
        while parent.get_child_cnt():
            parent.get_child(0).delete()

    def _update(timer=None):
        _clean(); gc.collect()
        try:
            r = urequests.get(url)
            data = ujson.loads(r.text); r.close()
            items = data.get("titles", [])[1:1+max_items]
        except:
            items = ["Error loading news"]

        cont = lv.obj(parent)
        cont.set_size(320, 200)
        cont.align(lv.ALIGN.BOTTOM_MID, 0, 0)
        cont.add_flag(lv.obj.FLAG.SCROLLABLE)
        cont.set_scroll_dir(lv.DIR.VER)

        y_offset = 0
        CARD_HEIGHT = 80
        for title in items:
            # 🧊 Create a card-like container
            card = lv.obj(cont)
            card.set_size(300, CARD_HEIGHT)
            card.set_align(lv.ALIGN.TOP_MID)
            card.set_y(y_offset)
            card.set_style_radius(5, 0)
            card.set_style_bg_color(lv.color_hex(0xf0f0f0), 0)
            card.set_style_pad_all(6, 0)
            
            # 📰 Add label inside the card
            lbl = lv.label(card)
            lbl.set_text(title[9:-3].strip())
            scr.update_layout()
            card_width = card.get_width()
            lbl.set_long_mode(lv.label.LONG.WRAP)
            lbl.set_width(card_width - 16)
            scr.update_layout()
            card.set_height(lbl.get_height() + 25)
            scr.update_layout()# leave room for padding
            CARD_HEIGHT = card.get_height()
            lbl.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            
            
            y_offset += CARD_HEIGHT + 10

        gc.collect()

    _update()
    label = lv.label(parent)
    label.set_text("News")
    label.align(lv.ALIGN.CENTER, 0, -100)
    lv.timer_create(_update, 300_000, None)
