class BitmapFile:
    def __init__(self, data):
        self.size = self.sumBytes(data[2:6])
        self.start = self.sumBytes(data[10:14])
        self.width = self.sumBytes(data[18:22])
        self.height = self.sumBytes(data[22:26])
        self.depth = self.sumBytes(data[28:30])
        self.bpp = self.depth // 8
        #self.head = data[0:self.start]
        #self.data = data[self.start:self.size]
        self.data = data
    
    def sumBytes(self, d):
        sum = 0
        for i in range(len(d)):
            sum = sum + (d[i] % 16) * 16**(i*2) + (d[i] // 16) * 16**(i*2 + 1)
        return sum