class Wallet:
    
    def __init__(self, fee = 0.1):
        
        self.fee = fee/100
        
        self.deals = list()
        self.log = list()
    #
    
    def check_deals(self, price):
        
        if not self.count_deals(): return
        
        #
        
        for deal in self.deals[:]:
            
            _price = price if deal["params"]["type"] == "buy" else (1 / price)
            
            #
            
            if _price <= deal["sl"] or _price >= deal["tp"]:
                
                self.close_deal(_price, deal)
                
                self.deals.remove(deal)
                
                continue
            #
        #
    #
    
    def open_deal(self, price, stop_loss, take_profit, params):
        
        sl = stop_loss/100
        tp = take_profit/100
        
        deal = {
            "price": price,
            "sl": price - price * sl,
            "tp": price + price * tp,
            "params": params
        }
        
        self.deals.append(deal)
    #
    
    def close_deal(self, price_close, deal):
        
        pnl = (price_close - deal["price"]) / deal["price"]
        
        log = {
            "pnl": (pnl - self.fee * 2) * 100,
            "confidence": deal["params"]["confidence"],
            "type": deal["params"]["type"],
            "conclusion": deal["params"]["conclusion"],
        }
        
        self.log.append(log)
    #
    
    def statistic(self):
        
        if not len(self.log):
            
            return {
                "total": 0,
                "avg": 0.0,
                "winrate": 0.0
            }
        #
        
        win = 0
        pnls = list()
        
        for deal in self.log:
            
            if deal["pnl"] > 0.0: win += 1
            
            pnls.append(deal["pnl"])
        #
        
        avg = round(sum(pnls)/len(pnls), 2)
        
        winrate = 0 if win == 0 else round(win/len(self.log), 2) * 100
        
        return {
            "total": len(self.log),
            "avg": avg,
            "winrate": winrate,
        }
    #
    
    def get_close_deals(self):
        
        if not len(self.log): return False
        
        #
        
        output = ""
        
        for deal in self.log:
            
            output += f'{round(deal["pnl"], 2)}%|{deal["type"]}|{deal["conclusion"]}\n'
        #
        
        output = output[:-1] + "(last deal)\n"
        
        return output
    #
    
    def count_deals(self):
        
        return len(self.deals)
    #
#