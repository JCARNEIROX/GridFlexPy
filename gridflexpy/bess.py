def construct_bess(batteries):

    ids = batteries['Id'].values
    list_bess_objects = []

    for id in ids:
        bess = Bess(id, batteries.loc[batteries['Id'] == id, 'Bus_node'].values[0], batteries.loc[batteries['Id'] == id, 'Pmax'].values[0], 
                    batteries.loc[batteries['Id'] == id, 'Einit'].values[0], batteries.loc[batteries['Id'] == id, 'Emax'].values[0], 
                    batteries.loc[batteries['Id'] == id, 'Emin(%)'].values[0], batteries.loc[batteries['Id'] == id, 'Efficiency'].values[0])
        list_bess_objects.append(bess)

    return list_bess_objects

class Bess:
    def __init__(self, id,buss_node,pmax,eini,emax,emin,efficiency):
        self.id = id
        self.bus_node = buss_node
        self.pmax = pmax
        self.eini = eini
        self.emax = emax
        self.emin = emin
        self.efficiency = efficiency

    def get_id(self):
        return self.id
    
    def get_bus_node(self):
        return self.bus_node
    
    def get_pmax(self):
        return self.pmax
    
    def get_eini(self):
        return self.eini
    
    def get_emax(self):
        return self.emax
    
    def get_emin(self):
        return self.emin
    
    def get_efficiency(self):
        return self.efficiency
    