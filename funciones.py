import pygame

import math
import heapq

# Controlador PID
class PID:
    def __init__(self, kp, ki, kd):
        """
        Argumentos:
        kp -- Constante proporcional
        ki -- Constante integrall
        kd -- Constante derivativa

        
        Descripción:
        Inicializa el controladir PID con las constantes dadas
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def calcular(self, error, dt):
        """
        Argumentos:
        error -- Error entre la posición deseada y la actual
        dt -- Tiempo entre actualizaciones
        
        Descripción:
        Calcula la salidq del controlador PID basada en el error actual
        """
        self.integral += error * dt
        derivada = (error - self.prev_error) / dt

        salida = self.kp * error + self.ki * self.integral + self.kd * derivada
        self.prev_error = error
        return salida

# Clase Robot
class Robot:
    def __init__(self, x, y, theta, radio, largo):
        """
        Argumentos:
        x -- Posición inicial en el eje x
        y -- Posición inicial en el eje y
        theta -- Ángulo inicial de orientación del robot
        radio -- Radio del robot
        largo -- Distancia entre las ruedas
        
        Descripción:
        Inicializa el robot con su posición, orientación y tamaños dados
        """
        self.x = x
        self.y = y
        self.theta = theta
        self.radio = radio
        self.largo = largo
        self.v_r = 0
        self.v_l = 0
        self.objetivo = None

    def mover(self, dt, ancho_pantalla, alto_pantalla):
        """
        Argumentos:
        dt -- Tiempo entre actualizaciones (segundos)
        ancho_pantalla -- Ancho de la pantalla de simulación

        alto_pantalla -- Alto de la pantalla de simulación
        
        Descripción:
        Actualiza la posición del robot basándose en el modelo cinemático, ajustando su orientación 
        de manera más suave utilizando un controlador PID y manteniéndolo dentro de los límites 
        de la pantalla
        """
        if self.objetivo:
            # Calcular la distancia y ángulo hacia el objetivo
            dx = self.objetivo[0] - self.x
            dy = self.objetivo[1] - self.y
            distancia = math.sqrt(dx**2 + dy**2)
            angulo_objetivo = math.atan2(dy, dx)

            # Control PID para ajustar el ángulo
            pid_angulo = PID(1.0, 0.0, 0.05)  
            
            # Ajustar el error angular para que esté en el rango [-pi, pi]
            error_angulo = angulo_objetivo - self.theta
            error_angulo = (error_angulo + math.pi) % (2 * math.pi) - math.pi  #entre [-pi, pi]
            
            # Tolerancia para evitar pequeños ajustes constantes
            tolerancia_angular = 0.05  # Valor en radianes (~3 grados)
            
            # Solo se ajusts la orientación si el error es significativo
            if abs(error_angulo) > tolerancia_angular:
                omega = pid_angulo.calcular(error_angulo, dt)
            else:
                omega = 0
            
            # Ajustar velocidades de las ruedas
            self.v_r = 100 + omega * self.largo / 2
            self.v_l = 100 - omega * self.largo / 2

            # Modelo cinemático
            v = (self.v_r + self.v_l) / 2
            omega = (self.v_r - self.v_l) / self.largo

            # Actualizar la orientación
            self.theta += omega * dt

            # Actualizar la posición
            self.x += v * math.cos(self.theta) * dt
            self.y += v * math.sin(self.theta) * dt

            # Mantener el robot dentro de los límites de la pantalla
            # En un primer momento lo tenía sin esta instrucción y el robot se salía de la pantalla 
            self.x = max(self.radio, min(ancho_pantalla - self.radio, self.x))
            self.y = max(self.radio, min(alto_pantalla - self.radio, self.y))



    def dibujar(self, pantalla):
        """
        Argumentos:
        pantalla -- Superficie de Pygame donde se dibuja el robot
        
        Descripción:
        Dibuja el robot en la pantalla y una línea que indica su orientació
        """
        # Dibujar el cuerpo del robot como un círculo
        pygame.draw.circle(pantalla, (255, 0, 0), (int(self.x), int(self.y)), self.radio)
        # Dibujar una línea que indica la orientación
        extremo_x = self.x + self.radio * math.cos(self.theta)
        extremo_y = self.y + self.radio * math.sin(self.theta)
        pygame.draw.line(pantalla, (0, 0, 0), (self.x, self.y), (extremo_x, extremo_y), 3)

    def establecer_objetivo(self, objetivo):
        """
        Argumentos:
        objetivo -- Tupla (x, y) que representa la posición objetivo
        
        Descripción:
        Establece un objetivo al que el robot debe dirigirse
        """
        self.objetivo = objetivo

# Planificación de la ruta usando A*
def planificar_ruta(inicio, objetivo, ancho, alto):
    """
    Argumentos:
    inicio -- Coordenadas iniciales del robot
    objetivo -- Coordenadas objetivo
    ancho -- Ancho de la pantalla
    alto -- Alto de la pantalla
    
    Descripción:
    Planifica una ruta desde el punto de inicio hasta el objetivo utilizando el algoritmo A*
    """
    def heuristica(a, b):
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

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

        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            siguiente = (actual[0] + dx, actual[1] + dy)
            if 0 <= siguiente[0] < ancho and 0 <= siguiente[1] < alto:
                nuevo_costo = cost_so_far[actual] + 1
                if siguiente not in cost_so_far or nuevo_costo < cost_so_far[siguiente]:
                    cost_so_far[siguiente] = nuevo_costo
                    prioridad = nuevo_costo + heuristica(objetivo, siguiente)
                    heapq.heappush(open_list, (prioridad, siguiente))
                    came_from[siguiente] = actual

    ruta = []
    actual = objetivo
    while actual != inicio:
        ruta.append(actual)
        actual = came_from.get(actual, inicio)
    ruta.reverse()
    return ruta

def simplificar_ruta(ruta):
    """
    Argumentos:
    ruta -- Lista de puntos que forman la ruta
    
    Descripción:
    Simplifica la ruta eliminando puntos intermedios que están muy cerca unos de otros
    """
    if len(ruta) <= 2:
        return ruta

    nueva_ruta = [ruta[0]]  # se mantiene el primer punto
    for i in range(1, len(ruta) - 1):
        # Solo mantenemos puntos si están lo suficientemente lejos del anterior
        if abs(ruta[i][0] - nueva_ruta[-1][0]) > 10 or abs(ruta[i][1] - nueva_ruta[-1][1]) > 10:
            nueva_ruta.append(ruta[i])
    
    nueva_ruta.append(ruta[-1])  # Mantenemos el último punt o

    return nueva_ruta
