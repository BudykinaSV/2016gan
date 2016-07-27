from tkinter import *
from random import choice, randint
from math import*
from tkinter import messagebox

screen_width = 400
screen_height = 400
timer_delay = 20
initial_number = 20
time_limit = 20# время игры

class Ball:
    """
    Абстрактный класс -- предок для шариков-мишеней и для снарядов.
    Имеет атрибуты x, y, Vx, Vy, R, avatar
    а также метод fly -- абстрактный (т.е. его нельзя реально вызывать)
    """
    def __init__(self, x, y, Vx, Vy, R, avatar):

        self._R = R
        self._x = x
        self._y = y
        self._Vx = Vx
        self._Vy = Vy
        self._avatar = avatar

    def fly(self):
        """
        Абстрактный метод! Нельзя вызывать.
        Требуется реализовывать в классах-потомках.
        """
        raise RuntimeError()

    def delete(self): # удаление объекта
        canvas.delete(self._avatar)

class Target(Ball):
    """
    Мишень, шары разного цвета и диаметра, отражающиеся от стен
    """
    minimal_radius = 15
    maximal_radius = 30
    available_colors = ['green', 'blue', 'red', 'yellow']

    def __init__(self):
        """
        Cоздаёт шарик в случайном месте игрового холста canvas,
        при этом шарик не выходит за границы холста!
        """
        R = randint(Target.minimal_radius, Target.maximal_radius)
        x = randint(0, screen_width-1-2*R)
        y = randint(0, screen_height-1-2*R)
        color = choice(Target.available_colors)
        avatar = canvas.create_oval(x, y, x+2*R, y+2*R,
                                          width=1, fill=color,
                                          outline=color)
        Vx = 0
        while Vx ==0:
            Vx = randint(-2, 2)
        Vy = 0
        while Vy ==0:
            Vy = randint(-2, 2)
        super().__init__(x, y, Vx, Vy, R, avatar)

    def fly(self):
        self._x += self._Vx
        self._y += self._Vy
        # отбивается от горизонтальных стенок
        if self._x < 0:
            self._x = 0
            self._Vx = -self._Vx
        elif self._x + 2*self._R >= screen_width:
            self._x = screen_width - 2*self._R
            self._Vx = -self._Vx
        # отбивается от вертикальных стенок
        if self._y < 0:
            self._y = 0
            self._Vy = -self._Vy
        elif self._y + 2*self._R >= screen_height:
            self._y = screen_height - 2*self._R
            self._Vy = -self._Vy
        canvas.coords(self._avatar, self._x, self._y,
                      self._x + 2*self._R, self._y + 2*self._R)

    def delete(self): # удаление экземпляра
        canvas.delete(self._avatar)

class Shell(Ball):
    """
    Снаряд, вылетающий из пушки.
    Не отражается от стенок, уничтожается, если вылетел за пределы поля.
    Двигается по гравитационной траектории.
    """
    color = 'black'

    def __init__(self, x, y, Vx, Vy):
        R = 5
        avatar = canvas.create_oval(x, y, x+2*R, y+2*R, width=1, fill=Shell.color,
                                          outline=Shell.color)
        super().__init__(x, y, Vx, Vy, R, avatar)

    def fly(self):
        ax = 0
        ay = 0
        dt = 2  # квант физического времени
        self._x += self._Vx*dt + ax*dt**2/2
        self._y += self._Vy*dt + ay*dt**2/2
        self._Vx += ax*dt
        self._Vy += ay*dt
        canvas.coords(self._avatar, self._x, self._y,
                      self._x + 2*self._R, self._y + 2*self._R)
class Gun:
    def __init__(self):
        self._x = 0
        self._y = screen_height
        self.lx = 30
        self.ly = -30
        self.avatar = canvas.create_line(self._x, self._y, self._x+self.lx, self._y+self.ly,width=4)

    def shoot(self):
        """  :return возвращает объект снаряда (класса Shell) по щелчку мышки
        """
        x = self._x - 5 + self.lx
        y = self._y - 5+ self.ly
        Vx = self.lx/10
        Vy = self.ly/10
        shell = Shell(x, y, Vx, Vy)
        shell.fly()
        return shell

    def move(self,dx,dy):
        """Движение пушки за мышкой"""
        dy = self._y-dy
        r = sqrt(dx**2+dy**2)
        self.lx =int(42*(dx/r))
        self.ly = -int(42*(dy/r))
        canvas.delete(self.avatar)
        self.avatar = canvas.create_line(self._x, self._y, self._x+self.lx, self._y+self.ly,width=4)

def init_game():
    """     Создаём необходимое для игры количество объектов-шариков,
    а также объект - пушку.    """
    global balls, gun, shells_on_fly
    balls = [Target() for i in range(initial_number)]
    gun = Gun()
    shells_on_fly = []

def move_gun(event):
    if 1 < event.x < screen_width and 1 < event.y < screen_height:
        gun.move(event.x, event.y)

def meeting(event):
    global goals_value
    count = False
    for ball in balls:
        # Проверяем, соприкасаются ли снаряд и мяч
        if ((ball._x+ball._R)-(event._x+event._R))**2+((ball._y+ball._R)-(event._y+event._R))**2<(ball._R+event._R)**2:
            index = balls.index(ball)
            if ball._R>25:
                goals_value.set(goals_value.get()+1)
            elif ball._R>20:
                goals_value.set(goals_value.get()+2)
            else:
                goals_value.set(goals_value.get()+3)
            balls.pop(index)
            ball.delete()
            count =True #если произощло столкновение, фиксируем
    return count

def click_event_handler(event):
    global shells_on_fly
    shell = gun.shoot()
    shells_on_fly.append(shell)
    shell_value.set(shell_value.get()+1)

def timer_event():
    # все периодические рассчёты, которые я хочу, делаю здесь
    for ball in balls:
        ball.fly()
    for shell in shells_on_fly:
        # Проверка вылета снаряда за пределы поля
        if shell._x+shell._Vx+10>screen_width or shell._y+shell._Vy<0 or  shell._x - shell._Vx<0 or shell._y + shell._Vy>screen_height:
            shell.delete()
        elif meeting(shell):
            index = shells_on_fly.index(shell)
            shells_on_fly.pop(index)
            shell.delete()
        else:
            shell.fly()
    canvas.after(timer_delay, timer_event)

def close_win():
    root.destroy()

def rules():
    rule = "На поле движется 20 шариков\n Надо сбить шарики как можно меньшим числом снарядов\n "
    rule +='Чем мешьше шарик, тем больше очков за него дается\n '
    rule +='Движение курсора мышки управляет поворотом пушки\n '
    rule +='Снаряд выпускается по щелчку левой клавиши мышки\n '
    tex = messagebox.showinfo("Правила игры",rule)

def init_menu():# создание меню
    m = Menu(root)
    root.config(menu = m)
    fm = Menu(m)
    m.add_cascade(label="Меню", menu=fm)
    fm.add_command(label="Правила игры", command=rules)
    fm.add_command(label="Выход", command=close_win)

def init_frame():
    global canvas, goals_text, goals_value, shell_value
    frame =Frame(root)
    goals_value = IntVar()
    shell_value = IntVar()
    goals_text = Label(frame, text='Число набранных очков', font='Calibri 14')
    goals_text.grid(row=0, column=0 )
    goals_count = Label(frame, width=5,bg='white', textvariable=goals_value, font='Calibri 14')
    goals_count.grid(row=0, column=1)
    shell_text = Label(frame, text='Число выпущенных снарядов', font='Calibri 14')
    shell_text.grid(row=1, column=0)
    shell_count = Label(frame,width=5, bg='white', textvariable=shell_value, font='Calibri 14')
    shell_count.grid(row=1, column=1)
    canvas = Canvas(frame, width=screen_width, height=screen_height,bg="white")
    canvas.grid(row=2, column=0, columnspan=2)
    frame.pack()


def init_main_window():
    global root, canvas
    root = Tk()
    root.title("Пушка")
    root.minsize(450, 500)
    root.maxsize(450, 500)
    init_frame()
    canvas.bind('<Button-1>', click_event_handler)
    canvas.bind("<Motion>", move_gun)
    init_menu()

if __name__ == "__main__":
    init_main_window()
    init_game()
    timer_event()
    root.mainloop()