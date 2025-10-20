# Сортировки
##from numpy.ma.core import negative


# Выбором
def sort_choisemethod(arr):
    for i in range(len(arr)):
        min_index = i
        for j in range(i + 1, len(arr)):
            if arr[j] < arr[min_index]:
                min_index = j
        arr[i], arr[min_index] = arr[min_index], arr[i]
    return arr


# Radix-прямая
def sort_radixmethod(arr):
    if not arr:
        return arr

    if isinstance(arr[0], int):
        return _radix_sort_num(arr)
    elif isinstance(arr[0], str):
        return _radix_sort_str(arr)
    else:
        raise TypeError('Radix-sort method must be of type int or str')


def _radix_sort_num(arr):
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

def _radix_sort_str(arr):
    max_length = max(len(str(item)) for item in arr)
    for i in range(max_length - 1, -1, -1):
        buckets = [[] for _ in range(256)]
        for item in arr:
            key = ord(item[i]) if i < len(item) else 0
            buckets[key].append(item)

        arr = []
        for bucket in buckets:
            arr.extend(bucket)
    return arr


if __name__ == '__main__':
    num_massive = [7, 4, -3, 8, 5, 6]
    string_massive = ['banAna', 'Apple', 'jews', 'nig']

    print(f"\nСортировка выбором:\n{sort_choisemethod(num_massive)}"
          f"\n{sort_choisemethod(string_massive)}")
    print(f"\nСортировка Radix-прямая:\n{sort_radixmethod(num_massive)}"
          f"\n{sort_radixmethod(string_massive)}")
    print(f"\nСортировки Python: \n{sorted(num_massive)}\n{sorted(string_massive)}")

