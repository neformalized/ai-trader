import os

class History:
    
    def __init__(self, path_minutes, path_seconds, shift, window):
        
        self.size = 12
        
        #
        
        self.shift = shift
        self.window = window
        
        #
        
        self.timeframe = {
            "primary" : self.generate(),
            "secondary" : self.generate()
        }
        
        #
        
        self.push_history(path_seconds, "primary")
        self.len_primary = len(self.timeframe["primary"][0])
        
        self.push_history(path_minutes, "secondary")
        self.len_secondary = len(self.timeframe["secondary"][0])
        
        #print(f'primary:{self.len_primary}')
        #print(f'secondary:{self.len_secondary}')
        
        #
        
        self.scale = int(len(self.timeframe["primary"][0])/len(self.timeframe["secondary"][0]))
        
        #
        
        self.end_primary = int(self.shift * self.scale)
        self.end_secondary = self.shift
        
        self.start_primary = int(self.shift * self.scale)
        self.start_secondary = self.shift - self.window + 1
    #
    
    def generate(self):
        
        return [[] for i in range(self.size)]
    #
    
    def push_history(self, path, target):
        
        for period in os.listdir(path):
            
            with open(path + period, "r") as file:
                
                for line in file.readlines():
                    
                    candles = line.replace("\n", "").split(",")
                    
                    for i in range(self.size): self.timeframe[target][i].append(candles[i])
                #
            #
        #
    #
    
    def step(self, only_price = True):
        
        if self.end_primary == self.len_primary:
            
            return False
        #
        
        price = self.timeframe["primary"][4][self.end_primary]
        
        #
        
        candles = None if only_price else self.candles()
        
        #
        
        self.re_range()
        
        #
        
        return {"price": float(price), "candles": candles}
    #
    
    def candles(self):
        
        response = [list(row) for row in zip(*[self.timeframe["secondary"][i][self.start_secondary:self.end_secondary] for i in range(self.size)])]
        
        delta = self.end_primary - self.start_primary
        
        if delta == 0:
            
            candle = []
            
            for i in range(self.size):
                
                candle.append(self.timeframe["primary"][i][self.end_primary])
            #
            
            response.append(candle)
        #
        
        if delta > 0:
            
            response.append(self.unite())
        #
        
        return response
    #
    
    def unite(self):
        
        return [
            self.timeframe["primary"][0][self.start_primary],
            self.timeframe["primary"][1][self.start_primary],
            max(self.timeframe["primary"][2][self.start_primary: self.end_primary]),
            min(self.timeframe["primary"][3][self.start_primary: self.end_primary]),
            self.timeframe["primary"][4][self.end_primary],
            sum(map(float, self.timeframe["primary"][5][self.start_primary: self.end_primary])),
            self.timeframe["primary"][6][self.end_primary],
            sum(map(float, self.timeframe["primary"][7][self.start_primary: self.end_primary])),
            sum(map(float, self.timeframe["primary"][8][self.start_primary: self.end_primary])),
            sum(map(float, self.timeframe["primary"][9][self.start_primary: self.end_primary])),
            sum(map(float, self.timeframe["primary"][10][self.start_primary: self.end_primary])),
            sum(map(float, self.timeframe["primary"][11][self.start_primary: self.end_primary]))
        ]
    #
    
    def re_range(self):
        
        delta = self.end_primary - self.start_primary
        
        #
        
        self.end_primary += 1
        
        #
        
        if delta == self.scale:
            
            self.start_primary += self.scale
            
            self.start_secondary += 1
            self.end_secondary += 1
        #
    #
#