# 1. Two Sum
# Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.
# You may assume that each input would have exactly one solution, and you may not use the same element twice.
# You can return the answer in any order.


# Example 1:

# Input: nums = [2,7,11,15], target = 9
# Output: [0,1]
# Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].

# Example 2:

# Input: nums = [3,2,4], target = 6
# Output: [1,2]

# Example 3:

# Input: nums = [3,3], target = 6
# Output: [0,1]

class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        result = []
        if len(nums) < 2 or len(nums) >= 10**4:
            print("contraint violated: 2 <= nums.length <= 10**4")
        elif target <= -10**9 or target >= 10**9:
            print("constraint violated:  -10**9 <= nums[i] <= 10**9")

        for i in range(len(nums)):
            for j in range(i+1, len(nums)):
                if nums[i] <= -10**9 or nums[i] >= 10**9:
                    print("constraint violated: -10**9 <= target <= 10**9")
                    return []
                if (nums[i] + nums[j]) == target:
                    result.append((i,j))
        return result


if __name__ == "__main__":
    solution = Solution()
    test_cases = [
        ([2,7,11,15], 9, [(0,1)]),
        ([3,2,4], 6, [(1,2)]),    
        ([3,3], 6, [(0,1)]),
        ([2,7,11,15,6,3], 9, [(0,1), (4,5)]),
    ]
    
    for i, (nums, target, expected) in enumerate(test_cases):
        result = solution.twoSum(nums, target)
        print(f"Test case {i+1}: nums: {nums} | target: {target} | Expected: {expected} | Got: {result}")
        assert result == expected, f"Test case {i+1} failed: expected {expected}, got {result}"
        print(result)