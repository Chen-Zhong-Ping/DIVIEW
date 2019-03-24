
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

    def change_bin_value(self, bin_index, new_binvalue):
        if new_binvalue in self.bin :
            print("bin value is already in the list! nothing done")
            return None
        else:
            self.bin[bin_index] = new_binvalue
            self.bin.sort()
            if self.bin.index(new_binvalue) == bin_index:    # determine whether the bin list has been sorted or not
                return False
            else:
                return True

    def map2color(self, value):
        if value >= self.bin[-1]:
            return self.color[-1]
        else:
            for i in range(0, len(self.bin)):
                if value < self.bin[i]:
                    return self.color[i]

    def write_colorbar(self, cb_file_name):
        with open(cb_file_name, "w") as output_file:
#            print(len(self.bin), file=output_file)
            for value in self.bin:
                print(value, file=output_file)
            for colorcode in self.color:
                print(f"{colorcode[0]} {colorcode[1]} {colorcode[2]} {colorcode[3]}", file=output_file)

    def read_colorbar(self, cb_file):
        lines = []
        with open(cb_file, 'rt') as input_file :
            for line in input_file :
                lines.append(line)
#        print((len(lines)-1)/2)    # note that (len(lines)-1)/2 will give you a float not integer .split()[0]
#        print((len(lines)-1)//2)
        self.bin = [float(lines[i]) for i in range((len(lines)-1)//2)]    # you need integer division //
#        print(self.bin)
        self.color = [(float(lines[i].split()[0]), float(lines[i].split()[1]), float(lines[i].split()[2]), float(lines[i].split()[3])) for i in range((len(lines)-1)//2, len(lines))]
#        print(self.color)
