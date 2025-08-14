import lvgl as lv, urequests, ujson, gc
from weather_converter import weathercode_to_text, weathercode_to_symbol

def setup_weather_tile(parent, fonts, latitude=53.7628, longitude=-2.7045):
    """
    Build weather UI on `parent`.  `fonts` = {"temp", "cond", "symbol"}.
    """
    # Title
    title = lv.label(parent)
    title.set_text("Weather")
    title.align(lv.ALIGN.CENTER, 0, -100)        

    # Labels
    labels = {}
    labels["temp"] = lv.label(parent)
    labels["temp"].set_style_text_font(fonts["temp"],0)
    

    labels["cond"] = lv.label(parent)
    labels["cond"].set_style_text_font(fonts["cond"],0)
    

    labels["symbol"] = lv.label(parent)
    labels["symbol"].set_style_text_font(fonts["symbol"],0)
    

    # Details
    offs = [-20,0,20]
    for i, key in enumerate(["wind","rain","uv","humidity"]):
        lbl = lv.label(parent)
        labels[key] = lbl

    def _update(timer=None):
        try:
            url = (
                "http://api.open-meteo.com/v1/forecast?"
                f"latitude={latitude}&longitude={longitude}"
                "&daily=uv_index_max,precipitation_probability_max"
                "&current=weather_code,temperature_2m,relative_humidity_2m,wind_speed_10m"
                "&timezone=GMT&wind_speed_unit=mph"
            )
            r = urequests.get(url)
            d = ujson.loads(r.text); r.close()

            labels["temp"].set_text(f"{d['current']['temperature_2m']}°C")
            labels["temp"].align(lv.ALIGN.CENTER, 0, 70)
            
            code = d["current"]["weather_code"]
            
            labels["cond"].set_text(weathercode_to_text.get(code, "N/A"))
            labels["cond"].align(lv.ALIGN.CENTER, 0, -70)
            
            labels["symbol"].set_text(weathercode_to_symbol.get(code, "?"))
            labels["symbol"].align(lv.ALIGN.CENTER, 0, 0)
            
            labels["wind"].set_pos(5, 90)
            labels["wind"].set_text(f"Wind: {d['current']['wind_speed_10m']}mph")
            
            labels["rain"].set_pos(5, 75)
            labels["rain"].set_text(f"Rain: {d['daily']['precipitation_probability_max'][0]}%")
            
            labels["uv"].set_pos(5, 105)
            labels["uv"].set_text(f"UV: {d['daily']['uv_index_max'][0]}")
            
            labels["humidity"].set_pos(5, 120)
            labels["humidity"].set_text(f"Hum: {d['current']['relative_humidity_2m']}%")
            gc.collect()
        except Exception as e:
            print("Weather error:", e)

    _update()
    lv.timer_create(_update, 300_000, None)

    return labels
