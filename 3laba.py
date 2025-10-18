# Сортировки
from numpy.ma.core import negative


# Выбором
def sort_choisemethod(arr):
    for i in range(len(arr)):
        min_index = i
        for j in range(i + 1, len(arr)):
            if arr[j] < arr[min_index]:
                min_index = j
        arr[i], arr[min_index] = arr[min_index], arr[i]
    return arr


# Radix-прямая // Строки пока не работают!!!
def sort_radixmethod(arr):
    negatives = [abs(x) for x in arr if x < 0]
    non_neg = [x for x in arr if x >= 0]

    def sort_non_negative(nums):
        if not nums:
            return nums


        max_val = max(nums)
        num_bits = max_val.bit_length()

        for bit in range(num_bits):
            zero = []
            ones = []
            for value in nums:
                if (value >> bit) & 1:
                    ones.append(value)
                else:
                    zero.append(value)
            nums = zero + ones
        return nums

    sorted_non_neg = sort_non_negative(non_neg)
    sorted_neg = [-x for x in reversed(sort_non_negative(negatives))]

    return sorted_neg + sorted_non_neg





if __name__ == '__main__':
    num_massive = [7, 4, -3, 8, 5, 6]
    string_massive = ['банан', 'аб', 'ск', 'кп', 'ав', 'цу']

    print(f"Сортировка выбором:\n{sort_choisemethod(num_massive)}"
          f"\n{sort_choisemethod(string_massive)}")
    print(f"\nСортировка Radix-прямая:\n{sort_radixmethod(num_massive)}")

