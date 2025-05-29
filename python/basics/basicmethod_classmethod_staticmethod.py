class Example:
    count = 0

    def __init__(self, value):
        self.value = value
        Example.count += 1

    def increment_count(self):
        self.count += 1

    def get_count_basic(self):
        return self.count

    @classmethod
    def get_count(cls):
        return cls.count


example = Example(5)
print(example.get_count_basic())
print(Example.get_count())
print("---------------")
example.increment_count()
print(example.get_count_basic())
print(Example.get_count())
print("---------------")
example.increment_count()
print(example.get_count_basic())
print(Example.get_count())
print("---------------")
example2 = Example(5)
example.increment_count()
print(example.get_count_basic())
print(Example.get_count())

# Result:
# 1
# 1
# ---------------
# 2
# 1
# ---------------
# 3
# 1
# ---------------
# 4
# 2
