# ==============================================================================
# Módulo de Auditoría, Validaciones Avanzadas y Simulaciones de Estrés
# Autor: Johan Camilo Guzmán Bareño
# Curso: Programación (213023) - Fase 4 (Software FJ)
# ==============================================================================

import logging
import os

# Aseguramos que exista la carpeta de logs antes de configurar el archivo
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configuración del registro de eventos en archivo y consola
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler("logs/eventos_fj.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# ------------------------------------------------------------------------------
# 1. EXCEPCIONES PERSONALIZADAS DEL SISTEMA
# ------------------------------------------------------------------------------
class ErrorBaseSoftwareFJ(Exception):
    """Excepción padre para todos los errores de negocio de Software FJ."""
    pass

class ErrorValidacionDatos(ErrorBaseSoftwareFJ):
    """Se lanza cuando un cliente o servicio tiene datos vacíos o incoherentes."""
    pass

class ErrorOperacionReserva(ErrorBaseSoftwareFJ):
    """Se lanza al intentar confirmar, cancelar o cobrar una reserva inválida."""
    pass


# ------------------------------------------------------------------------------
# 2. CLASE DE AUDITORÍA Y CONTROL CON MANEJO ROBUSTO DE EXCEPCIONES
# ------------------------------------------------------------------------------
class AuditorReservas:
    """
    Clase encargada de validar operaciones críticas, aplicar sobrecarga
    en el cálculo de penalidades y encadenar excepciones técnicas.
    """
    def __init__(self):
        self.historial_auditoria = []

    def calcular_tarifa_ajustada(self, valor_base, horas, descuento=0.0, recargo_urgencia=False):
        """
        Método con parámetros opcionales (sobrecarga) para calcular costos
        validando que no existan valores negativos o tipos de datos erróneos.
        """
        try:
            # Convertimos a float para atrapar si el usuario envió texto por error
            base = float(valor_base)
            tiempo = int(horas)
            
            if base <= 0 or tiempo <= 0:
                raise ErrorValidacionDatos("El valor base y las horas deben ser mayores a cero.")
                
            subtotal = base * tiempo
            
            if recargo_urgencia:
                subtotal += subtotal * 0.15  # 15% adicional por servicio inmediato
                
            total = subtotal - (subtotal * descuento)
            
        except ValueError as error_nativo:
            # Encadenamiento de excepciones: transformamos el error técnico en uno de negocio
            logging.error(f"Fallo de conversión numérica al calcular tarifa: {error_nativo}")
            raise ErrorOperacionReserva("Los parámetros numéricos ingresados no son válidos.") from error_nativo
            
        except ErrorValidacionDatos as error_negocio:
            logging.warning(f"Regla de negocio incumplida: {error_negocio}")
            raise
            
        else:
            # El bloque 'else' solo corre si todo salió perfecto en el 'try'
            logging.info(f"Cálculo de tarifa exitoso. Total generado: ${total:,.2f}")
            return round(total, 2)
            
        finally:
            # El bloque 'finally' siempre se ejecuta para dejar trazabilidad
            self.historial_auditoria.append("Intento de cálculo procesado.")

    def procesar_cancelacion(self, id_reserva, estado_actual, horas_anticipacion):
        """
        Valida si una reserva puede cancelarse según su estado y tiempo previo.
        """
        try:
            if not id_reserva or not isinstance(id_reserva, str):
                raise ErrorValidacionDatos("El código de reserva es obligatorio.")
                
            if estado_actual == "CANCELADA":
                raise ErrorOperacionReserva(f"La reserva {id_reserva} ya se encuentra cancelada.")
                
            if horas_anticipacion < 2:
                raise ErrorOperacionReserva(
                    f"No se puede cancelar {id_reserva} con menos de 2 horas de anticipación."
                )
                
        except ErrorBaseSoftwareFJ as err:
            logging.error(f"Rechazo en cancelación [{id_reserva}]: {err}")
            return False
        else:
            logging.info(f"Reserva {id_reserva} cancelada correctamente sin penalidad.")
            return True
        finally:
            logging.info(f"Auditoría de estado finalizada para el registro: {id_reserva}")


# ------------------------------------------------------------------------------
# 3. EJECUCIÓN DE SIMULACIONES (CASOS VÁLIDOS E INVÁLIDOS SIN DETENER EL SISTEMA)
# ------------------------------------------------------------------------------
def ejecutar_pruebas_auditoria():
    print("\n--- INICIANDO SIMULACIONES DE AUDITORÍA Y EXCEPCIONES (JOHAN GUZMÁN) ---")
    auditor = AuditorReservas()

    # Simulación 1: Cálculo válido normal
    try:
        auditor.calcular_tarifa_ajustada(50000, 3)
    except ErrorBaseSoftwareFJ:
        pass

    # Simulación 2: Cálculo válido con sobrecarga (descuento y recargo de urgencia)
    try:
        auditor.calcular_tarifa_ajustada(80000, 2, descuento=0.10, recargo_urgencia=True)
    except ErrorBaseSoftwareFJ:
        pass

    # Simulación 3: Error encadenado (enviar texto en lugar de horas)
    try:
        auditor.calcular_tarifa_ajustada(40000, "cuatro_horas")
    except ErrorOperacionReserva as e:
        print(f"Excepción atrapada de forma segura: {e} | Causa original: {e.__cause__}")

    # Simulación 4: Error de validación (tarifa en cero o negativa)
    try:
        auditor.calcular_tarifa_ajustada(-15000, 2)
    except ErrorValidacionDatos as e:
        print(f"Excepción de negocio atrapada: {e}")

    # Simulación 5: Cancelación válida
    auditor.procesar_cancelacion("RES-101", "CONFIRMADA", 5)

    # Simulación 6: Cancelación inválida por falta de tiempo
    auditor.procesar_cancelacion("RES-102", "CONFIRMADA", 1)

    # Simulación 7: Cancelación inválida por estado repetido
    auditor.procesar_cancelacion("RES-103", "CANCELADA", 10)

    print("--- FIN DE SIMULACIONES: EL SISTEMA SIGUE ESTABLE Y ACTIVO ---\n")

if __name__ == "__main__":
    ejecutar_pruebas_auditoria()
