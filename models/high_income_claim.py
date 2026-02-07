class HighIncomeClaim:
    def __init__(self, salary):
        self.salary = salary

    def calculate_compensation(self):
        calculated = self.salary / 5
        return min(calculated, 20000)