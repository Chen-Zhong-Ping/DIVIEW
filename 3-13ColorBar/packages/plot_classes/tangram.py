
# a color bar pertains to a set of two or more pictures that share the same type of data, Te for example, so I don't want to make each 2D_data object to have its individual color bar.

class Tangram:
    
    def __init__(self):
        
        self.bin = []
        self.color = [(0, 0, 0, 1)]
        
    def add_bin(self, newbin, newcolor):
        if newbin not in self.bin:
            self.bin.append(newbin)
            self.bin.sort()
            self.color.insert(self.bin.index(newbin), newcolor)
        else:
            print("bin is already in the list! nothing done")
        
    def map2color(self, value):
        if value >= self.bin[-1]:
            return self.color[-1]
        else:
            for i in range(0, len(self.bin)):
                if value < self.bin[i]:
                    return self.color[i]

