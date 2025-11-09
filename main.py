import pygame
from sys import exit
import os
import math


pygame.init()
screen = pygame.display.set_mode((1200, 900))
pygame.display.set_caption("平抛运动模拟")
clock = pygame.time.Clock()


# ========== 资源 ==========
ball_image = pygame.image.load("ball.png").convert_alpha()
ball_surf = pygame.transform.scale(ball_image, (24, 24))
ball_rect = ball_surf.get_rect()


font_path = "C:/Windows/Fonts/msyh.ttc"
if not os.path.exists(font_path):
    font = pygame.font.SysFont(None, 24)
else:
    font = pygame.font.Font(font_path, 24)


# ========== 物理参数 ==========
SCALE = 100.0        # 1m = 100px
g = 9.8              # m/s^2
v_x = 10.0        # 初始速度
h0_m = 2.0           # 初始高度
v_y = 0              # 垂直速度分量
t_s = 1.0
ground_y_px = 500
start_x_px = 50



# ========== 状态 ==========
running = False
fired = False
show_force = False
show_velocity = False
dragging_angle = False

start_time = 0.0
trail_surface = pygame.Surface((1200, 900), pygame.SRCALPHA)
trail_points = []


# ========== 滑块参数 ==========
slider_w = 500
slider_h = 6
handle_r = 10


# 速度滑块位置与范围
v_slider_x = 350
v_slider_y = 20
min_speed = 0
max_speed = 30


# 高度滑块位置与范围
h_slider_x = 350
h_slider_y = 60
min_height = -2.5
max_height = 4.0

# 时间滑块位置与范围
ts_slider_x = 350
ts_slider_y = 100
min_timeSpeed = 0.1
max_timeSpeed = 2

# 角度滑块位置与范围
angle_slider_x = 350
angle_slider_y = 140
min_angle = 0
max_angle = 90
angle_deg = 45.0  # 初始角度（单位：度）



# 状态
dragging_v = False
dragging_h = False
dragging_ts = False

# ======== CheckBox ========
checkbox_rect = pygame.Rect(1000, 120, 20, 20)
velocity_checkbox = pygame.Rect(1000, 150, 20, 20)


# ========== 工具函数 ==========
def phys_to_pixel(x_m, h_m):
    """物理坐标(米) → 屏幕像素坐标"""
    x_px = start_x_px + x_m * SCALE
    y_px = ground_y_px - h_m * SCALE
    return (int(x_px), int(y_px))



def draw_slider(screen, x, y, value, min_val, max_val, label, color):
    """绘制滑块"""
    pygame.draw.rect(screen, (180, 180, 180), (x, y, slider_w, slider_h))
    handle_x = x + (value - min_val) / (max_val - min_val) * slider_w
    pygame.draw.circle(screen, color, (int(handle_x), y + slider_h // 2), handle_r)
    txt = font.render(f"{label}: {value:.1f}", True, (0, 0, 0))
    screen.blit(txt, (x + slider_w + 20, y - 5))
    return handle_x


def draw_arrow(surface, start, end, color=(255, 0, 0), width=3):
    """绘制从 start 到 end 的箭头"""
    pygame.draw.line(surface, color, start, end, width)
    # 箭头头部
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    arrow_size = 8
    left = (end[0] - arrow_size * math.cos(angle - math.pi / 6),
            end[1] - arrow_size * math.sin(angle - math.pi / 6))
    right = (end[0] - arrow_size * math.cos(angle + math.pi / 6),
             end[1] - arrow_size * math.sin(angle + math.pi / 6))
    pygame.draw.polygon(surface, color, [end, left, right])


# ========== 主循环 ==========
while True:

    dt = clock.tick(60) / 1000.0

    #事件检测
    for event in pygame.event.get():

        # ==== 退出 ====
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()


        # ==== 空格运行 ====
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not running:
                running = True
                fired = True
                start_time = pygame.time.get_ticks() / 1000.0
                trail_points.clear()
                angle_rad = math.radians(angle_deg) if 'angle_deg' in globals() else math.radians(
                    45.0)  # 如果你用了角度滑块则用 angle_deg
                v0 = v_x  # v_x 是滑块上的初速度大小（m/s）
                v_x_comp = v0 * math.cos(angle_rad)  # 水平分量（向右为正）
                v_y_comp = v0 * math.sin(angle_rad)  # 竖直初速度（向上为正）





        # ==== 按R重置 ====
            elif event.key == pygame.K_r:
                running = False
                fired = False
                trail_surface.fill((0, 0, 0, 0))
                trail_points.clear()


        # ==== 滑块功能 ====
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mx, my = event.pos
                # 判断哪个滑块被拖动
                v_handle_x = v_slider_x + (v_x - min_speed) / (max_speed - min_speed) * slider_w
                h_handle_x = h_slider_x + (h0_m - min_height) / (max_height - min_height) * slider_w
                ts_handle_x = ts_slider_x + (t_s - min_timeSpeed) / (max_timeSpeed - min_timeSpeed) * slider_w
                angle_handle_x = angle_slider_x + (angle_deg - min_angle) / (max_angle - min_angle) * slider_w
                if abs(mx - v_handle_x) < 15 and abs(my - (v_slider_y + slider_h // 2)) < 15:
                    dragging_v = True
                elif abs(mx - h_handle_x) < 15 and abs(my - (h_slider_y + slider_h // 2)) < 15:
                    dragging_h = True
                elif abs(mx - ts_handle_x) < 15 and abs(my - (ts_slider_y + slider_h // 2)) < 15:
                    dragging_ts = True
                elif abs(mx - angle_handle_x) < 15 and abs(my - (angle_slider_y + slider_h // 2)) < 15:
                    dragging_angle = True


        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging_v = False
                dragging_h = False
                dragging_ts = False
                dragging_angle = False


        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            if dragging_v and not running:
                mx = max(v_slider_x, min(v_slider_x + slider_w, mx))
                ratio = (mx - v_slider_x) / slider_w
                v_x = min_speed + ratio * (max_speed - min_speed)
            elif dragging_h and not running:
                mx = max(h_slider_x, min(h_slider_x + slider_w, mx))
                ratio = (mx - h_slider_x) / slider_w
                h0_m = min_height + ratio * (max_height - min_height)
            elif dragging_ts and not running:
                mx = max(ts_slider_x, min(ts_slider_x + slider_w, mx))
                ratio = (mx - ts_slider_x) / slider_w
                t_s = min_timeSpeed + ratio * (max_timeSpeed - min_timeSpeed)
            elif dragging_angle and not running:
                mx = max(angle_slider_x, min(angle_slider_x + slider_w, mx))
                ratio = (mx - angle_slider_x) / slider_w
                angle_deg = min_angle + ratio * (max_angle - min_angle)



        # ==== checkbox ====
        if event.type == pygame.MOUSEBUTTONDOWN:
            if checkbox_rect.collidepoint(event.pos):
                show_force = not show_force

        if event.type == pygame.MOUSEBUTTONDOWN:
            if velocity_checkbox.collidepoint(event.pos):
                show_velocity = not show_velocity


    # ========== 绘制 ==========
    screen.fill((255, 255, 255))
    screen.blit(trail_surface, (0, 0)) #轨迹



    if running:

        #更新小球状态
        now = pygame.time.get_ticks() / 1000.0
        t = (now - start_time) * t_s
        if t < 0:
            t = 0.0

        # 瞬时速度
        vx_inst = v_x_comp  # 水平恒定（向右为正）
        vy_inst = v_y_comp - g * t  # 竖直瞬时速度（向上为正）

        # 位置
        x_m = v_x_comp * t
        h_m = h0_m + v_y_comp * t - 0.5 * g * t * t

        # 到底部检测
        if h_m <= -4:
            h_m = -4
            running = False

        px, py = phys_to_pixel(x_m, h_m)
        ball_rect.center = (px, py)

        # 计算合速度
        v_total = (v_x ** 2 + v_y ** 2) ** 0.5
        angle_v_total = math.atan2(v_y, v_x)


        #轨迹
        trail_points.append((px, py))
        if len(trail_points) > 1:
            pygame.draw.line(trail_surface, (0, 0, 255), trail_points[-2], trail_points[-1], 2)

    else:
        px, py = phys_to_pixel(0.0, h0_m)
        ball_rect.center = (px, py)
        v_y = 0



    screen.blit(ball_surf, ball_rect)


    # 绘制重力矢量
    if show_force and (running or fired):
        px, py = ball_rect.center
        g_arrow_len = 60
        end = (px, py + g_arrow_len)
        draw_arrow(screen, (px, py), end, color=(255, 0, 0), width=3)
        label = font.render("mg", True, (255, 0, 0))
        screen.blit(label, (px + 10, py + g_arrow_len / 2))


    #绘制速度矢量
    if show_velocity and (running or fired):
        start = ball_rect.center

        vx_px = vx_inst * SCALE
        vy_px = -vy_inst * SCALE

        arrow_scale = 0.06  # 调节视觉长度

        # 合速度（红）
        end_total = (start[0] + vx_px * arrow_scale, start[1] + vy_px * arrow_scale)
        draw_arrow(screen, start, end_total, color=(255, 0, 0), width=3)
        screen.blit(font.render("v", True, (255, 0, 0)), (end_total[0] + 5, end_total[1] - 10))

        # 水平分速度 vx（绿）
        end_vx = (start[0] + vx_px * arrow_scale, start[1])
        draw_arrow(screen, start, end_vx, color=(0, 150, 0), width=2)
        screen.blit(font.render("vx", True, (0, 150, 0)), (end_vx[0] + 5, end_vx[1] - 10))

        # 竖直分速度 vy（蓝）
        end_vy = (start[0], start[1] + vy_px * arrow_scale)
        draw_arrow(screen, start, end_vy, color=(0, 0, 255), width=2)
        screen.blit(font.render("vy", True, (0, 0, 255)), (end_vy[0] + 5, end_vy[1] + 5))

        # 辅助线
        pygame.draw.line(screen, (180, 180, 180), end_vx, end_total, 1)
        pygame.draw.line(screen, (180, 180, 180), end_vy, end_total, 1)


    # 绘制UI
    screen.blit(font.render("按 [空格] 运行 | 按 [R] 重置", True, (0, 0, 0)), (10, 10))

    #绘制复选框
    pygame.draw.rect(screen, (0, 0, 0), checkbox_rect, 2)  # 边框


    if show_force:
        pygame.draw.rect(screen, (0, 255, 0), checkbox_rect.inflate(-4, -4))  # 填充选中状态


    label = font.render("显示受力矢量", True, (0, 0, 0))
    screen.blit(label, (checkbox_rect.x + 20, checkbox_rect.y - 10))
    pygame.draw.rect(screen, (0, 0, 0), velocity_checkbox, 2)


    if show_velocity:
        pygame.draw.rect(screen, (0, 255, 0), velocity_checkbox.inflate(-4, -4))


    velocity_label = font.render("显示速度矢量", True, (0, 0, 0))
    screen.blit(velocity_label, (velocity_checkbox.x + 30, velocity_checkbox.y - 10))




    # ==== 绘制滑块 ====
    draw_slider(screen, v_slider_x, v_slider_y, v_x, min_speed, max_speed, "速度(m/s)", (255, 100, 100))
    draw_slider(screen, h_slider_x, h_slider_y, h0_m, min_height, max_height, "高度(m)", (100, 150, 255))
    draw_slider(screen,ts_slider_x,ts_slider_y,t_s,min_timeSpeed,max_timeSpeed,"时间流速",(100,255,100))
    draw_slider(screen, angle_slider_x, angle_slider_y, angle_deg, min_angle, max_angle, "角度(°)", (255, 200, 0))

    pygame.display.flip()
