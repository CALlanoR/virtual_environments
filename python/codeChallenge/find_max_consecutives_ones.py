class findMaxConsecutiveOnes:
    def findMaxConsecutiveOnes(self, nums):
        max_ones_count = 0
        current_count = 0
        for number in nums:
            print("number:", number)
            if number == 1:
                current_count += 1
            else:
                if current_count >= max_ones_count:
                    max_ones_count = current_count
                    current_count = 0
        return max(max_ones_count, current_count)
    
def main():
    solution = findMaxConsecutiveOnes()
    test_cases = [
        ([1, 1, 0, 1, 1, 1], 3),
        ([1, 0, 1, 1, 0, 1], 2),
        ([0, 0, 0], 0),
        ([1, 1, 1, 1], 4),
        ([1, 0, 1, 0, 1], 1)
    ]
    
    for i, (nums, expected) in enumerate(test_cases):
        result = solution.findMaxConsecutiveOnes(nums)
        print(f"Test case {i+1}: Input: {nums} | Expected: {expected} | Got: {result}")
        assert result == expected, f"Test case {i+1} failed: expected {expected}, got {result}"
    
    print("All test cases passed!")

if __name__ == "__main__":
    main()