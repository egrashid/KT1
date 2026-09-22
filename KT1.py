import heapq
import random
import time
class TrieNode:
    # Узел префиксного дерева (Trie)
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.frequency = 0

class Trie:
    # Префиксное дерево с автодополнением на основе Min-Heap
    def __init__(self):
        self.root = TrieNode()
    def insert(self, word: str, frequency: int = 1):
        # Добавляет слово и его частоту в Trie. Если слово уже есть, увеличивает его частоту
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.frequency += frequency
    def search(self, word: str) -> bool:
        # Проверяет, есть ли слово в Trie
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end
    def _collect(self, node, prefix, heap, k=5):
        if node.is_end:
            item = (node.frequency, prefix)
            if len(heap) < k:
                heapq.heappush(heap, item)
            elif item > heap[0]:
                heapq.heapreplace(heap, item)
        for ch, child in node.children.items():
            self._collect(child, prefix + ch, heap, k)

    def autocomplete(self, prefix: str) -> list:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]
        heap = []
        self._collect(node, prefix, heap)
        return [w for _, w in sorted(heap, key=lambda x: (-x[0], x[1]))]

    def _collect_max(self, node, prefix, heap):
        if node.is_end:
            heapq.heappush(heap, (-node.frequency, prefix))
        for ch, child in node.children.items():
            self._collect_max(child, prefix + ch, heap)

    def autocomplete_max(self, prefix: str, k: int = 5) -> list:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]
        heap = []
        self._collect_max(node, prefix, heap)
        return [word for _, word in
                (heapq.heappop(heap) for _ in range(min(k, len(heap))))]
        return [word for _, word in
                    (heapq.heappop(heap) for _ in range(min(k, len(heap))))]
    def delete(self, word: str) -> bool:
            # Удаляет слово из Trie и подрезает пустые ветки
        def _rec(node, i):
            if i == len(word):
                if not node.is_end:
                    return False
                node.is_end = False
                node.frequency = 0
                return len(node.children) == 0
            ch = word[i]
            if ch not in node.children:
                return False
            if _rec(node.children[ch], i + 1):
                del node.children[ch]
            return not node.is_end and not node.children
        return _rec(self.root, 0)

class PriorityQueue:
    # Очередь с приоритетами: чем больше priority, тем раньше обработка
    def __init__(self):
        self._heap = []
        self._counter = 0
    def enqueue(self, request: str, priority: int):
        heapq.heappush(self._heap, (-priority, self._counter, request))
        self._counter += 1
    def dequeue(self):
        if not self._heap:
            raise IndexError("Очередь пуста")
        neg_p, _, request = heapq.heappop(self._heap)
        return -neg_p, request
    def is_empty(self) -> bool:
        return not self._heap

def load_words(path: str, trie: Trie):
    # Загружает слова из файла формата: 'слово частота' (по одному на строку).
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            word = parts[0]
            freq = int(parts[1]) if len(parts) > 1 else 1
            trie.insert(word, freq)

def benchmark(trie: Trie, n: int = 10_000):
    pq = PriorityQueue()
    prefixes = ["a", "b", "c", "t", "s", "ap", "ba"]
    for _ in range(n):
        pq.enqueue(("autocomplete", random.choice(prefixes)),
                   priority=random.randint(0, 1))

    t0 = time.perf_counter()
    while not pq.is_empty():
        _, req = pq.dequeue()
        if req[0] == "autocomplete":
            trie.autocomplete(req[1])
    dt = time.perf_counter() - t0
    print(f"\n[benchmark] {n} запросов за {dt:.3f} с ({n / dt:.0f} запр./с)")


if __name__ == "__main__":
    trie = Trie()

    # 1 Наполнение Trie данными
    dataset = {
        "apple": 10,
        "peach": 7,
        "banana": 5,
        "book": 8,
        "tv": 6,
        "computer": 9,
        "ski": 4,
        "ball": 3
    }

    for word, freq in dataset.items():
        trie.insert(word, freq)

    # 2 Создание и заполнение Priority Queue
    pq = PriorityQueue()
   
    # Поступают запросы
    pq.enqueue("a", priority=0)
    pq.enqueue("b", priority=1)

    # 3 Обработка запросов из очереди
    print("--- Порядок обработки запросов ---")
    while not pq.is_empty():
        priority, prefix = pq.dequeue()
        results = trie.autocomplete(prefix)
        user_type = "VIP" if priority == 1 else "Regular"
        print(f"Priority={priority} ({user_type}), Prefix='{prefix}' -> {results}")


benchmark(trie, n=10_000)