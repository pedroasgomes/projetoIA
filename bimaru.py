# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 120:
# 103468 Pedro Gomes
# 104156 Henrique Pimentel

import sys

from search import (
	Problem,
	Node,
	depth_first_graph_search,
)


class BimaruState:
	state_id = 0

	def __init__(self, board):
		self.board = board
		self.id = BimaruState.state_id
		BimaruState.state_id += 1

	def __lt__(self, other):
		return self.id < other.id


class Board:
	"""Representação interna de um tabuleiro de Bimaru."""

	def __init__(self):
		self.matrix = [['.' for _ in range(10)] for _ in range(10)]
		self.unexplored_hints = []
		self.bpieces_left_row = []
		self.bpieces_left_col = []
		self.empty_spaces_row = [10 for _ in range(10)]
		self.empty_spaces_col = [10 for _ in range(10)]
		self.boats = [4, 3, 2, 1]  # Where self.boats[size-1] = número de barcos que faltam por de tamanho 'size'
		self.hints = []

	def copy_board(self):
		board = Board()
		for i in range(10):
			board.matrix[i] = self.matrix[i][:]
		board.unexplored_hints = self.unexplored_hints[:]
		board.bpieces_left_row = self.bpieces_left_row[:]
		board.bpieces_left_col = self.bpieces_left_col[:]
		board.empty_spaces_row = self.empty_spaces_row[:]
		board.empty_spaces_col = self.empty_spaces_col[:]
		board.boats = self.boats[:]

		board.hints = self.hints[:]

		return board

	def __str__(self):
		"""Transforma board em string"""
		string = ""
		for row in range(10):
			for col in range(10):
				type = self.matrix[row][col]
				if (row, col) in self.hints:
					string += type.upper()
				else:
					if type == 'w':
						string += '.'
					else:
						string += type
			if row != 9:
				string += '\n'
		return string

	# ------------------------- Getters -------------------------
	def get_value(self, row: int, col: int):
		"""Devolve o valor na respetiva posição do tabuleiro. Se estiver
		fora retorna None, se não houver peca retorna '_' """
		if 0 <= row <= 9 and 0 <= col <= 9:
			return self.matrix[row][col]
		else:
			return None

	def get_adjacent_vertical_values(self, row: int, col: int):
		"""Devolve os valores imediatamente acima e abaixo"""
		return self.get_value(row - 1, col), self.get_value(row + 1, col)

	def get_adjacent_horizontal_values(self, row: int, col: int):
		"""Devolve os valores imediatamente à esquerda e à direita"""
		return self.get_value(row, col - 1), self.get_value(row, col + 1)

	# ------------------------- Low level functions -------------------------

	def add_piece(self, row: int, col: int, piece: str):
		if self.is_boat_piece(piece):
			self.bpieces_left_row[row] -= 1
			self.bpieces_left_col[col] -= 1
		self.empty_spaces_row[row] -= 1
		self.empty_spaces_col[col] -= 1
		self.matrix[row][col] = piece

	def add_hint(self, row: int, col: int, piece: str):
		if piece == 'w':
			if self.get_value(row, col) == '.':
				self.add_piece(row, col, piece)
		elif piece == 'c':
			self.place_boat(row, col, 1, 0, 0)
		else:
			self.add_piece(row, col, piece)
			self.unexplored_hints.append((row, col, piece))

	def is_hints_empty(self):
		return not self.unexplored_hints

	def isCenterBoat(self, row: int, col: int):
		return all(value in ('w', None) for value in self.get_adjacent_horizontal_values(row, col)) and \
			all(value in ('w', None) for value in self.get_adjacent_vertical_values(row, col))

	# ------------------------- Static functions -------------------------

	@staticmethod
	def parse_instance():
		"""Lê o test do standard input (stdin) passado como argumento
		e retorna uma instância da classe Board."""

		board = Board()
		rows = sys.stdin.readline().split()
		columns = sys.stdin.readline().split()

		for i in range(10):
			board.bpieces_left_row.append(int(rows[i + 1]))  # Guarda o número total de peças por colocar na row[i]
			board.bpieces_left_col.append(int(columns[i + 1]))  # Guarda o número total de peças por colocar na col[i]

		number_hints = sys.stdin.readline().split()
		middle_hint = []
		for j in range(int(number_hints[0])):
			hint = sys.stdin.readline().split()
			board.hints.append((int(hint[1]), int(hint[2])))
			if hint[3] == 'M':
				middle_hint.append((int(hint[1]), int(hint[2])))
			else:
				board.add_hint(int(hint[1]), int(hint[2]), str(hint[3]).lower())
		for hint in middle_hint:
			board.add_hint(hint[0], hint[1], 'm')  # evita um sort

		board.logic_away()  # TODO OOOOOOOOOOOOOOOOOO 1337
		return board

	def is_hint_piece(self, row: int, col: int):
		return (row, col) in self.hints

	@staticmethod
	def is_boat_piece(piece: str):
		return piece in ['c', 't', 'b', 'l', 'r', 'm', 'u']

	# =========================== Upper level functions ===========================

	def flood_lines(self):
		for i in range(10):
			if self.bpieces_left_row[i] == 0 and self.empty_spaces_row[i] != 0:
				for j in range(10):
					if self.matrix[i][j] == '.':
						self.add_piece(i, j, 'w')
			if self.bpieces_left_col[i] == 0 and self.empty_spaces_col[i] != 0:
				for j in range(10):
					if self.matrix[j][i] == '.':
						self.add_piece(j, i, 'w')

	def marshal_lines(self):

		boats = []
		new_boats = [0, 0, 0, 0]
		new_hints = []

		for i in range(10):
			row = i
			if self.bpieces_left_row[row] == self.empty_spaces_row[
				row] != 0:  # Verifica se os espaços restantes da linha são barcos
				col = 0
				while col < 10:
					size = 0
					hints = 0

					while True:
						value = self.get_value(row, col + size)
						if value == '.' or (value == 'm' and self.is_hint_piece(row, col + size)):
							hints += 1
						elif value != '.':
							break
						size += 1

					if size == 0:
						col += 1

					elif size == 1:
						value = self.get_value(row, col)
						if value == '.' or value == 'u':
							# É peça circular
							if self.isCenterBoat(row, col):
								new_boats[size - 1] += 1
								if self.boats[size - 1] - new_boats[size - 1] < 0:
									return 1
								boats.append((row, col, size, 0, hints))
							elif value == '.':
								new_hints.append((row, col, 'u'))
						col += size

					elif 2 <= size <= 4:  # Navios de 2 a 4
						new_boats[size - 1] += 1
						if self.boats[size - 1] - new_boats[size - 1] < 0:
							return 1
						boats.append((row, col, size, 0, hints))
						col += size

					elif size > 4:  # barcos maiores que 4
						return 1

			col = i
			if self.bpieces_left_col[col] == self.empty_spaces_col[col] != 0:
				row = 0
				while row < 10:
					size = 0
					hints = 0

					while True:
						value = self.get_value(row + size, col)
						if value == 'u' or (value == 'm' and self.is_hint_piece(row + size, col)):
							hints += 1
						elif value != '.':
							break
						size += 1

					if size == 0:
						row += 1

					elif size == 1:
						value = self.get_value(row, col)

						if value == '.' or value == 'u':
							if any(boat[0] == row and boat[1] == col for boat in boats):
								pass
							elif self.isCenterBoat(row, col):
								new_boats[size - 1] += 1
								if self.boats[size - 1] - new_boats[size - 1] < 0:
									return 1
								boats.append((row, col, size, 1, hints))
							elif value == '.':
								new_hints.append((row, col, 'u'))
						row += size

					elif 2 <= size <= 4:  # Navios de 2 a 4
						new_boats[size - 1] += 1
						if self.boats[size - 1] - new_boats[size - 1] < 0:
							return 1
						boats.append((row, col, size, 1, hints))
						row += size

					elif size > 4:  # B
						return 1

		if len(boats) == 0:
			if len(new_hints) == 0:
				return 2
			else:
				for new_hint in new_hints:
					row, col, piece = new_hint
					self.add_hint(row, col, piece)

		for boat in boats:
			row, col, size, orientation, hints = boat
			if self.place_boat(row, col, size, orientation, hints):
				return 1

		return 0

	def logic_away(self):

		self.flood_lines()
		while True:
			result = self.marshal_lines()
			if result == 0:
				self.flood_lines()
			elif result == 1:
				return 1
			elif result == 2:
				break

		return 0

	def place_boat(self, row: int, col: int, size: int, orientation: int, hints: int):
		""" Signigicado das hints é: peças que pertencem ao barco e ja se encontram no tabuleiro e ja têm os
		valores em consideracao no cálculo da informacao das linhas e colunas

		"""

		# Verifica se o barco dado é valido
		if self.boat_not_valid(row, col, size, orientation, hints):
			return 1

		# Atualiza o número de barcos que faltam para o respetivo tamanho (nunca é < 0)
		self.boats[size - 1] -= 1

		# Boat of size 1
		if size == 1:
			if self.place_boat_single(row, col):
				return 1
		# Vertical Orientation of size > 2
		elif orientation:
			if self.place_boat_long_vertical(row, col, size):
				return 1
		# Horizontal Orientation of size > 2
		else:
			if self.place_boat_long_horizontal(row, col, size):
				return 1

		return 0

	def boat_not_valid(self, row: int, col: int, size: int, orientation: int, hints: int):
		""" Verifica se o barco dado como 'input' não viola regras triviais de barcos """

		# Verifica se o novo barco (vertical) não ultrapassa o limite da respetiva coluna
		# [As hints incluidas não são tidas em conta já que são contablizamos na criação]
		if orientation and (size - hints) > self.bpieces_left_col[col]:
			return True

		# Verifica se o novo barco (horizontal) não ultrapassa o limite da respetiva linha
		# [As hints incluidas não são tidas em conta já que são contablizadas na criação]
		elif not orientation and (size - hints) > self.bpieces_left_row[row]:
			return True

		# Verifica se o novo barco (vertical) não se extende para fora do tabuleiro
		elif orientation and (row < 0 or size + row > 10):  # is vertical
			return True

		# Verifica se o novo barco (horizontal) não se extende para fora do tabuleiro
		elif not orientation and (col < 0 or size + col > 10):  # is horizontal
			return True

		# Verifica se o tamanho do barco respeita as regras (max size = 4)
		elif size > 4:
			return True

		# Verifica se já foram colocados todos os barcos do tamanho dado como ‘input’
		elif self.boats[size - 1] <= 0:
			return True

		return False

	def place_boat_single(self, row: int, col: int):

		if self.place_boat_line(row - 1, col, 'w', 0):  # [ '.' '.' '.'] -> [ 'w' 'w' 'w' ]
			return 1
		if self.place_boat_line(row, col, 'c', 0):  # [ '.' '.' '.'] -> [ 'w' 'c' 'w' ]
			return 1
		if self.place_boat_line(row + 1, col, 'w', 0):  # [ '.' '.' '.'] -> [ 'w' 'w' 'w' ]
			return 1

	def place_boat_long_vertical(self, row: int, col: int, size: int):

		if self.place_boat_line(row - 1, col, 'w', 0):  # [ '.' '.' '.'] -> [ 'w' 'w' 'w' ]
			return 1
		if self.place_boat_line(row, col, 't', 0):  # [ '.' '.' '.'] -> [ 'w' 't' 'w' ]
			return 1
		if self.place_boat_line(row + (size - 1), col, 'b', 0):  # [ '.' '.' '.'] -> [ 'w' 'b' 'w' ]
			return 1
		if self.place_boat_line(row + size, col, 'w', 0):  # [ '.' '.' '.'] -> [ 'w' 'w' 'w' ]
			return 1

		for i in range(size - 2):
			if self.place_boat_line(row + 1 + i, col, 'm', 0):  # [ '.' '.' '.'] -> [ 'w' 'm' 'w' ]
				return 1

	def place_boat_long_horizontal(self, row: int, col: int, size: int):

		if self.place_boat_line(row, col - 1, 'w', 1):  # [ '.' '.' '.']^T -> [ 'w' 'w' 'w' ]^T
			return 1
		if self.place_boat_line(row, col, 'l', 1):  # [ '.' '.' '.']^T -> [ 'w' 'l' 'w' ]^T
			return 1
		if self.place_boat_line(row, col + (size - 1), 'r', 1):  # [ '.' '.' '.']^T -> [ 'w' 'r' 'w' ]^T
			return 1
		if self.place_boat_line(row, col + size, 'w', 1):  # [ '.' '.' '.']^T -> [ 'w' 'w' 'w' ]^T
			return 1

		for i in range(size - 2):
			if self.place_boat_line(row, col + 1 + i, 'm', 1):  # [ '.' '.' '.']^T -> [ 'w' 'm' 'w' ]^T
				return 1

	def place_boat_line(self, row: int, col: int, piece: str, direction: int):

		water_pieces = [-1, 1]

		if self.is_boat_piece(piece):
			value = self.get_value(row, col)
			if value == '.':
				self.add_piece(row, col, piece)
			elif self.is_boat_piece(value):
				if (row, col, piece) in self.unexplored_hints:
					self.unexplored_hints.remove((row, col, value))
					pass
				elif value == 'u':
					self.unexplored_hints.remove((row, col, value))
					self.matrix[row][col] = piece
				else:
					return 1
		elif piece == 'w':
			water_pieces.append(0)

		new_row = row
		new_col = col
		for i in water_pieces:
			if direction:  # Itera sobre a mesma coluna
				new_row = row + i
			else:  # Itera sobre a mesma linha
				new_col = col + i
			value = self.get_value(new_row, new_col)
			if value == None or value == 'w':
				continue
			if value == '.':
				self.add_piece(new_row, new_col, 'w')
			elif self.is_boat_piece(value):
				return 1

		return 0

	# ----------------------- Helper functions for Actions -----------------------

	def get_hint_based_actions(self):  # Retorna uma ou mais actions com um unico move

		hints = 1
		actions = []

		for hint in self.unexplored_hints:
			row, col, piece = hint

			if piece == 'm':
				pass
			elif piece == 'u':
				if self.isCenterBoat(row, col):
					actions.append((row, col, 1, 0, hints))
					return actions
			elif piece == 'c':
				actions.append((row, col, 1, 0, hints))
				return actions
			else:
				for i in range(1, 4):
					if self.boats[i] > 0:
						size = i+1
						if piece == 't':
							next_piece = str(self.get_value(row + size - 1, col)).lower()
							restrictions = ('w', 'r', 'l', 't', 'c')
							coords = (row, col, i + 1, 1)
							opposite_piece = 'b'
							continue_pieces = ('m', 'u')
						elif piece == 'b':
							next_piece = str(self.get_value(row - size + 1, col)).lower()
							restrictions = ('w', 'r', 'l', 'b', 'c')
							coords = (row - size + 1, col, i + 1, 1)
							opposite_piece = 't'
							continue_pieces = ('m', 'u')
						elif piece == 'l':
							next_piece = str(self.get_value(row, col+size-1)).lower()
							restrictions = ('w', 'l', 't', 'b', 'c')
							coords = (row, col, i + 1, 0)
							opposite_piece = 'r'
							continue_pieces = ('m', 'u')
						elif piece == 'r':
							next_piece = str(self.get_value(row, col - size + 1)).lower()
							restrictions = ('w', 'r', 't', 'b', 'c')
							coords = (row,  col - size + 1, i + 1, 0)
							opposite_piece = 'l'
							continue_pieces = ('m', 'u')
						else:
							continue

						if next_piece in restrictions:
							break
						elif next_piece == '.':
							actions.append((coords[0], coords[1], coords[2], coords[3], hints))
						elif next_piece == opposite_piece:
							hints += 1
							actions.append((coords[0], coords[1], coords[2], coords[3], hints))
							return actions
						elif next_piece in continue_pieces:
							hints += 1

			return actions

	def get_guess_boats_row(self, row: int, size: int):

		actions = []
		hints = 0

		col = 0
		while col < 10:
			max_size = 0
			value = self.get_value(row, col)
			if value == '.' or value == 'u':
				while True:
					value = self.get_value(row, col + max_size)
					if value == 'u' or value == 'm':
						hints += 1
					elif value != '.':
						break
					max_size += 1

				if max_size >= size:
					for delta in range(0, max_size - size + 1):
						actions.append((row, col + delta, size, 0, hints))
			col += max_size + 1
		return actions

	def get_guess_boats_col(self, col: int, size: int):

		actions = []
		hints = 0

		row = 0
		while row < 10:
			max_size = 0
			value = self.get_value(row, col)
			if value == '.' or value == 'u':
				while True:
					value = self.get_value(row + max_size, col)
					if value == 'u' or value == 'm':
						hints += 1
					elif value != '.':
						break
					max_size += 1

				if max_size >= size:
					for delta in range(0, max_size - size + 1):
						actions.append((row + delta, col, size, 1, hints))

			row += max_size + 1

		return actions

	def get_guess_based_actions(self):  # Retorna uma ou mais actions com um unico move

		if self.boats == [0, 0, 0, 0]:
			return []

		size = 4
		while self.boats[size - 1] == 0:
			size -= 1

		possible_rows = []
		possible_cols = []
		actions = []

		hints_rows = [0 for _ in range(10)]
		hints_cols = [0 for _ in range(10)]

		for hint in self.unexplored_hints:
			row, col, piece = hint
			hints_rows[row] += 1
			hints_cols[col] += 1

		for coordinate in range(10):

			if self.bpieces_left_row[coordinate] >= size - hints_rows[coordinate]:  # UNICAS ROWS POSSIVEIS
				possible_rows.append(coordinate)

			if self.bpieces_left_col[coordinate] >= size - hints_cols[coordinate]:  # UNICAS COLS POSSIVEIS
				possible_cols.append(coordinate)

		# AGORA É SÓ VER DENTRO DESSAS QUAIS SÃO OS BOATS DE SIZE POSSIBEL, SE É QUE EXISTEM

		for row in possible_rows:
			actions.extend(self.get_guess_boats_row(row, size))
		for col in possible_cols:
			actions.extend(self.get_guess_boats_col(col, size))

		return actions


class Bimaru(Problem):
	def __init__(self, board: Board):
		"""O construtor especifica o estado inicial."""
		super().__init__(BimaruState(board))

	def actions(self, state: BimaruState):
		"""Retorna uma lista de ações que podem ser executadas a partir
		do estado passado como argumento. Retorna None quando nao consegue
		encontrar uma unica jogada para devolver como ação. Uma açãoo
		pode ser várias jogadas consecutivas caso uma das jogadas cause uma
		chain reaction obrigatória. A funcao action pode entao retornar varias
		actions e cada action pode ter varias jogadas em cadeia. A funcao result
		aceita então um tuplo de jogadas. OU SEJA UMA ACAO E UM TUPLO DE JOGADAS"""

		if state is None:
			return []

		if not state.board.is_hints_empty():
			actions = state.board.get_hint_based_actions()  # Retorna uma unica action com 1 move
			if len(actions) > 0:
				return actions

		actions = state.board.get_guess_based_actions()  # Retorna varias actions com 1 move
		return actions

	def result(self, state: BimaruState, action):
		"""Retorna o estado resultante de executar a 'action' sobre
		'state' passado como argumento. A ação a executar deve ser uma
		das presentes na lista obtida pela execução de
		self.actions(state)."""

		new_board = state.board.copy_board()
		row, col, size, orientation, hints = action

		if new_board.place_boat(row, col, size, orientation, hints) or new_board.logic_away():
			return None

		return BimaruState(new_board)

	def goal_test(self, state: BimaruState):
		"""Retorna True se e só se o estado passado como argumento é
		um estado objetivo. Deve verificar se todas as posições do tabuleiro
		estão preenchidas conforme as regras do problema."""

		# Verifica se é um estado válido
		if state is None:
			return False

		# Verifica se todos os barcos foram colocados
		for i in range(4):
			if state.board.boats[i] != 0:
				return False

		# Verifica se todas as colunas e linhas estão cheias e com o número de peças de barco correto
		for coordenada in range(10):
			if (state.board.bpieces_left_row[coordenada] != 0) or \
					(state.board.bpieces_left_col[coordenada] != 0) or \
					(state.board.empty_spaces_row[coordenada] != 0) or \
					(state.board.empty_spaces_col[coordenada] != 0):
				return False

		return True

	def h(self, node: Node):
		"""Função heuristica utilizada para a procura A*."""
		# TODO
		pass


if __name__ == "__main__":
	# TODO:
	# Ler o ficheiro do standard input,
	# Usar uma técnica de procura para resolver a instância,
	# Retirar a solução a partir do nó resultante,
	# Imprimir para o standard output no formato indicado.
	board = Board.parse_instance()
	problem = Bimaru(board)
	initial_state = BimaruState(board)
	goal_node = depth_first_graph_search(problem)

	print(goal_node.state.board, sep="")