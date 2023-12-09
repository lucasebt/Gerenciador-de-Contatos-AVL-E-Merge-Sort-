# Em sorting_algorithms.py

def merge_sort(arr, key=lambda x: x):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left_half = arr[:mid]
    right_half = arr[mid:]

    left_half = merge_sort(left_half, key)
    right_half = merge_sort(right_half, key)

    return merge(left_half, right_half, key)

def merge(left, right, key=lambda x: x):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if key(left[i]) < key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])

    return result
