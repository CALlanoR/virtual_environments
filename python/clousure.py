def calculate():
    num = 1
    def inner_func():
        nonlocal num
        num += 2
        return num
    return inner_func

# call the outer function
odd = calculate()

# call the inner function
print(odd())
print(odd())
print(odd())

# # call the outer function again
odd2 = calculate()
print(odd2())

# output:
# 3
# 5
# 7
# 3

# usadas para simular encapsulamiento y la ocultacion de la programacion orientada a objetos. 
# El concepto de clausura fue definido por Peter J. Landin en 1964