# Ejemplo1
a = [1, 2, 3, 4, 5]
res = [val * 2 for val in a]
print(res)

# Ejemplo2 
# Sintax:
# newlist = [expression for item in iterable if condition == True]
fruits = ["apple", "banana", "cherry", "kiwi", "mango"]
newlist = [x for x in fruits if "a" in x]
print(newlist)


# Ejemplo 3
newlist = [x for x in range(10) if x < 5] 
print(newlist)

# Ejemplo 4
newlist = [x.upper() for x in fruits]
print(newlist)

# Ejemplo 5
newlist1 = [x if x != "banana" else "orange" for x in fruits]
print(newlist1)

# Ejemplo 6 (crear una lista con rango)
a = [i for i in range(10)]
print(a)

# Ejemplo 7 Using nested loops
c = [(x, y) for x in range(3) for y in range(3)]
print(c)

# Ejemplo 8 Flattening a list of lists
mat = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
res = [val for row in mat for val in row]
print(res)