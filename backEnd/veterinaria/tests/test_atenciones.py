"""
Pruebas de los casos de uso de atenciones con repositorios falsos en memoria.

No usan Django ni Oracle: demuestran que application/ solo depende de los
puertos. Se ejecutan con:  python -m unittest veterinaria.tests.test_atenciones -v
"""
import unittest
from dataclasses import replace
from datetime import datetime, timedelta
from decimal import Decimal

from veterinaria.application.exceptions import (
    AtencionAgendadaMismoDia,
    AtencionNoEliminable,
    AtencionNoEncontrada,
    AtencionSinDetalle,
    DatoAtencionInvalido,
    EstadoAtencionDesconocido,
    MascotaNoEncontrada,
    ServicioInactivo,
    ServicioNoEncontrado,
    ServicioRepetidoEnAtencion,
    TransicionAtencionInvalida,
)
from veterinaria.application.use_cases.atenciones import (
    CambiarEstadoAtencion,
    CrearAtencion,
    EliminarAtencion,
    ListarAtenciones,
    ObtenerAtencion,
)
from veterinaria.domain.entities.atencion import AGENDADA, CANCELADA, PAGADA, REALIZADA
from veterinaria.domain.entities.mascota import Mascota
from veterinaria.domain.entities.servicio import Servicio
from veterinaria.domain.ports.atencion_repository import AtencionRepository
from veterinaria.domain.ports.mascota_repository import MascotaRepository
from veterinaria.domain.ports.servicio_repository import ServicioRepository


class AtencionRepoFalso(AtencionRepository):
    def __init__(self):
        self.datos = {}
        self.sig = 1

    def listar(self, estado=None, mascota_id=None, desde=None, hasta=None, texto=None):
        res = list(self.datos.values())
        if estado:
            res = [a for a in res if a.estado == estado]
        if mascota_id:
            res = [a for a in res if a.mascota_id == mascota_id]
        if texto:
            res = [a for a in res if texto.lower() in a.motivo.lower()]
        return sorted(res, key=lambda a: a.fecha, reverse=True)

    def obtener(self, atencion_id):
        return self.datos.get(atencion_id)

    def crear(self, atencion):
        detalles = [replace(d, atencion_id=self.sig) for d in atencion.detalles]
        nueva = replace(atencion, id=self.sig, detalles=detalles)
        self.datos[self.sig] = nueva
        self.sig += 1
        return nueva

    def actualizar_estado(self, atencion_id, nuevo_estado, total=None):
        a = self.datos.get(atencion_id)
        if a is None:
            return None
        a = replace(a, estado=nuevo_estado, total=a.total if total is None else total)
        self.datos[atencion_id] = a
        return a

    def eliminar(self, atencion_id):
        return self.datos.pop(atencion_id, None) is not None

    def existe_agendada_mismo_dia(self, mascota_id, fecha, excluir_id=None):
        return any(
            a.mascota_id == mascota_id
            and a.estado == AGENDADA
            and a.fecha.date() == fecha.date()
            and a.id != excluir_id
            for a in self.datos.values()
        )

    def existe_con_mascota(self, mascota_id):
        return any(a.mascota_id == mascota_id for a in self.datos.values())


class MascotaRepoFalso(MascotaRepository):
    def __init__(self, mascotas):
        self.datos = {m.id: m for m in mascotas}

    def listar(self, dueno_id=None, especie=None, texto=None): return list(self.datos.values())
    def obtener(self, mascota_id): return self.datos.get(mascota_id)
    def obtener_por_dueno_y_nombre(self, dueno_id, nombre): return None
    def crear(self, mascota): return mascota
    def actualizar(self, mascota): return mascota
    def eliminar(self, mascota_id): return False
    def existe_con_dueno(self, dueno_id): return False


class ServicioRepoFalso(ServicioRepository):
    def __init__(self, servicios):
        self.datos = {s.id: s for s in servicios}

    def listar(self, texto=None, activo=None): return list(self.datos.values())
    def obtener(self, servicio_id): return self.datos.get(servicio_id)
    def obtener_por_codigo(self, codigo): return None
    def obtener_por_nombre(self, nombre): return None
    def crear(self, servicio): return servicio
    def actualizar(self, servicio): return servicio
    def eliminar(self, servicio_id): return False


ROCKY = Mascota(id=1, dueno_id=1, nombre="Rocky", especie="perro", sexo="M")
MICHI = Mascota(id=2, dueno_id=1, nombre="Michi", especie="gato", sexo="H")
CONSULTA = Servicio(id=1, codigo="CON-01", nombre="Consulta general", precio=Decimal("15000"))
VACUNA = Servicio(id=2, codigo="VAC-01", nombre="Vacuna antirrábica", precio=Decimal("12000"))
BANO = Servicio(id=3, codigo="BAN-01", nombre="Baño medicado", precio=Decimal("9000"), activo=False)

MANANA_10 = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)


class BaseAtenciones(unittest.TestCase):
    def setUp(self):
        self.repo = AtencionRepoFalso()
        self.crear = CrearAtencion(
            self.repo,
            MascotaRepoFalso([ROCKY, MICHI]),
            ServicioRepoFalso([CONSULTA, VACUNA, BANO]),
        )
        self.cambiar = CambiarEstadoAtencion(self.repo)
        self.eliminar = EliminarAtencion(self.repo)

    def nueva(self, mascota_id=1, fecha=MANANA_10, detalles=None):
        if detalles is None:
            detalles = [{"servicio_id": 1, "cantidad": 1}, {"servicio_id": 2, "cantidad": 2}]
        return self.crear.ejecutar(mascota_id, fecha, "Control anual y vacunas", detalles)


class TestCrearAtencion(BaseAtenciones):
    def test_crea_con_detalle_y_total_desde_el_detalle(self):
        a = self.nueva()
        self.assertEqual(a.estado, AGENDADA)
        self.assertEqual(len(a.detalles), 2)
        self.assertEqual(a.total, Decimal("39000"))  # 15000 + 2 × 12000
        self.assertEqual(a.detalles[1].servicio_nombre, "Vacuna antirrábica")

    def test_precio_unitario_sale_del_catalogo_no_del_cliente(self):
        a = self.nueva(detalles=[{"servicio_id": 1, "cantidad": 1, "precio_unitario": 1}])
        self.assertEqual(a.detalles[0].precio_unitario, Decimal("15000"))
        self.assertEqual(a.total, Decimal("15000"))

    def test_r1_misma_mascota_mismo_dia_falla(self):
        self.nueva()
        with self.assertRaises(AtencionAgendadaMismoDia):
            self.nueva(fecha=MANANA_10.replace(hour=17))

    def test_r1_otra_mascota_o_otro_dia_si_se_permite(self):
        self.nueva()
        self.nueva(mascota_id=2)
        self.nueva(fecha=MANANA_10 + timedelta(days=1))
        self.assertEqual(len(self.repo.datos), 3)

    def test_r1_no_cuenta_atenciones_canceladas(self):
        a = self.nueva()
        self.cambiar.ejecutar(a.id, CANCELADA)
        self.nueva()  # la cancelada ya no bloquea el día

    def test_r2_servicio_inactivo_falla(self):
        with self.assertRaises(ServicioInactivo):
            self.nueva(detalles=[{"servicio_id": 1, "cantidad": 1}, {"servicio_id": 3, "cantidad": 1}])
        self.assertEqual(self.repo.datos, {})  # no se guardó nada

    def test_servicio_inexistente(self):
        with self.assertRaises(ServicioNoEncontrado):
            self.nueva(detalles=[{"servicio_id": 99, "cantidad": 1}])

    def test_mascota_inexistente(self):
        with self.assertRaises(MascotaNoEncontrada):
            self.nueva(mascota_id=99)

    def test_sin_detalle(self):
        with self.assertRaises(AtencionSinDetalle):
            self.nueva(detalles=[])

    def test_servicio_repetido(self):
        with self.assertRaises(ServicioRepetidoEnAtencion):
            self.nueva(detalles=[{"servicio_id": 1, "cantidad": 1}, {"servicio_id": 1, "cantidad": 2}])

    def test_cantidad_invalida(self):
        for cantidad in (0, -1, 100000, "2", 1.5, True):
            with self.subTest(cantidad=cantidad), self.assertRaises(DatoAtencionInvalido):
                self.nueva(detalles=[{"servicio_id": 1, "cantidad": cantidad}])

    def test_motivo_vacio_o_largo(self):
        for motivo in ("", "   ", "x" * 201):
            with self.subTest(motivo=motivo[:5]), self.assertRaises(DatoAtencionInvalido):
                self.crear.ejecutar(1, MANANA_10, motivo, [{"servicio_id": 1, "cantidad": 1}])

    def test_fecha_sin_hora(self):
        with self.assertRaises(DatoAtencionInvalido):
            self.crear.ejecutar(1, MANANA_10.date(), "Control", [{"servicio_id": 1, "cantidad": 1}])


class TestCambiarEstado(BaseAtenciones):
    def test_flujo_completo_agendada_realizada_pagada(self):
        a = self.nueva()
        self.assertEqual(self.cambiar.ejecutar(a.id, REALIZADA).estado, REALIZADA)
        self.assertEqual(self.cambiar.ejecutar(a.id, PAGADA).estado, PAGADA)

    def test_agendada_a_cancelada(self):
        a = self.nueva()
        self.assertEqual(self.cambiar.ejecutar(a.id, "Cancelada ").estado, CANCELADA)

    def test_transiciones_no_permitidas(self):
        casos = [
            ([], PAGADA),                    # agendada → pagada (salta realizada)
            ([REALIZADA], CANCELADA),        # realizada → cancelada
            ([REALIZADA], AGENDADA),         # no se vuelve atrás
            ([REALIZADA, PAGADA], CANCELADA),
            ([CANCELADA], AGENDADA),
        ]
        for previos, destino in casos:
            with self.subTest(previos=previos, destino=destino):
                self.setUp()
                a = self.nueva()
                for e in previos:
                    self.cambiar.ejecutar(a.id, e)
                with self.assertRaises(TransicionAtencionInvalida):
                    self.cambiar.ejecutar(a.id, destino)

    def test_estado_desconocido(self):
        a = self.nueva()
        with self.assertRaises(EstadoAtencionDesconocido):
            self.cambiar.ejecutar(a.id, "archivada")

    def test_no_encontrada(self):
        with self.assertRaises(AtencionNoEncontrada):
            self.cambiar.ejecutar(99, REALIZADA)

    def test_r2_total_se_recalcula_al_cambiar_estado(self):
        a = self.nueva()
        self.repo.datos[a.id] = replace(a, total=Decimal("1"))  # total desincronizado
        self.assertEqual(self.cambiar.ejecutar(a.id, REALIZADA).total, Decimal("39000"))


class TestEliminarYConsultar(BaseAtenciones):
    def test_elimina_agendada(self):
        a = self.nueva()
        self.eliminar.ejecutar(a.id)
        with self.assertRaises(AtencionNoEncontrada):
            ObtenerAtencion(self.repo).ejecutar(a.id)

    def test_no_elimina_si_no_esta_agendada(self):
        a = self.nueva()
        self.cambiar.ejecutar(a.id, REALIZADA)
        with self.assertRaises(AtencionNoEliminable):
            self.eliminar.ejecutar(a.id)

    def test_eliminar_inexistente(self):
        with self.assertRaises(AtencionNoEncontrada):
            self.eliminar.ejecutar(99)

    def test_listar_filtra_por_estado(self):
        a = self.nueva()
        self.nueva(mascota_id=2)
        self.cambiar.ejecutar(a.id, CANCELADA)
        self.assertEqual(len(ListarAtenciones(self.repo).ejecutar(estado=CANCELADA)), 1)


if __name__ == "__main__":
    unittest.main()
