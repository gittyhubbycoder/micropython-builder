import network, gc

def connect_wifi(ssid, password, timeout=15):
    """
    Connect to Wi-Fi and return the WLAN object.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass

    print("Wi-Fi status:", wlan.ifconfig() if wlan.isconnected() else "Failed")
    gc.collect()
    return wlan
