import numpy as np
import random
import pandas as pd
from abc import ABC, abstractmethod

# Configuração para exibir todas as linhas do DataFrame
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# Criando a Matriz SWAP (100x6)
swap_matrix = np.zeros((100, 6), dtype=int)
swap_matrix[:, 0] = np.arange(100)  # Número da Página (N)
swap_matrix[:, 1] = np.arange(1, 101)  # Instrução (I)
swap_matrix[:, 2] = np.random.randint(1, 51, size=100)  # Dado (D)
swap_matrix[:, 3] = 0  # Bit de Acesso (R)
swap_matrix[:, 4] = 0  # Bit de Modificação (M)
swap_matrix[:, 5] = np.random.randint(100, 10000, size=100)  # Tempo de Envelhecimento (T)

# Criando a Matriz RAM (10x6)
def create_ram_matrix():
    ram_matrix = np.zeros((10, 6), dtype=int)
    random_indexes = random.sample(range(100), 10)  # Seleciona 10 índices aleatórios
    ram_matrix[:, :] = swap_matrix[random_indexes, :]
    return ram_matrix

# Classe Abstrata para Algoritmos de Substituição de Página
class PageReplacementAlgorithm(ABC):
    @abstractmethod
    def replace_page(self, ram_matrix):
        pass

# Implementações concretas dos algoritmos de substituição de página


class FIFO(PageReplacementAlgorithm):
    def replace_page(self, ram_matrix):
        return np.argmin(ram_matrix[:, 5])  # Substitui a página mais antiga

class NRU(PageReplacementAlgorithm):
    def replace_page(self, ram_matrix):
        nru_candidates = np.where((ram_matrix[:, 3] == 0) & (ram_matrix[:, 4] == 0))[0]
        return nru_candidates[0] if nru_candidates.size > 0 else FIFO().replace_page(ram_matrix)

class LRU(PageReplacementAlgorithm):
    def replace_page(self, ram_matrix):
        return np.argmin(ram_matrix[:, 5])  # Supondo T como contador de uso

class Clock(PageReplacementAlgorithm):
    def replace_page(self, ram_matrix):
        pointer = 0
        while True:
            if ram_matrix[pointer, 3] == 0:
                return pointer
            ram_matrix[pointer, 3] = 0  # Reseta bit de acesso
            pointer = (pointer + 1) % len(ram_matrix)

class WSClock(PageReplacementAlgorithm):
    def replace_page(self, ram_matrix):
        ep = random.randint(100, 9999)
        ws_clock_candidates = np.where(ram_matrix[:, 5] < ep)[0]
        return ws_clock_candidates[0] if ws_clock_candidates.size > 0 else FIFO().replace_page(ram_matrix)

class FIFOSC(PageReplacementAlgorithm):
    def replace_page(self, ram_matrix):
        for i in range(len(ram_matrix)):
            if ram_matrix[i, 3] == 0:
                return i
        return FIFO().replace_page(ram_matrix)

# Lista de algoritmos para teste
algorithms = [FIFO(), NRU(), LRU(), Clock(), WSClock(), FIFOSC()]

# Testando cada algoritmo
for algorithm in algorithms:
    ram_matrix = create_ram_matrix()
    print(f"\nExecutando algoritmo: {algorithm.__class__.__name__} ------------------------------------------------")

    print("\nMatriz SWAP Inicial:")
    print(pd.DataFrame(swap_matrix, columns=["N", "I", "D", "R", "M", "T"]))

    print("\nMatriz RAM Inicial:")
    print(pd.DataFrame(ram_matrix, columns=["N", "I", "D", "R", "M", "T"]))

    for instruction_count in range(1000):
        instruction = random.randint(1, 100)  # Sorteia uma instrução (I)
        match = np.where(ram_matrix[:, 1] == instruction)

        if match[0].size > 0:  # Caso a instrução esteja na RAM
            index = match[0][0]
            ram_matrix[index, 3] = 1  # Bit R = 1

            if random.random() < 0.5:  # 50% de chance de modificação
                ram_matrix[index, 2] += 1  # Atualiza Dado (D)
                ram_matrix[index, 4] = 1  # Bit M = 1
        else:
            index_to_replace = algorithm.replace_page(ram_matrix)
            page_to_replace = ram_matrix[index_to_replace]
            if page_to_replace[4] == 1:
                swap_matrix[page_to_replace[0]] = page_to_replace  # Salva a página modificada na SWAP
            new_page_index = random.choice(range(100))
            ram_matrix[index_to_replace] = swap_matrix[new_page_index]  # Carrega nova página na RAM

        if (instruction_count + 1) % 10 == 0:
            ram_matrix[:, 3] = 0  # Zera o Bit R a cada 10 instruções

    print("\nMatriz SWAP Final:")
    print(pd.DataFrame(swap_matrix, columns=["N", "I", "D", "R", "M", "T"]))

    print("\nMatriz RAM Final:")
    print(pd.DataFrame(ram_matrix, columns=["N", "I", "D", "R", "M", "T"]))
