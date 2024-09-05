import pygame
from funciones import Robot, planificar_ruta, simplificar_ruta
import matplotlib.pyplot as plt
import numpy as np

ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
BLANCO = (255, 255, 255)
VERDE = (0, 255, 0)

pygame.init()
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Simulación Robot")

robot = Robot(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2, 0, 20, 60)

# Variables de simulaciun
ruta = []
objetivo = None

# Inicialización del gráfico de matplotlib para mostrar el error de posición
plt.ion()  # Activar modo interactivo
fig, ax = plt.subplots()
errores = []
tiempos = []
linea_error, = ax.plot([], [], label="Error de Posición")
ax.set_xlim(0, 10)  # Mostrar los últimos 10 segundos
ax.set_ylim(0, 300)  # Rango inicial del error de posición (en píxeles)(Lo hago así porque resulta mas sencillo y a ciencia cierta en lo mismo)
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
            objetivo = pygame.mouse.get_pos()
            robot.establecer_objetivo(objetivo)
            ruta = planificar_ruta((int(robot.x), int(robot.y)), objetivo, ANCHO_PANTALLA, ALTO_PANTALLA)

            ruta = simplificar_ruta(ruta)  # Simplificamos la ruta antes de seguirla(Esta función es muy importante porque si no el robot cambiaba mucho de orientación, y en ocasiones no lo encontraba)

    # Dibujar el entorno
    pantalla.fill(BLANCO)

    # Dibujar el punto objetivo
    if objetivo:
        pygame.draw.circle(pantalla, VERDE, objetivo, 5)

    # Mover el robot
    if ruta:
        siguiente_punto = ruta[0]
        
        # Establecemos una tolerancia más grande para considerar que llegamos al siguiente punto
        distancia_tolerancia = 15  # Aumentamos el umbral de tolerancia para pasar al siguiente punto
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
