# Поиск подстроки в строке

# Наивный алгоритм
def naive_search(text, pattern):
    n = len(text)
    m = len(pattern)
    matches = []

    for i in range(n - m + 1):
        match = True
        for j in range(m):
            if text[i + j] != pattern[j]:
                match = False
                break
        if match:
            matches.append(i)

    return matches

# Конечный автомат
# def build_transition_table(pattern):
#     m = len(pattern)
#     alphabet = set(pattern)
#     table = {}
#
#     for state in range(m + 1):
#         for char in alphabet:
#             next_state = state
#
#             if state < m and char == pattern[state]:
#                 next_state = state + 1
#             else:
#                 for ns in range(state, 0, -1):
#                     if pattern[:ns] == (pattern[1:state] + char)[-ns:]:
#                         next_state = ns
#                         break
#                         ## pattern[:3] = "ABA" ==
#                 else:
#                     next_state = 0
#
#             table[(state, char)] = next_state
#
#     return table

def build_transition_table(pattern):
    m = len(pattern)
    alphabet = set(pattern)
    table = {}

    for state in range(m + 1):
        for char in alphabet:
            if state < m and char == pattern[state]:
                table[(state, char)] = state + 1
            else:
                current_string = pattern[:state] + char
                # current_string = "AB" + "B" = "ABB"
                for length in range(min(state + 1, m), 0, -1):
                    if current_string.endswith(pattern[:length]):
                        # for length = 3, 2, 1
                        # length = 3: "ABB".endswith("ABA") False
                        # length = 2: "ABB".endswith("AB") False
                        # length = 1: "ABB".endswith("A") False
                        next_state = length
                        break
                else:
                    next_state = 0

                table[(state, char)] = next_state

    return table


def search_substring(text, pattern):
    if not pattern or not text:
        return []

    table = build_transition_table(pattern)
    print("Таблица переходов:")
    for key, value in sorted(table.items()):
        print(f"Состояние {key[0]}, символ '{key[1]}' → {value}")

    m = len(pattern)
    state = 0
    results = []

    for i, char in enumerate(text):
        if (state, char) in table:
            state = table[(state, char)]
        else:
            state = 0
            if char == pattern[0]:
                state = 1

        if state == m:
            results.append(i - m + 1)

    return results


if __name__ == "__main__":
    text = "ababcababa"
    pattern = "aba"
    print(f"text: {text}\npattern: {pattern}\n")
    print(f"\nВхождения найдены на позициях:\n{naive_search(text, pattern)} - результат работы наивного поиска"
          f"\n{search_substring(text, pattern)} - результат работы конечного автомата")