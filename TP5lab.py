import struct
import sys
import os
from typing import Optional, Dict, List, Tuple
from collections import defaultdict

def read_ppm(filename: str) -> Tuple[str, int, int, int, bytes]:
    with open(filename, 'rb') as f:
        magic = f.readline().decode('ascii').strip()

        if magic not in ['P3', 'P6']:
            raise ValueError(f"Неподдерживаемый формат PPM: {magic}")

        line = f.readline()
        while line.startswith(b'#'):
            line = f.readline()

        width, height = map(int, line.decode('ascii').split())
        maxval = int(f.readline().decode('ascii').strip())

        if magic == 'P3':
            data = f.read().decode('ascii').split()
            pixel_data = bytes(int(x) for x in data)
        else:
            pixel_data = f.read()

        return magic, width, height, maxval, pixel_data


def write_ppm(filename: str, magic: str, width: int, height: int,
              maxval: int, pixel_data: bytes):
    with open(filename, 'wb') as f:
        f.write(f"{magic}\n".encode('ascii'))
        f.write(f"{width} {height}\n".encode('ascii'))
        f.write(f"{maxval}\n".encode('ascii'))

        if magic == 'P3':
            values = [str(b) for b in pixel_data]
            for i in range(0, len(values), 15):
                line = ' '.join(values[i:i + 15]) + '\n'
                f.write(line.encode('ascii'))
        else:
            f.write(pixel_data)


def create_node(weight: int = 0, number: int = 0, symbol: Optional[int] = None) -> Dict:
    return {
        'weight': weight,
        'number': number,
        'symbol': symbol,
        'parent': None,
        'left': None,
        'right': None
    }


def is_leaf(node: Dict) -> bool:
    return node['left'] is None and node['right'] is None

def is_nyt(node: Dict) -> bool:
    return node['symbol'] is None and is_leaf(node)

def get_code(node: Dict) -> List[int]:
    code = []
    current = node
    while current['parent'] is not None:
        parent = current['parent']
        if parent['left'] == current:
            code.append(0)
        else:
            code.append(1)
        current = parent
    return code[::-1]


def find_largest_number_in_block(node: Dict, weight_blocks: Dict) -> Dict:
    target_weight = node['weight']
    parent = node['parent']

    # Получаем все узлы с таким же весом
    candidates = weight_blocks.get(target_weight, [])

    largest = node
    for n in candidates:
        if n is not parent and n['number'] > largest['number']:
            largest = n

    return largest


def swap_nodes(node1: Dict, node2: Dict, tree_state: Dict):
    if node1 is node2:
        return

    # Удаляем из блоков весов
    weight_blocks = tree_state['weight_blocks']

    w1 = node1['weight']
    w2 = node2['weight']

    if node1 in weight_blocks[w1]:
        weight_blocks[w1].remove(node1)
    if node2 in weight_blocks[w2]:
        weight_blocks[w2].remove(node2)

    parent1 = node1['parent']
    parent2 = node2['parent']

    if parent1:
        if parent1['left'] is node1:
            parent1['left'] = node2
        else:
            parent1['right'] = node2

    if parent2:
        if parent2['left'] is node2:
            parent2['left'] = node1
        else:
            parent2['right'] = node1

    node1['parent'], node2['parent'] = parent2, parent1
    node1['number'], node2['number'] = node2['number'], node1['number']

    # Возвращаем в блоки весов
    weight_blocks[w1].append(node1)
    weight_blocks[w2].append(node2)

    if tree_state['root'] is node1:
        tree_state['root'] = node2
    elif tree_state['root'] is node2:
        tree_state['root'] = node1


def update_tree(node: Dict, tree_state: Dict):
    current = node
    weight_blocks = tree_state['weight_blocks']

    while current is not None:
        largest = find_largest_number_in_block(current, weight_blocks)

        if largest is not current and largest is not current['parent']:
            swap_nodes(current, largest, tree_state)

        # Удаляем из старого блока веса
        old_weight = current['weight']
        if current in weight_blocks[old_weight]:
            weight_blocks[old_weight].remove(current)

        # Увеличиваем вес
        current['weight'] += 1

        # Добавляем в новый блок веса
        weight_blocks[current['weight']].append(current)

        current = current['parent']


def init_encoder_state() -> Dict:
    nyt = create_node(0, 256, None)
    weight_blocks = defaultdict(list)
    weight_blocks[0].append(nyt)

    return {
        'nyt': nyt,
        'root': nyt,
        'seen': {},
        'weight_blocks': weight_blocks  # ОПТИМИЗАЦИЯ: индекс по весам
    }


def add_symbol(symbol: int, state: Dict) -> List[int]:
    code = []
    node = state['seen'].get(symbol)

    if node is None:
        nyt = state['nyt']
        code.extend(get_code(nyt))

        for i in range(7, -1, -1):
            code.append((symbol >> i) & 1)

        new_nyt = create_node(0, nyt['number'] - 2, None)
        new_leaf = create_node(1, nyt['number'] - 1, symbol)

        # Удаляем NYT из блока веса 0
        weight_blocks = state['weight_blocks']
        if nyt in weight_blocks[0]:
            weight_blocks[0].remove(nyt)

        nyt['symbol'] = None
        nyt['left'] = new_nyt
        nyt['right'] = new_leaf
        nyt['weight'] = 1

        new_nyt['parent'] = nyt
        new_leaf['parent'] = nyt

        # Добавляем узлы в блоки весов
        weight_blocks[0].append(new_nyt)
        weight_blocks[1].append(new_leaf)
        weight_blocks[1].append(nyt)

        state['nyt'] = new_nyt
        state['seen'][symbol] = new_leaf

        update_tree(nyt['parent'], state)
    else:
        code.extend(get_code(node))
        update_tree(node, state)

    return code


def encode_data(data: bytes) -> bytes:
    state = init_encoder_state()
    bits = []

    total = len(data)
    print(f"Кодирование {total: ,} байт...")

    # Индикатор прогресса
    checkpoint = total // 100 if total > 1000 else total // 10

    for i, byte in enumerate(data):
        bits.extend(add_symbol(byte, state))

        # Показываем прогресс
        if checkpoint > 0 and (i + 1) % checkpoint == 0:
            progress = (i + 1) / total * 100
            print(f"  Прогресс: {progress:.1f}% ({i + 1:,}/{total:,} байт)", end='\r')

    print(f"  Прогресс: 100.0% ({total:,}/{total:,} байт)")
    print("Преобразование битов в байты...")

    result = bytearray()
    result.extend(struct.pack('>I', len(data)))

    padding = (8 - len(bits) % 8) % 8
    result.append(padding)

    bits.extend([0] * padding)

    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        result.append(byte)

    return bytes(result)


# Функции декодирования
def init_decoder_state() -> Dict:
    nyt = create_node(0, 256, None)
    weight_blocks = defaultdict(list)
    weight_blocks[0].append(nyt)

    return {
        'nyt': nyt,
        'root': nyt,
        'seen': {},
        'weight_blocks': weight_blocks
    }


def decode_data(data: bytes) -> bytes:
    if len(data) < 5:
        return b''

    original_size = struct.unpack('>I', data[0:4])[0]
    padding = data[4]

    print(f"Декодирование {original_size:,} байт...")

    bits = []
    for byte in data[5:]:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)

    if padding > 0:
        bits = bits[:-padding]

    state = init_decoder_state()
    result = bytearray()
    bit_index = 0

    checkpoint = original_size // 100 if original_size > 1000 else original_size // 10

    while len(result) < original_size and bit_index < len(bits):
        current = state['root']

        while not is_leaf(current):
            if bit_index >= len(bits):
                break

            if bits[bit_index] == 0:
                current = current['left']
            else:
                current = current['right']
            bit_index += 1

        if is_nyt(current):
            if bit_index + 8 > len(bits):
                break

            symbol = 0
            for _ in range(8):
                symbol = (symbol << 1) | bits[bit_index]
                bit_index += 1

            result.append(symbol)

            nyt = state['nyt']
            new_nyt = create_node(0, nyt['number'] - 2, None)
            new_leaf = create_node(1, nyt['number'] - 1, symbol)

            weight_blocks = state['weight_blocks']
            if nyt in weight_blocks[0]:
                weight_blocks[0].remove(nyt)

            nyt['symbol'] = None
            nyt['left'] = new_nyt
            nyt['right'] = new_leaf
            nyt['weight'] = 1

            new_nyt['parent'] = nyt
            new_leaf['parent'] = nyt

            weight_blocks[0].append(new_nyt)
            weight_blocks[1].append(new_leaf)
            weight_blocks[1].append(nyt)

            state['nyt'] = new_nyt
            state['seen'][symbol] = new_leaf

            update_tree(nyt['parent'], state)
        else:
            symbol = current['symbol']
            result.append(symbol)
            update_tree(current, state)

        # Показываем прогресс
        if checkpoint > 0 and len(result) % checkpoint == 0:
            progress = len(result) / original_size * 100
            print(f"  Прогресс: {progress:.1f}% ({len(result):,}/{original_size:,} байт)", end='\r')

    print(f"  Прогресс: 100.0% ({len(result):,}/{original_size:,} байт)")

    return bytes(result)


# Функции сжатия/распаковки PPM

def compress_ppm(input_file: str, output_file: str):
    try:
        print(f"Чтение PPM файла: {input_file}")
        magic, width, height, maxval, pixel_data = read_ppm(input_file)

        print(f"Формат:  {magic}")
        print(f"Размер:  {width}x{height}")
        print(f"Максимальное значение: {maxval}")
        print(f"Размер пиксельных данных: {len(pixel_data)} байт\n")

        compressed_pixels = encode_data(pixel_data)

        archive = bytearray()
        archive.extend(b'PPMVIT')
        archive.append(1)
        archive.append(ord(magic[1]))
        archive.extend(struct.pack('>I', width))
        archive.extend(struct.pack('>I', height))
        archive.extend(struct.pack('>I', maxval))
        archive.extend(compressed_pixels)

        with open(output_file, 'wb') as f:
            f.write(archive)

        original_size = len(pixel_data)
        archive_size = len(archive)
        total_original = os.path.getsize(input_file)
        ratio = (1 - archive_size / total_original) * 100

        print(f"\nСжатие завершено!")
        print(f"Исходный размер файла: {total_original: ,} байт")
        print(f"Размер архива: {archive_size:,} байт")
        print(f"Степень сжатия: {ratio:.2f}%")

    except Exception as e:
        print(f"Ошибка при сжатии: {e}")
        import traceback
        traceback.print_exc()


def decompress_ppm(input_file: str, output_file: str):
    try:
        print(f"Чтение архива: {input_file}")

        with open(input_file, 'rb') as f:
            data = f.read()

        if data[: 6] != b'PPMVIT':
            raise ValueError("Неверная сигнатура файла")

        version = data[6]
        if version != 1:
            raise ValueError(f"Неподдерживаемая версия:  {version}")

        format_char = chr(data[7])
        magic = f"P{format_char}"

        width = struct.unpack('>I', data[8:12])[0]
        height = struct.unpack('>I', data[12:16])[0]
        maxval = struct.unpack('>I', data[16:20])[0]

        print(f"Формат: {magic}")
        print(f"Размер: {width}x{height}")
        print(f"Максимальное значение: {maxval}\n")

        compressed_pixels = data[20:]
        pixel_data = decode_data(compressed_pixels)

        print(f"\nСохранение PPM файла: {output_file}")
        write_ppm(output_file, magic, width, height, maxval, pixel_data)

        print("Распаковка завершена!")

    except Exception as e:
        print(f"Ошибка при распаковке: {e}")
        import traceback
        traceback.print_exc()


def get_ppm_info(filename: str):
    try:
        magic, width, height, maxval, pixel_data = read_ppm(filename)

        print(f"Информация о PPM файле:  {filename}")
        print(f"Формат: {magic}")
        print(f"Размер изображения: {width}x{height}")
        print(f"Максимальное значение:  {maxval}")
        print(f"Количество пикселей: {width * height: ,}")
        print(f"Ожидаемый размер данных: {width * height * 3:,} байт")
        print(f"Фактический размер данных: {len(pixel_data):,} байт")
        print(f"Размер файла: {os.path.getsize(filename):,} байт")

    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")

if __name__ == "__main__":
    input_file = "test.ppm"      # Исходный PPM файл
    compressed_file = "test.vit"  # Сжатый файл

    # 1. Сжать файл
    compress_ppm(input_file, compressed_file)

    # 2. Распаковать файл
    # decompress_ppm(compressed_file, restored_file)
