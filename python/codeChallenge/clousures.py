# Define f such that f(n)(m) == n+m.  Example: f(3)(4) should be 7.
    
def f(n: int) -> int:
    # x = lambda m: n + m
    def x(m): 
        return n + m
    return x

print(type(f(3)))
print(f(3)(4))

plusone = f(1)
plustwo = f(2)
print(f"1+1={plusone(1)}, 2+2={plustwo(2)}")