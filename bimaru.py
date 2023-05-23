# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 00000 Nome1
# 00000 Nome2

import sys
from search import (
	Problem,
	Node,
	astar_search,
	breadth_first_tree_search,
	depth_first_tree_search,
	greedy_search,
	recursive_best_first_search,
)


class BimaruState:
	state_id = 0
	def __init__(self, board):
		self.board = board
		self.id = BimaruState.state_id
		BimaruState.state_id += 1

	def __lt__(self, other):
		return self.id < other.id
	


	

	# TODO: outros metodos da classe


class Board:
	"""Representação interna de um tabuleiro de Bimaru."""
	def __init__(self):
		self.matrix = [['.' for _ in range(10)] for _ in range(10)]
		self.boats = []
		self.rows = [] # barcos em falta na linha
		self.columns = [] # barcos em falta na coluna
		self.rows_pieces = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10] # peças em falta na linha
		self.columns_pieces = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10] # peças em falta na coluna


	def isValid(self, row: int, col: int):
		return 0 <= row <= 9 and 0 <= col <= 9

	def notEmpty(self, row: int, col: int):
		return self.matrix[row][col] != '.'

	def get_value(self, row: int, col: int) -> str:
		"""Devolve o valor na respetiva posição do tabuleiro."""
		if self.isValid(row, col) and self.notEmpty(row, col):
			return self.matrix[row][col] 
		else:
			return None

	def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
		"""Devolve os valores imediatamente acima e abaixo,
		respectivamente."""
		return (self.get_value(row-1, col), self.get_value(row+1, col))

	def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
		"""Devolve os valores imediatamente à esquerda e à direita,
		respectivamente."""
		return (self.get_value(row, col-1), self.get_value(row, col+1))

	def get_water_positions(self, row:int, col: int, type: str):
		positions = [(row-1, col-1), (row-1, col), (row, col-1), (row+1, col+1), (row+1, col), (row, col+1), (row+1, col-1), (row-1, col+1)]
		def valid_pos(pos):
			return self.isValid(pos[0], pos[1])
		positions = list(filter(valid_pos, positions))
		if type == 'T':
			positions.pop(positions.index((row+1, col)))
		elif type == 'B':
			positions.pop(positions.index((row-1, col)))
		elif type == 'L':
			positions.pop(positions.index((row, col+1)))
		elif type == 'R':
			positions.pop(positions.index((row, col-1)))
		elif type == 'M':
			vertical = self.adjacent_vertical_values(row, col)
			horizontal = self.adjacent_horizontal_values(row,col)
			if vertical[0] == 'W' or vertical[1] == 'W' or (horizontal[0] != 'W' and horizontal[0] != None) or (horizontal[1] != 'W' and horizontal[1] != None):
				positions.pop(positions.index((row, col-1)))
				positions.pop(positions.index((row, col+1)))
			if horizontal[0] == 'W' or horizontal[1] == 'W' or (vertical[0] != 'W' and vertical[0] != None) or (vertical[1] != 'W' and vertical[1] != None):
				positions.pop(positions.index((row+1, col)))
				positions.pop(positions.index((row-1, col)))
			if horizontal == (None, None) and vertical == (None, None):
				positions.pop(positions.index((row, col-1)))
				positions.pop(positions.index((row, col+1)))
				positions.pop(positions.index((row+1, col)))
				positions.pop(positions.index((row-1, col)))

		return positions

			
	def check_if_row_col_completed(self, row: int, col: int):
		"""Verifica se a linha e a coluna que foi alterada está terminada"""
		if self.rows[row] == 0: # verifica linha preenchida
			self.fill_water([[row, i] for i in range(10)])
		elif self.rows[row] == self.rows_pieces[row]: # preencher espaço em branco com peças
			pass
		if self.columns[col] == 0: # verifica coluna preenchida
			self.fill_water([[i, col] for i in range(10)])
		elif self.columns[col] == self.columns_pieces[col]: # preencher espaço em branco com peças
			pass
		

	
	def fill_water(self, cells):
		"""Preenche multiplas celas com água"""
		for cell in cells:
			row, col = cell
			if self.get_value(row,col) == None:
				self.matrix[row][col] = 'W'
				self.rows_pieces[row] -= 1
				self.columns_pieces[row] -= 1
				self.check_if_row_col_completed(row, col)
	
	
	def place_piece(self, row: int, col: int, type: str):
		if type == 'W':
			self.fill_water([(row, col)])
		else:
			self.matrix[row][col] = type
			self.rows[row] -= 1
			self.rows_pieces[row] -= 1
			self.columns[col] -= 1
			self.columns_pieces[col] -= 1
			self.check_if_row_col_completed(row, col)
			self.fill_water(self.get_water_positions(row, col, type))
			if type == 'T':
				if self.adjacent_vertical_values(row,col)[1] == None: # coloca peça abaixo do topo
					self.place_piece(row+1, col, 'U')
			elif type == 'B':
				if self.adjacent_vertical_values(row,col)[0] == None: # coloca peça acima do baixo
					self.place_piece(row-1, col, 'U')
			elif type == 'L':
				if self.adjacent_horizontal_values(row,col)[1] == None: 
					self.place_piece(row, col+1, 'U')
			elif type == 'R':
				if self.adjacent_horizontal_values(row,col)[0] == None: 
					self.place_piece(row, col-1, 'U')
			elif type == 'M':
				horizontal = self.adjacent_horizontal_values(row,col)
				vertical = self.adjacent_vertical_values(row,col)
				if horizontal[0] == 'W' or horizontal[1] == 'W' or not self.isValid(row,col-1) or not self.isValid(row,col+1):
					self.place_piece(row-1, col, 'U')
					self.place_piece(row+1, col, 'U')
				if vertical[0] == 'W' or vertical[1] == 'W' or not self.isValid(row-1,col) or not self.isValid(row+1,col):
					self.place_piece(row, col-1, 'U')
					self.place_piece(row, col+1, 'U')


	def preload_board(self):
		for i in range(10):
			if self.rows[i] == 0: # verifica se a linha está completa
				self.fill_water([[i, j] for j in range(10)])
		for i in range(10):
			if self.columns[i] == 0: # verifica se a coluna está completa
				self.fill_water([[j, i] for j in range(10)])
			

	

	
	def print_board(self):
		"""Imprime o tabuleiro"""
		i = 0
		for line in self.matrix:
			print(' '.join(line) + ' ' + str(self.rows[i]))
			i += 1
		list_columns = [str(num) for num in self.columns]
		print(' '.join(list_columns))


	@staticmethod
	def parse_instance():
		"""Lê o test do standard input (stdin) que é passado como argumento
		e retorna uma instância da classe Board."""
		board = Board()
		board.rows = [int(i) for i in sys.stdin.readline().split()[1:]]
		board.columns = [int(i) for i in sys.stdin.readline().split()[1:]]
		hints = int(sys.stdin.readline())
		board.preload_board()
		for i in range(hints):
			hint = sys.stdin.readline().split()[1:]
			row = int(hint[0])
			col = int(hint[1])

			val = hint[2]
			board.place_piece(row,col,val)
			

		
		# faz o pre-processamento inicial

		#board.preload_board()
		board.print_board()
		return board

	# TODO: outros metodos da classe


class Bimaru(Problem):
	def __init__(self, board: Board):
		"""O construtor especifica o estado inicial."""
		super().__init__(BimaruState(board))

	def actions(self, state: BimaruState):
		"""Retorna uma lista de ações que podem ser executadas a
		partir do estado passado como argumento."""
		# Ações que podem ser tomada:
		# - verifica se pode pôr barcos
		# - 
		# TODO
		pass

	def result(self, state: BimaruState, action):
		"""Retorna o estado resultante de executar a 'action' sobre
		'state' passado como argumento. A ação a executar deve ser uma
		das presentes na lista obtida pela execução de
		self.actions(state)."""
		# TODO
		pass

	def goal_test(self, state: BimaruState):
		"""Retorna True se e só se o estado passado como argumento é
		um estado objetivo. Deve verificar se todas as posições do tabuleiro
		estão preenchidas de acordo com as regras do problema."""
		# TODO
		pass

	def h(self, node: Node):
		"""Função heuristica utilizada para a procura A*."""
		# TODO
		pass

	# TODO: outros metodos da classe


if __name__ == "__main__":

	board = Board().parse_instance()

	# TODO:

	# Usar uma técnica de procura para resolver a instância,
	# Retirar a solução a partir do nó resultante,
	# Imprimir para o standard output no formato indicado.
