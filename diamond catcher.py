from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
import os

score = 0
game_state = 'active'
cheat_mode = False

d_size = 15
d_x = random.randint(50, 550)
d_y = 800
d_speed = 100.0
d_color = [random.uniform(0.6, 1.0), random.uniform(0.6, 1.0), random.uniform(0.6, 1.0)]

c_x = 300
c_y = 25
c_w = 100
c_h = 15
c_speed = 20
c_color = [1.0, 1.0, 1.0]

cross_x = 550
cross_y = 550
cross_size = 15

arrow_x = 50
arrow_y = 550
arrow_size = 15

pause_btn_x = 300
pause_btn_y = 550
pause_btn_size = 15

last_time = None

def Find_Zone(x, y, x1, y1):
    dx = x1 - x
    dy = y1 - y
    if abs(dx) >= abs(dy):
        if dx >= 0 and dy >= 0: return 0
        elif dx < 0 and dy >= 0: return 3
        elif dx < 0 and dy < 0: return 4
        elif dx >= 0 and dy < 0: return 7
    else:
        if dx >= 0 and dy >= 0: return 1
        elif dx < 0 and dy >= 0: return 2
        elif dx < 0 and dy < 0: return 5
        elif dx >= 0 and dy < 0: return 6

def conv_To_Zone0(x, y, zone):
    if zone == 0: return x, y
    elif zone == 1: return y, x
    elif zone == 2: return y, -x
    elif zone == 3: return -x, y
    elif zone == 4: return -x, -y
    elif zone == 5: return -y, -x
    elif zone == 6: return -y, x
    elif zone == 7: return x, -y

def conv_From_Zone0(x, y, zone):
    if zone == 0: return x, y
    elif zone == 1: return y, x
    elif zone == 2: return -y, x
    elif zone == 3: return -x, y
    elif zone == 4: return -x, -y
    elif zone == 5: return -y, -x
    elif zone == 6: return y, -x
    elif zone == 7: return x, -y

def draw_pixel(x, y):
    glBegin(GL_POINTS)
    glVertex2f(int(x), int(y))
    glEnd()

def draw_line(x, y, x1, y1):
    zone = Find_Zone(x, y, x1, y1)
    x_conv, y_conv = conv_To_Zone0(x, y, zone)
    x1_conv, y1_conv = conv_To_Zone0(x1, y1, zone)
    if x_conv > x1_conv:
        x_conv, y_conv, x1_conv, y1_conv = x1_conv, y1_conv, x_conv, y_conv
    dx = x1_conv - x_conv
    dy = y1_conv - y_conv
    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)
    x_cur, y_cur = x_conv, y_conv
    while x_cur <= x1_conv:
        rx, ry = conv_From_Zone0(x_cur, y_cur, zone)
        draw_pixel(rx, ry)
        if d > 0:
            d = d + incNE
            y_cur += 1
        else:
            d = d + incE
        x_cur += 1

def draw_diamond(x, y, size):
    glColor3f(d_color[0], d_color[1], d_color[2])
    top_x, top_y = x, y + size
    right_x, right_y = x + int(size * 0.6), y
    bottom_x, bottom_y = x, y - size
    left_x, left_y = x - int(size * 0.6), y
    draw_line(top_x, top_y, right_x, right_y)
    draw_line(right_x, right_y, bottom_x, bottom_y)
    draw_line(bottom_x, bottom_y, left_x, left_y)
    draw_line(left_x, left_y, top_x, top_y)

def draw_catcher(c_x, c_y, width):
    glColor3f(c_color[0], c_color[1], c_color[2])
    draw_line(c_x - width // 2, c_y, c_x + width // 2, c_y)
    draw_line(c_x - width // 2, c_y, c_x - width // 3, c_y - 15)
    draw_line(c_x + width // 2, c_y, c_x + width // 3, c_y - 15)
    draw_line(c_x - width // 3, c_y - 15, c_x + width // 3, c_y - 15)

def draw_cross(x, y):
    glColor3f(1.0, 0.0, 0.0)
    draw_line(x - 10, y - 10, x + 10, y + 10)
    draw_line(x - 10, y + 10, x + 10, y - 10)

def draw_arrow(x, y):
    glColor3f(0.0, 1.0, 1.0)
    draw_line(x - 15, y, x + 5, y)
    draw_line(x - 15, y, x - 8, y + 8)
    draw_line(x - 15, y, x - 8, y - 8)

def draw_pause(x, y):
    glColor3f(1.0, 1.0, 0.0)
    draw_line(x - 5, y - 10, x - 5, y + 10)
    draw_line(x + 5, y - 10, x + 5, y + 10)

def draw_play(x, y):
    glColor3f(1.0, 1.0, 0.0)
    draw_line(x - 8, y + 10, x + 8, y)
    draw_line(x + 8, y, x - 8, y - 10)
    draw_line(x - 8, y - 10, x - 8, y + 10)

def aabb_collision(box1, box2):
    left1, right1, top1, bottom1 = box1
    left2, right2, top2, bottom2 = box2
    return not (right1 < left2 or right2 < left1 or bottom1 > top2 or bottom2 > top1)

def get_diamond_bbox(x, y, size):
    half_w = int(size * 0.6)
    return (x - half_w, x + half_w, y + size, y - size)

def get_catcher_bbox(cx, cy, width):
    half_w = width // 2
    return (cx - half_w, cx + half_w, cy, cy - c_h)

def has_collided():
    return aabb_collision(get_diamond_bbox(d_x, d_y, d_size),
                          get_catcher_bbox(c_x, c_y, c_w))

def reset_diamond():
    global d_x, d_y, d_speed, d_color
    d_x = random.randint(50, 550)
    d_y = 800
    d_speed += 30
    d_color = [random.uniform(0.6, 1.0), random.uniform(0.6, 1.0), random.uniform(0.6, 1.0)]

def reset_game():
    global score, game_state, c_color, c_x, d_speed, d_y, d_x, d_color, cheat_mode
    score = 0
    game_state = 'active'
    c_x = 300
    c_color = [1.0, 1.0, 1.0]
    d_speed = 100
    d_x = random.randint(50, 550)
    d_y = 800
    d_color = [random.uniform(0.6, 1.0), random.uniform(0.6, 1.0), random.uniform(0.6, 1.0)]
    cheat_mode = False

def mouse_click(button, state, x, y):
    global game_state
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        y = 600 - y
        if (arrow_x - 20 <= x <= arrow_x + 20) and (arrow_y - 20 <= y <= arrow_y + 20):
            reset_game()
            return
        if (cross_x - 20 <= x <= cross_x + 20) and (cross_y - 20 <= y <= cross_y + 20):
            print("Final Score:", score)
            os._exit(0)
        if (pause_btn_x - 20 <= x <= pause_btn_x + 20) and (pause_btn_y - 20 <= y <= pause_btn_y + 20):
            toggle_pause()

def keyboard_handler(key, x, y):
    global cheat_mode
    if key == b'c' or key == b'C':
        if game_state != 'over':
            cheat_mode = not cheat_mode

def toggle_pause():
    global game_state
    if game_state == 'active':
        game_state = 'paused'
    elif game_state == 'paused':
        game_state = 'active'

def animate():
    global game_state, score, d_y, d_x, c_x, c_color, last_time
    current = time.time()
    if last_time is None:
        last_time = current
    dt = current - last_time
    last_time = current

    if game_state == 'active':
        d_y -= d_speed * dt
        
        if cheat_mode:
            if c_x < d_x - 2: 
                c_x += 1
                if c_x > d_x: c_x = d_x
            elif c_x > d_x + 2:
                c_x -= 1
                if c_x < d_x: c_x = d_x

        half_w = c_w // 2
        c_x = max(half_w, min(600 - half_w, c_x))
        
        d_half_w = int(d_size * 0.6)
        if d_x < d_half_w: d_x = d_half_w
        elif d_x > 600 - d_half_w: d_x = 600 - d_half_w

        if has_collided():
            score += 1
            print("Score:", score)
            reset_diamond()
        elif d_y < -50:
            game_state = 'over'
            c_color = [1.0, 0.0, 0.0]
            print("Game Over! Final Score:", score)
            
    glutPostRedisplay()

def display():
    glClear(GL_COLOR_BUFFER_BIT)

    draw_catcher(c_x, c_y, c_w)
    draw_cross(cross_x, cross_y)
    draw_arrow(arrow_x, arrow_y)

    if game_state != 'over':
        draw_diamond(d_x, int(d_y), d_size)

    if game_state == 'active':
        draw_pause(pause_btn_x, pause_btn_y)
    else:
        draw_play(pause_btn_x, pause_btn_y)

    glutSwapBuffers()
    animate()

def special_input(key, x, y):
    global c_x
    if not cheat_mode and game_state == 'active':
        if key == GLUT_KEY_LEFT:
            c_x -= c_speed
        elif key == GLUT_KEY_RIGHT:
            c_x += c_speed

def main():
    global last_time
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(600, 600)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Catch the Diamonds")
    
    glViewport(0, 0, 600, 600)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 600.0, 0.0, 600.0, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    
    glutKeyboardFunc(keyboard_handler)
    glutDisplayFunc(display)
    glutSpecialFunc(special_input)
    glutMouseFunc(mouse_click)
    last_time = time.time()
    glutMainLoop()

if __name__ == "__main__":
    main()