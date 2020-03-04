class Loopqueue:
    def __init__(self, length):
        self.head = 0
        self.cnt = 0
        self.maxSize = length
        self.__list = [None]*length


    def push(self, data):
        self.__list[self.head] = data
        self.head = (self.head+1)%self.maxSize
        
        if self.cnt < self.maxSize:
            self.cnt += 1

        return True

    def pop(self):
        if self.cnt == 0:
            return False

        self.head = (self.head-1+self.maxSize)%self.maxSize
        data = self.__list[self.head]
        
        self.cnt -= 1

        return data

    def clear(self):
        self.head = 0
        self.cnt = 0
        return True

    def __str__(self):
        s = ''
        for i in range(self.cnt):
            index = (i + self.head) % self.maxSize
            s += str(self.__list[index])+' '
        return s

    def len(self):
        return self.cnt
