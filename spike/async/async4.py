def sendme():
    while 1:
        something = yield
        if something is None:
            raise StopIteration()
        print(something)

gen = sendme()
next(gen)
gen.send('a')  # => a
gen.send('b')  # => b
gen.send(None)  # StopIteration