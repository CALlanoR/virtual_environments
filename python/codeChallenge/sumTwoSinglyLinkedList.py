from typing import Optional

# Definition for singly-linked list.
class ListNode:
     def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def createSinglyLinkedList(self, l1: list[int], reverse = True) -> Optional[ListNode]:
        if reverse:
            l1.reverse()
        head = ListNode(l1[0])
        current = head

        for element in l1[1:]:
            current.next = ListNode(element)
            current = current.next
        return head

    def convertSinglyLinkedListToList(self, sll: Optional[ListNode]) -> list[int]:
        list_result = []
        while sll:
            list_result.append(sll.val)
            sll = sll.next
        return list_result

    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        list_sum = []
        carry = 0
        while l1:
            val1 = l1.val
            if val1 < 0 or val1 > 9:
                print("contraint violated in singlyLinkedList1: 0 <= Node.val <= 9")
                return None
            val2 = 0
            if l2:
                val2 = l2.val
                if val2 < 0 or val2 > 9:
                    print("contraint violated in singlyLinkedList2: 0 <= Node.val <= 9")
                    return None
            
            sum = val1 + val2 + carry
            # print(f"val1: {val1}, val2: {val2}, carry: {carry}, sum: {sum}")
            if sum >= 10:
                carry = sum // 10
                num = sum % 10
                list_sum.append(num)
            else:
                carry = 0
                list_sum.append(sum)
            l1 = l1.next
            if l2:
                l2 = l2.next
        if carry:
            list_sum.append(carry)
        return self.createSinglyLinkedList(list_sum, reverse = False)
        
if __name__ == "__main__":

    test_cases = [
        ([4,6,5], [3,4,2], [7, 0, 8]),
        ([0], [0], [0]),
        ([9,9,9,9,9,9,9], [9,9,9,9], [8,9,9,9,0,0,0,1])
    ]

    for i, (l1, l2, expected) in enumerate(test_cases):
        solution = Solution()
        singlyLinkedList1 = solution.createSinglyLinkedList(l1)
        singlyLinkedList2 = solution.createSinglyLinkedList(l2)

        result = solution.addTwoNumbers(singlyLinkedList1, singlyLinkedList2)
        result_plain_list = solution.convertSinglyLinkedListToList(result)
        print(f"test case: {i+1}, l1: {l1}, l2: {l2}, expected: {expected}, got: {result_plain_list}")
        assert result_plain_list == expected, "not ok"