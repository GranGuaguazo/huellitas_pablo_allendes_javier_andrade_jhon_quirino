"""
Pruebas de los casos de uso de servicios con repositorios falsos en memoria.

No usan Django ni Oracle: demuestran que application/ solo depende de los
puertos. Se ejecutan con:  python -m unittest veterinaria.tests.test_servicios -v
"""
import unittest
from dataclasses import replace
from decimal import Decimal

from veterinaria.application.exceptions import (
    CodigoServicioDuplicado,
    CodigoServicioInvalido,
    NombreServicioDuplicado,
    PrecioServicioInvalido,
    ServicioEnUso,
    ServicioNoEncontrado,
)
from veterinaria.application.use_cases.servicios import (
    ActualizarServicio,
    CrearServicio,
    EliminarServicio,
    ListarServicios,
    ObtenerServicio,
)
from veterinaria.domain.entities.servicio import Servicio
from veterinaria.domain.ports.detalle_atencion_repository import DetalleAtencionRepository
from veterinaria.domain.ports.servicio_repository import ServicioRepository


class ServicioRepoFalso(ServicioRepository):
    def __init__(self):
        self.datos = {}
        self.sig = 1

    def listar(self, texto=None, activo=None):
        res = list(self.datos.values())
        if activo is not None:
            res = [s for s in res if s.activo == activo]
        if texto:
            t = texto.lower()
            res = [s for s in res if t in s.codigo.lower() or t in s.nombre.lower()]
        return sorted(res, key=lambda s: s.nombre)

    def obtener(self, servicio_id):
        return self.datos.get(servicio_id)

    def obtener_por_codigo(self, codigo):
        return next((s for s in self.datos.values() if s.codigo == codigo), None)

    def obtener_por_nombre(self, nombre):
        return next((s for s in self.datos.values() if s.nombre == nombre), None)

    def crear(self, servicio):
        nuevo = replace(servicio, id=self.sig)
        self.datos[self.sig] = nuevo
        self.sig += 1
        return nuevo

    def actualizar(self, servicio):
        if servicio.id not in self.datos:
            return None
        self.datos[servicio.id] = servicio
        return servicio

    def eliminar(self, servicio_id):
        return self.datos.pop(servicio_id, None) is not None


class DetalleRepoFalso(DetalleAtencionRepository):
    def __init__(self, servicios_usados=()):
        self.usados = set(servicios_usados)

    def listar_por_atencion(self, atencion_id):
        return []

    def existe_con_servicio(self, servicio_id):
        return servicio_id in self.usados


class TestServicios(unittest.TestCase):
    def setUp(self):
        self.repo = ServicioRepoFalso()
        self.crear = CrearServicio(self.repo)
        self.vacuna = self.crear.ejecutar("VAC-01", "Vacuna antirrábica", 12000)

    def test_crear_guarda_y_normaliza(self):
        s = self.crear.ejecutar(" des-01 ", "  Desparasitación ", "8500.50", "Dosis por peso")
        self.assertEqual(s.codigo, "DES-01")
        self.assertEqual(s.nombre, "Desparasitación")
        self.assertEqual(s.precio, Decimal("8500.50"))
        self.assertTrue(s.activo)
        self.assertIsNotNone(s.id)

    def test_codigo_con_formato_invalido(self):
        for malo in ("abc", "VAC1", "VA-01", "VAC-001", "", None):
            with self.assertRaises(CodigoServicioInvalido):
                self.crear.ejecutar(malo, "Otro", 1000)

    def test_precio_negativo_o_invalido(self):
        with self.assertRaises(PrecioServicioInvalido):
            self.crear.ejecutar("CON-01", "Consulta", -1)
        with self.assertRaises(PrecioServicioInvalido):
            self.crear.ejecutar("CON-01", "Consulta", "abc")

    def test_precio_cero_es_valido(self):
        self.assertEqual(self.crear.ejecutar("CON-01", "Control gratis", 0).precio, 0)

    def test_codigo_duplicado(self):
        with self.assertRaises(CodigoServicioDuplicado):
            self.crear.ejecutar("VAC-01", "Otro nombre", 5000)

    def test_nombre_duplicado(self):
        with self.assertRaises(NombreServicioDuplicado):
            self.crear.ejecutar("VAC-09", "Vacuna antirrábica", 5000)

    def test_obtener_y_no_encontrado(self):
        self.assertEqual(ObtenerServicio(self.repo).ejecutar(self.vacuna.id).codigo, "VAC-01")
        with self.assertRaises(ServicioNoEncontrado):
            ObtenerServicio(self.repo).ejecutar(999)

    def test_listar_con_filtros(self):
        self.crear.ejecutar("ECO-01", "Ecografía", 35000, activo=False)
        listar = ListarServicios(self.repo)
        self.assertEqual(len(listar.ejecutar()), 2)
        self.assertEqual([s.codigo for s in listar.ejecutar(activo=True)], ["VAC-01"])
        self.assertEqual([s.codigo for s in listar.ejecutar(texto="eco")], ["ECO-01"])

    def test_actualizar_con_su_propio_codigo_no_es_duplicado(self):
        s = ActualizarServicio(self.repo).ejecutar(
            self.vacuna.id, "VAC-01", "Vacuna antirrábica", 13000, activo=False
        )
        self.assertEqual(s.precio, 13000)
        self.assertFalse(s.activo)

    def test_actualizar_con_codigo_de_otro_servicio(self):
        otro = self.crear.ejecutar("DES-01", "Desparasitación", 8500)
        with self.assertRaises(CodigoServicioDuplicado):
            ActualizarServicio(self.repo).ejecutar(otro.id, "VAC-01", "Desparasitación", 8500)
        with self.assertRaises(NombreServicioDuplicado):
            ActualizarServicio(self.repo).ejecutar(otro.id, "DES-01", "Vacuna antirrábica", 8500)

    def test_actualizar_no_encontrado(self):
        with self.assertRaises(ServicioNoEncontrado):
            ActualizarServicio(self.repo).ejecutar(999, "ZZZ-01", "Nada", 1)

    def test_eliminar_libre(self):
        EliminarServicio(self.repo, DetalleRepoFalso()).ejecutar(self.vacuna.id)
        self.assertIsNone(self.repo.obtener(self.vacuna.id))

    def test_eliminar_protegido_si_se_usa_en_atenciones(self):
        usado = DetalleRepoFalso(servicios_usados={self.vacuna.id})
        with self.assertRaises(ServicioEnUso):
            EliminarServicio(self.repo, usado).ejecutar(self.vacuna.id)
        self.assertIsNotNone(self.repo.obtener(self.vacuna.id))  # sigue existiendo

    def test_eliminar_no_encontrado(self):
        with self.assertRaises(ServicioNoEncontrado):
            EliminarServicio(self.repo, DetalleRepoFalso()).ejecutar(999)


if __name__ == "__main__":
    unittest.main()