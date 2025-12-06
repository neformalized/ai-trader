import openai, json

#

class Trader:
    
    def __init__(self):
        
        self.tries = 5
        
        #
        
        self.model = "gpt-4.1-mini"
        self.model_price = [.15, .6]
        self.tokens = {"input": 0, "output": 0}
        
        #
        
        self.ai = openai.OpenAI()
        #self.ai = server.LLM_Remote("https://ad9febf4be40.ngrok-free.app/")
        
        #
        
        self.system = dict()
        
        parts = ["role", "output", "statistic"]
        
        for part in parts:
            
            with open(f"prompt/{part}.txt", "r", encoding="utf-8") as f:
                
                self.system[part] = f.read()
            #
        #
        
        self.messages = list()
        self.messages.append({"role": "system", "content": ""})
        self.messages.append({"role": "user", "content": ""})
    #
    
    def build_user_prompt(self, params):
        
        prompt = ""
        
        #
        
        prompt += "Basic info:\n"
        prompt += f"Seconds in current candle: {params['last']}\n"
       
        prompt += "\nCandles:\n"
        prompt += f"open: {[round(value, 2) for value in params['frame']['Open']]}\n"
        prompt += f"high: {[round(value, 2) for value in params['frame']['High']]}\n"
        prompt += f"low: {[round(value, 2) for value in params['frame']['Low']]}\n"
        prompt += f"close: {[round(value, 2) for value in params['frame']['Close']]}\n"
        prompt += f"volume: {[round(value, 2) for value in params['frame']['Volume']]}\n"
        
        prompt += "\nIndicators:\n"
        
        for key in params["frame"].keys():
            
            if key in params["exclude"]: continue
            
            if key in params["indicator"]: prompt += f"{params['indicator'][key]}: " + f"{[round(value, 2) for value in params['frame'][key]]}\n"
        #
        
        prompt += "\n"
        prompt += 'For answer ALWAYS use json schema {"type": "signal"} or {"type": "pass"} that is necessary for backend.'
        
        self.messages[1]["content"] = prompt
    #
    
    def build_system_prompt(self, params):
        
        prompt = ""
        
        #
        
        prompt += self.system["role"]
        
        prompt += self.system["output"]
        
        prompt += self.template_statistic(self.system["statistic"], params["statistic"])
        
        #
        
        self.messages[0]["content"] = prompt
    #
    
    def template_statistic(self, text, params):
        
        return text.format(**params)
    #
    
    def show_usage(self):
        
        price_input = round((self.tokens["input"]/1000000) * self.model_price[0], 2)
        price_output = round((self.tokens["output"]/1000000) * self.model_price[1], 2)
        price_total = round(price_input + price_output, 2)
        
        print(f'input tokens: {self.tokens["input"]} | {price_input}$')
        print(f'output tokens: {self.tokens["output"]} | {price_output}$')
        print(f'total tokens: {self.tokens["input"] + self.tokens["output"]} | {price_total}$')
    #
    
    def ask(self):
        
        #
        
        while ((i := 0) < self.tries):
            
            request = self.ai.responses.create(
                model=self.model,
                input=self.messages
            )
            
            self.tokens["input"] += request.usage.input_tokens
            self.tokens["output"] += request.usage.output_tokens
            
            return json.loads(request.output_text)
            
            """
            
            request = self.ai.inference(self.messages)
            print(request)
            return json.loads(request)
            
            """
            
            i += 1
        #
    #
#