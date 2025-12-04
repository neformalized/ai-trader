import numpy

numpy.set_printoptions(suppress = True, precision = 2)

#

class Buffer:
    
    def __init__(self, size_raw, candles, indicators, ignores):
        
        self.size_raw = size_raw
        self.matrix_raw = numpy.zeros((len(candles), self.size_raw), numpy.float32)
        
        self.indicators = indicators
        
        self.matrix_indicators = {}
        self.matrix_indicator_tmp = {}
        
        self.create_matrix_indicators()
        
        self.matrix_map = candles
        
        self.matrix_map_ignore_normalization = ignores
    #
    
    def push(self, history):
        
        for i, row in enumerate(history):
            
            self.matrix_raw[:,i] = row
        #
    #
    
    def calculate(self):
        
        for indicator in self.indicators:
            
            if indicator["type"] == "sma":
                
                self.sma(indicator["name"], indicator["size"], indicator["period"])
            #
            
            if indicator["type"] == "bollinger":
                
                self.bollinger(indicator["name"], indicator["size"], indicator["period"], indicator["k"])
            #
            
            if indicator["type"] == "ema":
                
                self.ema(indicator["name"], indicator["size"], indicator["period"], indicator["start"])
            #
            
            if indicator["type"] == "rsi":
                
                self.rsi(indicator["name"], indicator["size"], indicator["period"])
            #
        #
    #
    
    def take(self, cut):
        
        response = {}
        
        for key in self.matrix_map:
            
            response[key] = self.matrix_raw[self.matrix_map.index(key)][-cut:].tolist()
        #
        
        for indicator in self.indicators:
            
            if "bollinger" in indicator["type"]:
                
                response[indicator["name"] + " upper"] = self.matrix_indicators[indicator["name"] + " upper"][-cut:].tolist()
                response[indicator["name"] + " lower"] = self.matrix_indicators[indicator["name"] + " lower"][-cut:].tolist()
                
                continue
            #
            
            response[indicator["name"]] = self.matrix_indicators[indicator["name"]][-cut:].tolist()
        #
        
        return response
    #
    
    def take_normalized(self, cut):
        
        maximum = self.matrix_raw[self.matrix_map.index("High")][-cut:].max()
        minimum = self.matrix_raw[self.matrix_map.index("Low")][-cut:].min()
        
        #
        
        minmax_map = ["Open", "High", "Low", "Close"]
        
        #
        
        response = {}
        
        #
        
        for key in self.matrix_map:
            
            if key in self.matrix_map_ignore_normalization:
                
                response[key] = self.matrix_raw[self.matrix_map.index(key)][-cut:].tolist()
                
                continue
            #
            
            if key in minmax_map:
                
                response[key] = ((self.matrix_raw[self.matrix_map.index(key)][-cut:] - minimum)/(maximum - minimum)).tolist()
            else:
                
                response[key] = ( self.matrix_raw[self.matrix_map.index(key)][-cut:] / self.matrix_raw[self.matrix_map.index(key)][-cut:].max() ).tolist()
            #
        #
        
        for indicator in self.indicators:
            
            if indicator["norm"]:
                
                if indicator["type"] == "bollinger":
                    
                    response[indicator["name"] + " upper"] = ((self.matrix_indicators[indicator["name"] + " upper"][-cut:] - minimum)/(maximum - minimum)).tolist()
                    response[indicator["name"] + " lower"] = ((self.matrix_indicators[indicator["name"] + " lower"][-cut:] - minimum)/(maximum - minimum)).tolist()
                    
                    continue
                #
                
                response[indicator["name"]] = ((self.matrix_indicators[indicator["name"]][-cut:] - minimum)/(maximum - minimum)).tolist()
                
            else:
                
                if indicator["type"] == "rsi":
                    
                    response[indicator["name"]] = (self.matrix_indicators[indicator["name"]][-cut:]).tolist()
                    
                    continue
                #
                
                response[indicator["name"]] = (self.matrix_indicators[indicator["name"]][-cut:] / self.matrix_indicators[indicator["name"]][-cut:].max()).tolist()
            #
        #
        
        return response
    #
    
    def create_matrix_indicators(self):
        
        for indicator in self.indicators:
            
            if indicator["type"] == "sma":
                
                self.create_sma(indicator["name"], indicator["size"])
            #
            
            if indicator["type"] == "bollinger":
                
                self.create_bollinger(indicator["name"], indicator["size"], indicator["period"])
            #
            
            if indicator["type"] == "ema":
                
                self.create_sma(indicator["name"], indicator["size"])
            #
            
            if indicator["type"] == "rsi":
                
                self.create_rsi(indicator["name"], indicator["size"])
            #
        #
    #
    
    ### BUFFERS INIT
    
    def create_sma(self, name, size):
        
        self.matrix_indicators[name] = numpy.zeros(size, numpy.float32)
    #
    
    def create_bollinger(self, name, size, period):
        
        self.matrix_indicators[name + " upper"] = numpy.zeros(size, numpy.float32)
        self.matrix_indicators[name + " lower"] = numpy.zeros(size, numpy.float32)
        
        self.matrix_indicator_tmp[name] = numpy.zeros(period, numpy.float32)
    #
    
    def create_ema(self, name, size):
        
        self.matrix_indicators[name] = numpy.zeros(size, numpy.float32)
    #
    
    def create_rsi(self, name, size):
        
        self.matrix_indicators[name] = numpy.zeros(size, numpy.float32)
    #
    
    ### BUFFERS CALCULATE
    
    def bollinger(self, name, size, period, k):
        
        for i in reversed(range(size)):
            
            start = self.size_raw - period - i
            end = self.size_raw - i
            
            mean = self.matrix_raw[self.matrix_map.index("Close")][start:end].mean()
            
            self.matrix_indicator_tmp[name] = (self.matrix_raw[self.matrix_map.index("Close")][start:end] - mean) ** 2
            
            std = self.matrix_indicator_tmp[name].mean() ** 0.5
            
            self.matrix_indicators[name + " upper"][abs(i - size + 1)] = mean + (k * std)
            self.matrix_indicators[name + " lower"][abs(i - size + 1)] = mean - (k * std)
        #
    #
    
    def sma(self, name, size, period):
        
        for i in reversed(range(size)):
            
            start = self.size_raw - period - i
            end = self.size_raw - i

            self.matrix_indicators[name][abs(i - size + 1)] = self.matrix_raw[self.matrix_map.index("Close")][start:end].mean()
        #
    #
    
    def ema(self, name, size, period, start):
        
        alpha = 2 / (period + 1)
        
        #
        
        last_ema = self.matrix_raw[self.matrix_map.index("Close")][-start:-start+period].mean()
        
        #
        
        for i in reversed(range(1, start-period + 1)):
            
            last_ema = (self.matrix_raw[self.matrix_map.index("Close")][-i] - last_ema) * alpha + last_ema
            
            if size - i >= 0:
                
                self.matrix_indicators[name][size - i] = last_ema
            #
        #
    #
    
    def rsi(self, name, size, period):
        
        for i in reversed(range(size)):
            
            #
            
            start = self.size_raw - period - i
            end = self.size_raw - i
            
            index = abs(i - size + 1)
            
            #
            
            positives = []
            negatives = []
            
            for j in range(start, end):
                
                delta = self.matrix_raw[self.matrix_map.index("Close")][j] - self.matrix_raw[self.matrix_map.index("Close")][j-1]
                
                #
                
                if delta >= 0.0: positives.append(delta)
                else: negatives.append(abs(delta))
            #
            
            ### Rare case
            
            if(len(positives) == 0 and len(negatives) > 0):
                
                self.matrix_indicators[name][index] = 0.0
                continue
            #
            
            if(len(positives) > 0 and len(negatives) == 0):
                
                self.matrix_indicators[name][index] = 100.0
                continue
            #
            
            if(len(positives) == 0 and len(negatives) == 0):
            
                self.matrix_indicators[name][index] = 50.0
                continue
            #
            
            ### Usual case
            
            gains = sum(positives)/period
            losses = sum(negatives)/period
            
            #
            
            rs = gains/losses
            
            #
            
            rsi = 100 - (100/(1 + rs))
            
            #
            
            self.matrix_indicators[name][index] = rsi
        #
    #
#