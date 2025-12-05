import random

class Sudoku:
    def __init__(self, level=2):
        self.grid = [[0]*9 for _ in range(9)]
        self.nums_for_delete = 81 - self.dificult_definition(level)


    def is_valid(self, num, row, col):
        if num in self.grid[row] or any(self.grid[r][col] == num for r in range(9)):
            return False
        square_row, square_vertical = (row//3)*3, (col//3)*3
        return all(self.grid[r][c] != num for r in range(square_row, square_row+3) for c in range(square_vertical, square_vertical+3))


    def fill_grid(self):
        for row in range(9):
            for col in range(9):
                if self.grid[row][col] == 0:
                    for num in random.sample(range(1,10), 9):
                        if self.is_valid(num, row, col):
                            self.grid[row][col] = num
                            if self.fill_grid():
                                return True
                            self.grid[row][col] = 0
                    return False
        return True


    def dificult_definition(self, level):
        if level == 1: return random.randint(45, 65)
        if level == 2: return random.randint(24, 44)
        if level == 3: return random.randint(17, 23)
        if level == 4: return 80


    def del_nums(self):
        positions = [(row, ver) for row in range(9) for ver in range(9)]
        random.shuffle(positions)
        for row, ver in positions[:self.nums_for_delete]:
            self.grid[row][ver] = 0


    def print_grid(self):
        for row in self.grid:
            print(" ".join(str(num) for num in row))
        

    def get_grid(self):
        return self.grid


    def create_sudoku(self):
        self.fill_grid()
        self.del_nums()



