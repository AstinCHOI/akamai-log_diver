for i in range(5):
    print(i, end=' ')
# => 0 1 2 3 4

def custom_range(end):
    i = 0
    while i < end:
        yield i
        i += 1

gen = custom_range(5)  # => <generator object custom_range>
for i in gen:
    print(i, end=' ')
# => 0 1 2 3 4

list(custom_range(5))  # => [0, 1, 2, 3, 4]

# >>> gen = custom_range(2)
# >>> next(gen)
# 0
# >>> next(gen)
# 1
# >>> next(gen)
# Traceback (most recent call last):
#  File "<stdin>", line 1, in <module>
# StopIteration