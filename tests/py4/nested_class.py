class Outer:
    class Inner:
        def get(self):
            return 5

o = Outer()
i = Outer.Inner()
print(i.get())
