class Base:
    def set_value(self, v):
        self.value = v

    def get_value(self):
        return self.value

class Derived(Base):
    def get_value(self):
        return self.value * 2

o = Derived()
o.set_value(5)
print(o.get_value())
