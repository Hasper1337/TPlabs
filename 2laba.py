import turtle
'''
class LSystem: ## L-система
    def __init__(self, t, axiom, wight, length, angel):
        self.axiom = axiom
        self.state = axiom
        self.wight = wight
        self.length = length
        self.angel = angel
        self.t = t
        self.t.pensize(self.wight)
        self.rules = {}

    def add_rules(self, *rules):
        for key, value in rules:
            self.rules[key] = value

    def draw_turtle(self, start_pos, start_angle):
        turtle.tracer(1, 0)
        self.t.up()
        self.t.setpos(start_pos)
        self.t.seth(start_angle)
        self.t.down()

        for move in self.state:
            if move == 'F':
                self.t.forward(self.length)
            elif move == '+':
                self.t.left(self.angel)
            elif move == '-':
                self.t.right(self.angel)
        turtle.done()

    def generate_path(self, n_iner):
        for n in range(n_iner):
            for key, value in self.rules.items():
                self.state = self.state.replace(key, value)



if __name__ == '__main__':
    width = 1200
    height = 600
    screen = turtle.Screen()
    screen.setup(width, height, 0, 0)
    t = turtle.Turtle()
    t.ht()

    pen_width = 2
    f_len = 2
    angel = 60

    l_sys = LSystem(t, 'F--F--F', pen_width, f_len, angel)

    l_sys.add_rules(("F", "F+F--F+F"))
    l_sys.generate_path(5)
    l_sys.draw_turtle(start_pos=(0, 0), start_angle=0)
'''
def fractal(t, ln): ## Рекурсия
    if ln > 6:
        ln3 = ln // 3
        fractal(t, ln3)
        t.left(60)
        fractal(t, ln3)
        t.right(120)
        fractal(t, ln3)
        t.left(60)
        fractal(t, ln3)
    else:
        t.fd(ln)
        t.left(60)
        t.fd(ln)
        t.right(120)
        t.fd(ln)
        t.left(60)
        t.fd(ln)



if __name__ == '__main__':
    t = turtle.Turtle()
    t.ht()
    fractal(t, 100)
    turtle.done()
