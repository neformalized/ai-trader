import candles, buffer, history, ai, wallet
import time

#

window = 8

#

step_timeout = 20

#

max_deals = 1

stop_loss = 0.2
take_profit = 0.5

# Open, High, Low, Close are necessary!!!
candles = ["Open time", "Open", "High", "Low", "Close", "Volume", "Close time", "Quote", "Trade", "Buy base", "Buy quote", "Ignore"]
ignores = ["Open time", "Close time", "Ignore", "Quote", "Trade", "Buy base", "Buy quote"]

indicators = [
    {"type": "sma", "name": "sma99", "size": window, "period": 99, "norm": True, "description": "SMA : period 99"},    
    {"type": "sma", "name": "sma7", "size": window, "period": 7, "norm": True, "description": "SMA : period 7"},
    {"type": "ema", "name": "ema5.50", "size": window, "period": 5, "start": 50, "norm": True, "description": "EMA : period 5 : start index -50"},
    {"type": "bollinger", "name": "bollinger14.2", "size": window, "period": 14, "k": 2, "norm": True, "description": "BOLLINGER : period 14 : k 2"},
    {"type": "rsi", "name": "rsi5", "size": window, "period": 5, "norm": False, "description": "RSI - period 5"},
    {"type": "rsi", "name": "rsi21", "size": window, "period": 21, "norm": False, "description": "RSI - period 21"}
]

#

indicators_desc = dict()
for indicator in indicators: indicators_desc[indicator["name"]] = indicator["description"]

#

buf = buffer.Buffer(120, candles, indicators, ignores)

#

#client = candles.Candles()
historical = history.History("C:\\Users\\omni\\Desktop\\history\\m\\", "C:\\Users\\omni\\Desktop\\history\\s\\", 121, 120)

#

agent = ai.Trader()
wallet = wallet.Wallet()

#

current_step = step_timeout

start = time.time()
while True:
    
    print(historical.end_primary, historical.len_primary)
    #response = client.get("BTCUSDT", "1m", 120)
    
    if current_step < step_timeout:
        
        method = True
        current_step += 1
    else:
        
        method = False
        current_step = 1
    #
    
    #
    
    response = historical.step(method)
    if not response: break
    
    #
    
    wallet.check_deals(response["price"])
    
    #
    
    if method or wallet.count_deals() == max_deals: continue
    if abs(historical.end_primary - historical.start_primary) == 1: continue
    
    #
    
    stats = wallet.statistic()
    deals = wallet.get_close_deals()
    
    agent.build_system_prompt(
        {
            "statistic": {
                "deals": "No deals yet" if not deals else deals,
                "avg": stats["avg"],
                "deals_count": stats["total"],
                "winrate": round(stats["winrate"], 2)
            }
        }
    )
    
    #
    
    buf.push(response["candles"])
    buf.calculate()
    
    #
    
    agent.build_user_prompt(
        {
            "frame": buf.take(window),
            "exclude": candles,
            "indicator": indicators_desc,
            "last": abs(historical.end_primary - historical.start_primary)
        }
    )
    
    #
    
    print(agent.messages[0]["content"])
    #print(agent.messages[1]["content"])
    
    agent.show_usage()
    
    signal = agent.ask()
    
    if signal["type"] == "signal":
        
        price = response["price"] if signal["deal"] == "buy" else (1 / response["price"])
        
        wallet.open_deal(price, stop_loss, take_profit, {"type": signal["deal"], "conclusion": signal["conclusion"], "confidence": signal["confidence"]})
        
        #input("enter to continue:")
    #
#
end = time.time() - start

print(f"walked in {end} sec")
print(f"walked in {end / 60} min")
#agent.total_price()

with open("log.txt", "w") as f:
    
    stats = wallet.statistic()
    
    for key in stats.keys():
        
        stat = f"{key}: {stats[key]}"
        f.write(stat + "\n")
        print(stat)
    #
    
    print("")
    
    deals = wallet.get_close_deals()
    
    f.write(deals)
    print(deals)
#