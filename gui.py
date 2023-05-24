import tkinter as tk
from tkinter import font
from tkinter import simpledialog


class Application(tk.Tk):
	def __init__(self, matrix, rows, columns):
		super().__init__()
		self.title("Bimaru - Visualizador")
		self.resizable(False, False)
		self.matrix = matrix
		self.rows = rows
		self.columns = columns
		
		self.geometry("635x834")
		self.configure(bg="#a4d5ff")

		self.canvas = tk.Canvas(self, width=635, height=570+58, bg="#a4d5ff", highlightthickness=0, borderwidth=0,highlightbackground="#127bc7", relief='flat')
		self.canvas.pack()
		self.agua = tk.PhotoImage(file="img/agua.png")
		self.cima = tk.PhotoImage(file="img/cima.png")
		self.baixo = tk.PhotoImage(file="img/baixo.png")
		self.temporario = tk.PhotoImage(file="img/pequeno.png")
		self.direita = tk.PhotoImage(file="img/direita.png")
		self.esquerda = tk.PhotoImage(file="img/esquerda.png")
		self.centro = tk.PhotoImage(file="img/meio.png")
		self.circulo = tk.PhotoImage(file="img/circulo.png")
		self.create_grid()

	def create_grid(self):
		def get_color(n):
			if n > 0:
				return "#1b1b1b"
			else:
				return "#848b93"
		cell_width = 57
		cell_height = 57
		for row in range(11):
			for col in range(11):
				x1 = col * cell_width
				y1 = row * cell_height
				x2 = x1 + cell_width
				y2 = y1 + cell_height
				if row == 10 and col == 10:
					self.canvas.create_rectangle(x1, y1, x2, y2, outline="#127bc7", width="0")
				elif row == 10:
					text_x = (x1 + x2) // 2
					text_y = (y1 + y2) // 2
					self.canvas.create_rectangle(x1, y1, x2, y2, outline="#127bc7", width="0")
					self.canvas.create_text(text_x, text_y, text=self.columns[col], font=("Arial", 22), fill=get_color(self.columns[col]))
				elif col == 10:
					text_x = (x1 + x2) // 2
					text_y = (y1 + y2) // 2
					self.canvas.create_rectangle(x1, y1, x2, y2, outline="#127bc7", width="0")
					self.canvas.create_text(text_x, text_y, text=self.rows[row], font=("Arial", 22), fill=get_color(self.rows[row]))
				else:
					self.canvas.create_rectangle(x1, y1, x2, y2, outline="#127bc7", width="3")
					image_x = (x1 + x2) // 2
					image_y = (y1 + y2) // 2
					image = ''
					if self.matrix[row][col] == 'W':
						image = self.agua
					elif self.matrix[row][col] == 'T':
						image = self.cima
					elif self.matrix[row][col] == 'B':
						image = self.baixo
					elif self.matrix[row][col] == 'R':
						image = self.direita
					elif self.matrix[row][col] == 'E':
						image = self.esquerda
					elif self.matrix[row][col] == 'C':
						image = self.circulo
					elif self.matrix[row][col] == 'M':
						image = self.centro
					elif self.matrix[row][col] == 'L':
						image = self.esquerda
					self.canvas.create_image(image_x, image_y, anchor="center", image=image)