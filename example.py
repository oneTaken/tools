import timeit

def testTime1():
    a, b = 3, 5
    a, b = (a, b) if a>b else (b,a)

def testTime2():
    a, b = 3, 5
    x = max(a, b)
    y = min(a, b)

if __name__ == "__main__":
    times = 100000
    time1 = timeit.Timer(testTime1)
    print(time1.timeit(times))
    time2 = timeit.Timer(testTime2)
    print(time2.timeit(times))

