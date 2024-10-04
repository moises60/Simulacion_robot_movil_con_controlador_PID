import pygame
import math
import heapq

GRID_SIZE = 10  # Tamaño de la cuadrícula para A*

# Controlador PID
class PID:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def calcular(self, error, dt):
        self.integral += error * dt
        derivada = (error - self.prev_error) / dt if dt > 0 else 0
        salida = self.kp * error + self.ki * self.integral + self.kd * derivada
        self.prev_error = error
        return salida

# Clase Robot
class Robot:
    def __init__(self, x, y, theta, radio, largo):
        self.x = x
        self.y = y
        self.theta = theta
        self.radio = radio
        self.largo = largo
        self.v_r = 0
        self.v_l = 0
        self.objetivo = None
        self.pid_angulo = PID(2.0, 0.0, 0.1)  # Ajuste de los parámetros PID

    def mover(self, dt, ancho_pantalla, alto_pantalla):
        if self.objetivo:
            # Calcular la distancia y ángulo hacia el objetivo
            dx = self.objetivo[0] - self.x
            dy = self.objetivo[1] - self.y
            distancia = math.sqrt(dx**2 + dy**2)
            angulo_objetivo = math.atan2(dy, dx)

            # Ajustar el error angular para que esté en el rango [-pi, pi]
            error_angulo = angulo_objetivo - self.theta
            error_angulo = (error_angulo + math.pi) % (2 * math.pi) - math.pi

            # Control PID para ajustar el ángulo
            omega = self.pid_angulo.calcular(error_angulo, dt)

            # Velocidad lineal proporcional a la distancia al objetivo
            v = min(200, distancia)

            # Actualizar velocidades de las ruedas
            self.v_r = v + omega * self.largo / 2
            self.v_l = v - omega * self.largo / 2

            # Modelo cinemático
            v = (self.v_r + self.v_l) / 2
            omega = (self.v_r - self.v_l) / self.largo

            # Actualizar la orientación
            self.theta += omega * dt

            # Actualizar la posición
            self.x += v * math.cos(self.theta) * dt
            self.y += v * math.sin(self.theta) * dt

            # Mantener el robot dentro de los límites de la pantalla
            self.x = max(self.radio, min(ancho_pantalla - self.radio, self.x))
            self.y = max(self.radio, min(alto_pantalla - self.radio, self.y))

    def dibujar(self, pantalla):
        # Dibujar el cuerpo del robot como un círculo
        pygame.draw.circle(pantalla, (255, 0, 0), (int(self.x), int(self.y)), self.radio)
        # Dibujar una línea que indica la orientación
        extremo_x = self.x + self.radio * math.cos(self.theta)
        extremo_y = self.y + self.radio * math.sin(self.theta)
        pygame.draw.line(pantalla, (0, 0, 0), (self.x, self.y), (extremo_x, extremo_y), 3)

    def establecer_objetivo(self, objetivo):
        self.objetivo = objetivo

# Planificación de la ruta usando A*
def planificar_ruta(inicio, objetivo, ancho, alto, obstaculos):
    inicio = (inicio[0] // GRID_SIZE, inicio[1] // GRID_SIZE)
    objetivo = (objetivo[0] // GRID_SIZE, objetivo[1] // GRID_SIZE)
    ancho = ancho // GRID_SIZE
    alto = alto // GRID_SIZE

    def heuristica(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def point_in_obstacles(point, obstaculos):
        x, y = point[0] * GRID_SIZE, point[1] * GRID_SIZE
        rect_point = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        for obstaculo in obstaculos:
            if obstaculo.colliderect(rect_point):
                return True
        return False

    open_list = []
    heapq.heappush(open_list, (0, inicio))
    came_from = {}
    cost_so_far = {}
    came_from[inicio] = None
    cost_so_far[inicio] = 0

    while open_list:
        _, actual = heapq.heappop(open_list)

        if actual == objetivo:
            break

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            siguiente = (actual[0] + dx, actual[1] + dy)
            if 0 <= siguiente[0] < ancho and 0 <= siguiente[1] < alto:
                if point_in_obstacles(siguiente, obstaculos):
                    continue
                nuevo_costo = cost_so_far[actual] + 1
                if siguiente not in cost_so_far or nuevo_costo < cost_so_far[siguiente]:
                    cost_so_far[siguiente] = nuevo_costo
                    prioridad = nuevo_costo + heuristica(objetivo, siguiente)
                    heapq.heappush(open_list, (prioridad, siguiente))
                    came_from[siguiente] = actual

    ruta = []
    actual = objetivo
    while actual != inicio:
        ruta.append((actual[0] * GRID_SIZE + GRID_SIZE // 2, actual[1] * GRID_SIZE + GRID_SIZE // 2))
        actual = came_from.get(actual)
        if actual is None:
            break  # No hay ruta posible
    ruta.reverse()
    return ruta

def simplificar_ruta(ruta):
    if len(ruta) <= 2:
        return ruta

    nueva_ruta = [ruta[0]]  # se mantiene el primer punto
    for punto in ruta[1:]:
        if math.hypot(punto[0] - nueva_ruta[-1][0], punto[1] - nueva_ruta[-1][1]) > 15:
            nueva_ruta.append(punto)
    return nueva_ruta
