import pygame
from funciones import Robot, planificar_ruta, simplificar_ruta
import matplotlib.pyplot as plt
import numpy as np

ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
BLANCO = (255, 255, 255)
VERDE = (0, 255, 0)
NEGRO = (0, 0, 0)
AZUL = (0, 0, 255)
ROJO = (255, 0, 0)

pygame.init()
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Simulación Robot")

robot = Robot(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2, 0, 20, 60)

# Variables de simulación
ruta = []
objetivo = None
obstaculos = [
    pygame.Rect(200, 150, 100, 300),
    pygame.Rect(500, 100, 50, 200),
    pygame.Rect(600, 400, 150, 50)
]

dibujando_obstaculo = False
obstaculo_actual = None

# Inicialización del gráfico de matplotlib para mostrar el error de posición
plt.ion()  # Activar modo interactivo
fig, ax = plt.subplots()
errores = []
tiempos = []
linea_error, = ax.plot([], [], label="Error de Posición")
ax.set_xlim(0, 10)  # Mostrar los últimos 10 segundos
ax.set_ylim(0, 300)  # Rango inicial del error de posición (en píxeles)
ax.set_xlabel("Tiempo (s)")
ax.set_ylabel("Error de Posición (píxeles)")
ax.legend()

# Inicializar tiempo
tiempo_inicial = pygame.time.get_ticks() / 1000.0  # Tiempo inicial en segundos

# Loop principal
corriendo = True
while corriendo:
    dt = pygame.time.Clock().tick(60) / 1000.0  # Tiempo entre frames en segundos
    tiempo_actual = pygame.time.get_ticks() / 1000.0 - tiempo_inicial  # Tiempo transcurrido en segundos

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False

        # Detectar clic del ratón para establecer el objetivo
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:  # Clic izquierdo
                if pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]:
                    # Iniciar dibujo de obstáculo
                    dibujando_obstaculo = True
                    obstaculo_inicio = evento.pos
                    obstaculo_actual = pygame.Rect(obstaculo_inicio[0], obstaculo_inicio[1], 0, 0)
                    obstaculos.append(obstaculo_actual)
                else:
                    objetivo = evento.pos
                    robot.establecer_objetivo(objetivo)
                    ruta = planificar_ruta((int(robot.x), int(robot.y)), objetivo, ANCHO_PANTALLA, ALTO_PANTALLA, obstaculos)
                    ruta = simplificar_ruta(ruta)
            elif evento.button == 3:  # Clic derecho
                # Eliminar obstáculo si se hace clic derecho sobre él
                for obstaculo in obstaculos:
                    if obstaculo.collidepoint(evento.pos):
                        obstaculos.remove(obstaculo)
                        break

        elif evento.type == pygame.MOUSEBUTTONUP:
            if evento.button == 1 and dibujando_obstaculo:
                dibujando_obstaculo = False
                obstaculo_actual = None

        elif evento.type == pygame.MOUSEMOTION:
            if dibujando_obstaculo and obstaculo_actual is not None:
                x0, y0 = obstaculo_inicio
                x1, y1 = evento.pos
                obstaculo_actual.width = x1 - x0
                obstaculo_actual.height = y1 - y0

    # Dibujar el entorno
    pantalla.fill(BLANCO)

    # Dibujar los obstáculos
    for obstaculo in obstaculos:
        pygame.draw.rect(pantalla, NEGRO, obstaculo)

    # Dibujar el punto objetivo
    if objetivo:
        pygame.draw.circle(pantalla, VERDE, objetivo, 5)

    # Dibujar la ruta planeada
    if ruta:
        if len(ruta) > 1:
            pygame.draw.lines(pantalla, AZUL, False, ruta, 2)
        else:
            pygame.draw.circle(pantalla, AZUL, ruta[0], 2)

    # Mover el robot
    if ruta:
        siguiente_punto = ruta[0]

        # Establecemos una tolerancia para considerar que llegamos al siguiente punto
        distancia_tolerancia = 15
        robot.establecer_objetivo(siguiente_punto)
        robot.mover(dt, ANCHO_PANTALLA, ALTO_PANTALLA)

        # Calcular el error de posición (distancia entre el robot y el objetivo)
        error_posicion = np.sqrt((robot.x - objetivo[0])**2 + (robot.y - objetivo[1])**2)
        errores.append(error_posicion)
        tiempos.append(tiempo_actual)

        # Actualizar el gráfico de error en tiempo real
        linea_error.set_xdata(tiempos)
        linea_error.set_ydata(errores)

        ax.set_xlim(max(0, tiempo_actual - 10), tiempo_actual + 1)  # Mostrar los últimos 10 segundos
        ax.set_ylim(0, max(errores) + 10)
        plt.draw()
        plt.pause(0.001)  # Breve pausa para permitir la actualización del gráfico

        # Eliminar el punto alcanzado de la ruta si está dentro de la tolerancia
        if abs(robot.x - siguiente_punto[0]) < distancia_tolerancia and abs(robot.y - siguiente_punto[1]) < distancia_tolerancia:
            ruta.pop(0)

    # Dibujar el robot
    robot.dibujar(pantalla)

    # Actualizar pantalla
    pygame.display.flip()

pygame.quit()
plt.ioff()
plt.show()
