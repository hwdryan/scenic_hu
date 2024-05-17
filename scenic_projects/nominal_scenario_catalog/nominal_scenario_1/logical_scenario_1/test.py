a = [1, 2, 3, 4]
length_a = len(a)
count = 0

while count < 10:
    print(a[count % length_a], end=", ")
    count += 1
