from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import math
import time
import random

CAMERA_POS = [0, 820, 1185]
Y_FOV = 50
FIRST_PERSON = False

W, H = 1200, 800
BOARD_LENGTH = 600
SCORE = 0
LIVES = 5
BULLET_MISSED = 0

BOARD_GREEN = (125 / 255, 148 / 255, 92 / 255)
BOARD_WHITE = (239 / 255, 239 / 255, 213 / 255)

BOARD_WALL_1 = (255 / 255, 223 / 255, 100 / 255)
BOARD_WALL_2 = (200 / 255, 180 / 255, 255 / 255)
BOARD_WALL_3 = (100 / 255, 200 / 255, 255 / 255)
BOARD_WALL_4 = (200 / 255, 90 / 255, 90 / 255)

PLAYER = [0, 0, 0, 0]
P_SPEED = 8
P_BULLETS = []
FALLINGDOWN = 0
ENEMY = []

CHEAT = False
GUN_VISION = False

LOSE = False
GOD_BULLET = False

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()

    gluOrtho2D(0, W, 0, H)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def keyboardListener(key, x, y):
    global SCORE, LIVES, BULLET_MISSED, PLAYER, P_BULLETS, ENEMY, LOSE, FALLINGDOWN, CHEAT, Y_FOV, GUN_VISION

    min_x = -BOARD_LENGTH
    max_x = BOARD_LENGTH
    min_y = -BOARD_LENGTH
    max_y = BOARD_LENGTH

    if key.lower() == b"w" and not (LOSE):
        if CHEAT:
            new_x = PLAYER[0]
            new_y = PLAYER[1] - P_SPEED
        else:
            new_x = PLAYER[0] + P_SPEED * math.cos(math.radians(PLAYER[3]))
            new_y = PLAYER[1] + P_SPEED * math.sin(math.radians(PLAYER[3]))

        if min_x <= new_x <= max_x and min_y <= new_y <= max_y:
            PLAYER[0] = new_x
            PLAYER[1] = new_y

    if key.lower() == b"s" and not (LOSE):
        if CHEAT:
            new_x = PLAYER[0]
            new_y = PLAYER[1] + P_SPEED
        else:
            new_x = PLAYER[0] - P_SPEED * math.cos(math.radians(PLAYER[3]))
            new_y = PLAYER[1] - P_SPEED * math.sin(math.radians(PLAYER[3]))

        if min_x <= new_x <= max_x and min_y <= new_y <= max_y:
            PLAYER[0] = new_x
            PLAYER[1] = new_y

    if key.lower() == b"a" and not (LOSE):
        if CHEAT:
            new_x = PLAYER[0] + P_SPEED
            new_y = PLAYER[1]
        else:
            new_x = PLAYER[0]
            new_y = PLAYER[1]
            PLAYER[-1] += 5

        if min_x <= new_x <= max_x and min_y <= new_y <= max_y:
            PLAYER[0] = new_x
            PLAYER[1] = new_y

    if key.lower() == b"d" and not (LOSE):
        if CHEAT:
            new_x = PLAYER[0] - P_SPEED
            new_y = PLAYER[1]
        else:
            new_x = PLAYER[0]
            new_y = PLAYER[1]
            PLAYER[-1] -= 5

        if min_x <= new_x <= max_x and min_y <= new_y <= max_y:
            PLAYER[0] = new_x
            PLAYER[1] = new_y

    if key == b"c" and not (LOSE):
        CHEAT = not (CHEAT)
        print("-" * 30)
        print(f"Cheat Mode: {CHEAT}")
        print("-" * 30)

    if key == b"v" and not (LOSE):
        GUN_VISION = not (GUN_VISION)
        print("-" * 30)
        print(f"Cheat Vision: {CHEAT}")
        print("-" * 30)

    if key.lower() == b"r":
        print("-" * 30)
        print(f"Restarting The Game")
        print("-" * 30)
        SCORE = 0
        LIVES = 5
        BULLET_MISSED = 0
        PLAYER = [0, 0, 0, 0]
        P_BULLETS.clear()
        ENEMY.clear()
        LOSE = False
        FALLINGDOWN = 0

def specialKeyListener(key, x, y):
    global CAMERA_POS
    rateOfChange = 5

    if key == GLUT_KEY_UP and not FIRST_PERSON:
        CAMERA_POS[-1] += rateOfChange

    if key == GLUT_KEY_DOWN and not FIRST_PERSON:
        CAMERA_POS[-1] -= rateOfChange

    if key == GLUT_KEY_LEFT and not FIRST_PERSON:
        angle = math.radians(rateOfChange // 2)
        x_new = CAMERA_POS[0] * math.cos(angle) - CAMERA_POS[1] * math.sin(angle)
        y_new = CAMERA_POS[0] * math.sin(angle) + CAMERA_POS[1] * math.cos(angle)
        CAMERA_POS[0] = x_new
        CAMERA_POS[1] = y_new

    if key == GLUT_KEY_RIGHT and not FIRST_PERSON:
        angle = math.radians(-rateOfChange // 2)
        x_new = CAMERA_POS[0] * math.cos(angle) - CAMERA_POS[1] * math.sin(angle)
        y_new = CAMERA_POS[0] * math.sin(angle) + CAMERA_POS[1] * math.cos(angle)
        CAMERA_POS[0] = x_new
        CAMERA_POS[1] = y_new

def mouseListener(button, state, x, y):
    global P_BULLETS, FIRST_PERSON, Y_FOV

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not (LOSE):
        print("Bullet Fired! [LMB]")
        fire_bullet()

    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN and not (LOSE):
        if FIRST_PERSON:
            print("Enabling First Person View")
            FIRST_PERSON = not (FIRST_PERSON)
            Y_FOV = 50
        else:
            print("Enabling Third Person View")
            FIRST_PERSON = not (FIRST_PERSON)
            Y_FOV = 80

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(Y_FOV, W / H, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    x, y, z = CAMERA_POS
    if not (FIRST_PERSON):
        gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)
    else:
        if CHEAT:
            x, y, z, r = PLAYER
            eye_x = x + 25 * math.cos(math.radians(r))
            eye_y = y + 25 * math.sin(math.radians(r))
            eye_z = z + 90

            center_x = x + 100 * math.cos(math.radians(r))
            center_y = y + 100 * math.sin(math.radians(r))
            center_z = z + 60

            if GUN_VISION:
                gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, 0, 0, 1)
            else:
                gluLookAt(x + 100, y + 100, z + 100, x, y, z, 0, 0, 1)

        else:
            x, y, z, r = PLAYER
            eye_x = x + 25 * math.cos(math.radians(r))
            eye_y = y + 25 * math.sin(math.radians(r))
            eye_z = z + 90

            center_x = x + 100 * math.cos(math.radians(r))
            center_y = y + 100 * math.sin(math.radians(r))
            center_z = z + 60

            gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, 0, 0, 1)

def fire_bullet():
    x, y, z, r = PLAYER

    gun_length = 45
    bullet_x = x + gun_length * math.cos(math.radians(r))
    bullet_y = y + gun_length * math.sin(math.radians(r))

    P_BULLETS.append([bullet_x, bullet_y, z + 73, r])

def bulletLogic():
    global BULLET_MISSED, GOD_BULLET

    bullet_speed = 20
    min_x = -BOARD_LENGTH
    max_x = BOARD_LENGTH
    min_y = -BOARD_LENGTH
    max_y = BOARD_LENGTH

    new_bullets = []
    for bullet in P_BULLETS:
        x, y, z, r = bullet

        x += bullet_speed * math.cos(math.radians(r))
        y += bullet_speed * math.sin(math.radians(r))

        if min_x <= x <= max_x and min_y <= y <= max_y:
            hit = False

            for enemy in ENEMY:
                ex, ey, ez = enemy
                if math.hypot(x - ex, y - ey) < 30:
                    ENEMY.remove(enemy)
                    global SCORE
                    SCORE += 1
                    hit = True
                    print("Enemy Shot!")
                    break
            if hit:
                GOD_BULLET = False
                continue

            new_bullets.append([x, y, z, r])
            glPushMatrix()
            glTranslatef(x, y, z)
            glRotatef(r, 0, 0, 1)
            glColor3f(1, 0, 0)
            glutSolidCube(10)
            glPopMatrix()
        else:
            GOD_BULLET = False
            BULLET_MISSED += len(P_BULLETS) - len(new_bullets)

    P_BULLETS[::] = new_bullets

def drawBoard():
    cell_size = BOARD_LENGTH // 6
    start_x = -BOARD_LENGTH
    start_y = -BOARD_LENGTH

    for row in range(12):
        for col in range(12):
            if (row + col) % 2 == 0:
                glColor3f(*BOARD_GREEN)
            else:
                glColor3f(*BOARD_WHITE)

            x = start_x + col * cell_size
            y = start_y + row * cell_size

            glBegin(GL_QUADS)
            glVertex3f(x, y, 0)
            glVertex3f(x + cell_size, y, 0)
            glVertex3f(x + cell_size, y + cell_size, 0)
            glVertex3f(x, y + cell_size, 0)
            glEnd()

    wall_height = 100

    glColor3f(*BOARD_WALL_1)
    glBegin(GL_QUADS)
    glVertex3f(start_x, start_y, 0)
    glVertex3f(start_x + BOARD_LENGTH * 2, start_y, 0)
    glVertex3f(start_x + BOARD_LENGTH * 2, start_y, wall_height)
    glVertex3f(start_x, start_y, wall_height)
    glEnd()

    glColor3f(*BOARD_WALL_2)
    glBegin(GL_QUADS)
    glVertex3f(start_x, start_y + BOARD_LENGTH * 2, 0)
    glVertex3f(start_x + BOARD_LENGTH * 2, start_y + BOARD_LENGTH * 2, 0)
    glVertex3f(start_x + BOARD_LENGTH * 2, start_y + BOARD_LENGTH * 2, wall_height)
    glVertex3f(start_x, start_y + BOARD_LENGTH * 2, wall_height)
    glEnd()

    glColor3f(*BOARD_WALL_3)
    glBegin(GL_QUADS)
    glVertex3f(start_x, start_y, 0)
    glVertex3f(start_x, start_y + BOARD_LENGTH * 2, 0)
    glVertex3f(start_x, start_y + BOARD_LENGTH * 2, wall_height)
    glVertex3f(start_x, start_y, wall_height)
    glEnd()

    glColor3f(*BOARD_WALL_4)
    glBegin(GL_QUADS)
    glVertex3f(start_x + BOARD_LENGTH * 2, start_y, 0)
    glVertex3f(start_x + BOARD_LENGTH * 2, start_y + BOARD_LENGTH * 2, 0)
    glVertex3f(start_x + BOARD_LENGTH * 2, start_y + BOARD_LENGTH * 2, wall_height)
    glVertex3f(start_x + BOARD_LENGTH * 2, start_y, wall_height)
    glEnd()

def drawPlayer():
    x, y, z, r = PLAYER

    glPushMatrix()

    glTranslatef(x, y, z)
    glRotatef(r, 0, 0, 1)
    if LOSE:
        global FALLINGDOWN
        if FALLINGDOWN < 90:
            FALLINGDOWN += 1
        glRotatef(FALLINGDOWN, 1, 0, 0)

    glColor3f(0.1, 0.3, 0.7)
    glTranslatef(0, -10, 0)
    gluCylinder(gluNewQuadric(), 2, 5, 30, 30, 30)

    glTranslatef(0, 20, 0)
    gluCylinder(gluNewQuadric(), 2, 5, 30, 30, 30)

    glColor3f(1.0, 0.6, 0.8)
    glTranslatef(0, -10, 55)
    glScalef(1, 1.5, 2.5)
    glutSolidCube(20)

    glColor3f(0.1, 0.1, 0.1)
    glScalef(1, 1 / 1.5, 1 / 2.5)
    glTranslatef(0, 0, 35)
    gluSphere(gluNewQuadric(), 11, 50, 50)

    glColor3f(0.96, 0.80, 0.69)
    glTranslatef(0, -10, -20)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 5, 2, 60, 30, 30)
    glTranslatef(0, 20, 0)
    gluCylinder(gluNewQuadric(), 5, 2, 60, 30, 30)

    glColor3f(0.75, 0.75, 0.75)
    glTranslatef(0, -10, 3)
    gluCylinder(gluNewQuadric(), 7, 3, 65, 30, 30)

    glPopMatrix()

def drawEnemy():
    global ENEMY, LIVES

    if LOSE:
        return

    if len(ENEMY) < 5:
        ENEMY.append(
            [
                random.uniform(-BOARD_LENGTH, BOARD_LENGTH),
                random.uniform(-BOARD_LENGTH, BOARD_LENGTH),
                40,
            ]
        )

    for enemy in ENEMY:
        x, y, z = enemy

        player_x, player_y, player_z, _ = PLAYER
        dx = player_x - x
        dy = player_y - y
        distance = math.hypot(dx, dy)
        if distance > 50:
            speed = 0.2
            x += speed * dx / distance
            y += speed * dy / distance
            enemy[0], enemy[1] = x, y
        else:
            ENEMY.remove(enemy)
            LIVES -= 1
            print("Damage Taken!", "Lives Left:", LIVES)

        t = time.time()
        period = 2.0
        scale = 2.5 + 0.3 * (1 + math.sin(2 * math.pi * (t % period) / period))

        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(scale, scale, scale)
        glColor3f(1, 0.4, 0.4)
        gluSphere(gluNewQuadric(), 15, 30, 30)
        glTranslatef(0, 0, 22)
        glColor3f(0.4, 0.1, 0.1)
        gluSphere(gluNewQuadric(), 10, 30, 30)
        glPopMatrix()

def cheatMode():
    global PLAYER
    x, y, z, r = PLAYER
    r = math.radians(r)

    if CHEAT and not (LOSE):
        PLAYER[-1] += 1

        gun_length = 45
        bullet_x = x + gun_length * math.cos(r)
        bullet_y = y + gun_length * math.sin(r)

        for enemy in ENEMY:
            ex, ey, ez = enemy

            dx = ex - bullet_x
            dy = ey - bullet_y

            distance = (dx**2 + dy**2) ** 0.5

            error_margin = 10
            if abs((bullet_x + distance * math.cos(r)) - ex) <= error_margin:
                if abs((bullet_y + distance * math.sin(r)) - ey) <= error_margin:
                    global GOD_BULLET
                    if not (GOD_BULLET):
                        print("Shots Fired [Cheat]:")
                        fire_bullet()
                        GOD_BULLET = True
                        break

def showScreen():
    global LIVES, BULLET_MISSED, SCORE, LOSE, FIRST_PERSON, Y_FOV
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, W, H)

    setupCamera()

    drawBoard()
    drawPlayer()
    drawEnemy()
    bulletLogic()
    cheatMode()

    if (LIVES <= 0 or BULLET_MISSED >= 10) and not (LOSE):
        LOSE = True
        FIRST_PERSON = False
        Y_FOV = 50
        print("-" * 30)
        print(f"Game Over! Your Score is {SCORE}")
        print(f'Press "R" to RESTART the Game!')
        print("-" * 30)

    if not (LOSE):
        draw_text(10, 770, f"Player Life Remaining: {LIVES}")
        draw_text(10, 740, f"Game Score: {SCORE}")
        draw_text(10, 710, f"Player Bullet Missed: {BULLET_MISSED}")
    else:
        draw_text(10, 770, f"Game Over! Your Score is {SCORE}")
        draw_text(10, 740, f'Press "R" to RESTART the Game!')

    glutSwapBuffers()

def idle():
    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(W, H)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Sifats Bullet Frenzy")

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()

main()