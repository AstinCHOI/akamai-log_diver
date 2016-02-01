# http://benno.id.au/blog/2015/05/25/await1
from types import coroutine

@coroutine
def switch():
    yield


async def coro1():
    print("C1: Start")
    await switch()
    print("C1: Stop")

async def coro2():
    print("C2: Start")
    print("C2: a")
    print("C2: b")
    print("C2: c")
    print("C2: Stop")

# def run(coros):
#     coros = list(coros)

#     while coros:
#         # Duplicate list for iteration so we can remove from original list.
#         for coro in list(coros):
#             try:
#                 coro.send(None)
#             except StopIteration:
#                 coros.remove(coro)

c1 = coro1()
c2 = coro2()

try:
    c1.send(None)
except StopIteration:
    print("c1 stoped1")
    pass
try:
    c2.send(None)
except StopIteration:
    print("c2 stoped")
    pass
try:
    c1.send(None)
except StopIteration:
    print("c1 stoped2")
    pass

print(c1, c2)

# run([c1, c2])