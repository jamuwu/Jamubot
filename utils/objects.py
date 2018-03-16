class User:
    '''Extracting the important information since 2018'''
    def __init__(self, data):
        data = data[0]
        self.name = data['username']
        self.user = int(data['user_id'])
        self.cc = data['country'] # Country code
        self.grank = int(data['pp_rank'])
        self.crank = int(data['pp_country_rank'])
        self.pp = float(data['pp_raw'])
        self.playcount = int(data['playcount'])
        self.totalscore = int(data['total_score'])
        self.