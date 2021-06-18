class Status():
    def __init__(self, state, error="", info="", time="", dic={}):
        self.state = state
        self.info  = info
        self.error = error
        self.time  = time
        self.dic   = dic

    # setters
    def set_state(self, b):
        self.state = b

    def set_info(self, s):
        self.info  = s
    
    def set_error(self, e):
        self.error = e
    
    def set_time(self, t):
        self.time  = t
    
    def set_dic(self, d):
        self.dic   = d
    
    # getters
    def get_state(self):
        return self.state 
    
    def get_info(self):
        return self.info 
    
    def get_error(self):
        return self.error
    
    def get_time(self):
        return self.time
    
    def get_dic(self):
        return self.dic