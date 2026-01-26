a = int(input())
arr = []
for i in range(0,a):
    x = 2**i
    if not(x > a):
        arr.append(x)
    else:
        for i in range(0,arr):
            print(i)
        break