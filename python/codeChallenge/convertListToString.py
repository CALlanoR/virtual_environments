# funcion: 
#     input: array de strings ["foo", "bar", "xyz"]
#    output: "1:foo|2:bar|3:xyz"

def convert_array_to_custom_string(lst: list[str]) -> str:
    print(type(f"{pos+1}:{element}" for pos,element in enumerate(lst)))
    output_str = "|".join(f"{pos+1}:{element}" for pos,element in enumerate(lst))
    return output_str
    
print(convert_array_to_custom_string(["foo", "bar", "xyz"]))


# print(str.join.__doc__)
# print(enumerate.__doc__