class Claim:
    def __init__(self, salary):
        self.salary = salary

    def calculate_compensation(self):
        return min(self.salary, 20000)