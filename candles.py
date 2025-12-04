from binance.client import Client

class Candles:
    
    def __init__(self):
        
        self.client = Client()
    #
    
    def get(self, symbol, frame, limit):
        
        #
        
        interval = Client.KLINE_INTERVAL_1MINUTE
        
        if frame == "1m": interval = Client.KLINE_INTERVAL_1MINUTE
        if frame == "3m": interval = Client.KLINE_INTERVAL_3MINUTE
        if frame == "5m": interval = Client.KLINE_INTERVAL_5MINUTE
        if frame == "15m": interval = Client.KLINE_INTERVAL_15MINUTE
        if frame == "30m": interval = Client.KLINE_INTERVAL_30MINUTE
        if frame == "1h": interval = Client.KLINE_INTERVAL_1HOUR
        if frame == "2h": interval = Client.KLINE_INTERVAL_2HOUR
        if frame == "4h": interval = Client.KLINE_INTERVAL_4HOUR
        if frame == "6h": interval = Client.KLINE_INTERVAL_6HOUR
        if frame == "8h": interval = Client.KLINE_INTERVAL_8HOUR
        if frame == "12h": interval = Client.KLINE_INTERVAL_12HOUR
        if frame == "1d": interval = Client.KLINE_INTERVAL_1DAY
        
        #
        
        return self.client.get_klines(symbol = symbol, interval = interval, limit = limit)
    #
#