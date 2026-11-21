"""
Pruebas de los casos de uso de dueños y mascotas con repositorios falsos en memoria.

No usan Django ni Oracle: demuestran que application/ solo depende de los
puertos. Se ejecutan con:  python -m unittest veterinaria.tests.test_duenos_mascotas -v
"""
import unittest
from dataclasses import replace
from datetime import date, timedelta

from veterinaria.application.exceptions import (
    DuenoEnUso,
    DuenoNoEncontrado,
    EmailDuplicado,
    EmailInvalido,
    EspecieInvalida,
    FechaNacimientoFutura,
    MascotaEnUso,
    MascotaNoEncontrada,
    MascotaNombreDuplicado,
    ReglaIncumplida,
    RutDuplicado,
    RutInvalido,
    SexoInvalido,
)
from veterinaria.application.use_cases.duenos import (
    ActualizarDueno,
    CrearDueno,
    EliminarDueno,
    ListarDuenos,
    ObtenerDueno,
    normalizar_rut,
)
from veterinaria.application.use_cases.mascotas import (
    ActualizarMascota,
    CrearMascota,
    EliminarMascota,
    ListarMascotas,
    ObtenerMascota,
)
from veterinaria.domain.ports.atencion_repository import AtencionRepository
from veterinaria.domain.ports.dueno_repository import DuenoRepository
from veterinaria.domain.ports.mascota_repository import MascotaRepository


class DuenoRepoFalso(DuenoRepository):
    def __init__(self):
        self.datos = {}
        self.sig = 1

    def listar(self, texto=None, comuna=None):
        res = list(self.datos.values())
        if comuna:
            res = [d for d in res if d.comuna.lower() == comuna.lower()]
        if texto:
            t = texto.lower()
            res = [d for d in res if t in d.rut.lower() or t in d.nombre.lower() or t in d.email.lower()]
        return sorted(res, key=lambda d: d.nombre)

    def obtener(self, dueno_id):
        return self.datos.get(dueno_id)

    def obtener_por_rut(self, rut):
        return next((d for d in self.datos.values() if d.rut == rut), None)

    def obtener_por_email(self, email):
        return next((d for d in self.datos.values() if d.email.lower() == email.lower()), None)

    def crear(self, dueno):
        nuevo = replace(dueno, id=self.sig)
        self.datos[self.sig] = nuevo
        self.sig += 1
        return nuevo

    def actualizar(self, dueno):
        if dueno.id not in self.datos:
            return None
        self.datos[dueno.id] = dueno
        return dueno

    def eliminar(self, dueno_id):
        return self.datos.pop(dueno_id, None) is not None


class MascotaRepoFalso(MascotaRepository):
    def __init__(self):
        self.datos = {}
        self.sig = 1

    def listar(self, dueno_id=None, especie=None, texto=None):
        res = list(self.datos.values())
        if dueno_id:
            res = [m for m in res if m.dueno_id == dueno_id]
        if especie:
            res = [m for m in res if m.especie == especie]
        if texto:
            t = texto.lower()
            res = [m for m in res if t in m.nombre.lower() or t in (m.raza or "").lower()]
        return sorted(res, key=lambda m: m.nombre)

    def obtener(self, mascota_id):
        return self.datos.get(mascota_id)

    def obtener_por_dueno_y_nombre(self, dueno_id, nombre):
        return next(
            (m for m in self.datos.values()
             if m.dueno_id == dueno_id and m.nombre.lower() == nombre.lower()),
            None,
        )

    def crear(self, mascota):
        nueva = replace(mascota, id=self.sig)
        self.datos[self.sig] = nueva
        self.sig += 1
        return nueva

    def actualizar(self, mascota):
        if mascota.id not in self.datos:
            return None
        self.datos[mascota.id] = mascota
        return mascota

    def eliminar(self, mascota_id):
        return self.datos.pop(mascota_id, None) is not None

    def existe_con_dueno(self, dueno_id):
        return any(m.dueno_id == dueno_id for m in self.datos.values())


class AtencionRepoFalso(AtencionRepository):
    """Solo implementa lo que usa EliminarMascota; el resto no se necesita."""

    def __init__(self, mascotas_con_atencion=()):
        self.con_atencion = set(mascotas_con_atencion)

    def existe_con_mascota(self, mascota_id):
        return mascota_id in self.con_atencion

    def listar(self, *a, **k): return []
    def obtener(self, atencion_id): return None
    def crear(self, atencion): return atencion
    def actualizar_estado(self, atencion_id, nuevo_estado): return None
    def eliminar(self, atencion_id): return False
    def existe_agendada_mismo_dia(self, mascota_id, dia, excluir_id=None): return False


class TestRut(unittest.TestCase):
    def test_ruts_de_los_datos_de_ejemplo_son_validos(self):
        for rut in ("12.345.678-5", "15.678.234-3", "18.234.567-9",
                    "9.876.543-3", "20.123.456-5", "16.543.210-K"):
            self.assertEqual(normalizar_rut(rut), rut)

    def test_normaliza_formatos(self):
        self.assertEqual(normalizar_rut("123456785"), "12.345.678-5")
        self.assertEqual(normalizar_rut("12345678-5"), "12.345.678-5")
        self.assertEqual(normalizar_rut("16543210-k"), "16.543.210-K")

    def test_digito_verificador_incorrecto(self):
        with self.assertRaises(RutInvalido):
            normalizar_rut("12.345.678-9")

    def test_formato_incorrecto(self):
        for malo in ("", None, "abc", "1-9", "12.345.678-"):
            with self.assertRaises(RutInvalido):
                normalizar_rut(malo)


class TestDuenos(unittest.TestCase):
    def setUp(self):
        self.repo = DuenoRepoFalso()
        self.mascotas = MascotaRepoFalso()
        self.crear = CrearDueno(self.repo)
        self.carolina = self.crear.ejecutar(
            "12.345.678-5", "Carolina Muñoz", "+56 9 8123 4567", "carolina@gmail.com", "Renca"
        )

    def test_crear_guarda_y_normaliza(self):
        d = self.crear.ejecutar(
            "156782343", "  Felipe Rojas ", "+56 9 7234 5678", " FELIPE@Outlook.com ", " Quinta Normal "
        )
        self.assertEqual(d.rut, "15.678.234-3")
        self.assertEqual(d.nombre, "Felipe Rojas")
        self.assertEqual(d.email, "felipe@outlook.com")
        self.assertEqual(d.comuna, "Quinta Normal")
        self.assertIsNotNone(d.id)

    def test_rut_duplicado(self):
        with self.assertRaises(RutDuplicado):
            self.crear.ejecutar("123456785", "Otra", "+56 9 1", "otra@gmail.com", "Renca")

    def test_email_duplicado(self):
        with self.assertRaises(EmailDuplicado):
            self.crear.ejecutar("15.678.234-3", "Otro", "+56 9 1", "CAROLINA@gmail.com", "Renca")

    def test_rut_invalido(self):
        with self.assertRaises(RutInvalido):
            self.crear.ejecutar("12.345.678-0", "X", "+56 9 1", "x@gmail.com", "Renca")

    def test_email_invalido(self):
        for malo in ("sin-arroba", "@gmail.com", "a@b", ""):
            with self.assertRaises(EmailInvalido):
                self.crear.ejecutar("15.678.234-3", "X", "+56 9 1", malo, "Renca")

    def test_campos_obligatorios(self):
        with self.assertRaises(ReglaIncumplida):
            self.crear.ejecutar("15.678.234-3", "  ", "+56 9 1", "x@gmail.com", "Renca")
        with self.assertRaises(ReglaIncumplida):
            self.crear.ejecutar("15.678.234-3", "X", "", "x@gmail.com", "Renca")
        with self.assertRaises(ReglaIncumplida):
            self.crear.ejecutar("15.678.234-3", "X", "+56 9 1", "x@gmail.com", "")

    def test_obtener_y_no_encontrado(self):
        self.assertEqual(ObtenerDueno(self.repo).ejecutar(self.carolina.id).nombre, "Carolina Muñoz")
        with self.assertRaises(DuenoNoEncontrado):
            ObtenerDueno(self.repo).ejecutar(999)

    def test_listar_con_filtros(self):
        self.crear.ejecutar("15.678.234-3", "Felipe Rojas", "+56 9 1", "felipe@outlook.com", "Quinta Normal")
        listar = ListarDuenos(self.repo)
        self.assertEqual([d.nombre for d in listar.ejecutar()], ["Carolina Muñoz", "Felipe Rojas"])
        self.assertEqual(len(listar.ejecutar(comuna="renca")), 1)
        self.assertEqual(len(listar.ejecutar(texto="felipe")), 1)

    def test_actualizar_con_su_propio_rut_y_email_no_es_duplicado(self):
        d = ActualizarDueno(self.repo).ejecutar(
            self.carolina.id, "12.345.678-5", "Carolina Muñoz Soto",
            "+56 9 0000 0000", "carolina@gmail.com", "Independencia",
        )
        self.assertEqual(d.nombre, "Carolina Muñoz Soto")
        self.assertEqual(d.comuna, "Independencia")

    def test_actualizar_con_rut_de_otro_dueno(self):
        otro = self.crear.ejecutar("15.678.234-3", "Felipe", "+56 9 1", "felipe@outlook.com", "Renca")
        with self.assertRaises(RutDuplicado):
            ActualizarDueno(self.repo).ejecutar(
                otro.id, "12.345.678-5", "Felipe", "+56 9 1", "felipe@outlook.com", "Renca"
            )
        with self.assertRaises(EmailDuplicado):
            ActualizarDueno(self.repo).ejecutar(
                otro.id, "15.678.234-3", "Felipe", "+56 9 1", "carolina@gmail.com", "Renca"
            )

    def test_actualizar_no_encontrado(self):
        with self.assertRaises(DuenoNoEncontrado):
            ActualizarDueno(self.repo).ejecutar(
                999, "12.345.678-5", "X", "+56 9 1", "x@gmail.com", "Renca"
            )

    def test_eliminar_dueno_sin_mascotas(self):
        EliminarDueno(self.repo, self.mascotas).ejecutar(self.carolina.id)
        self.assertIsNone(self.repo.obtener(self.carolina.id))

    def test_r3_no_elimina_dueno_con_mascotas(self):
        CrearMascota(self.mascotas, self.repo).ejecutar(self.carolina.id, "Rocky", "perro", "M")
        with self.assertRaises(DuenoEnUso):
            EliminarDueno(self.repo, self.mascotas).ejecutar(self.carolina.id)
        self.assertIsNotNone(self.repo.obtener(self.carolina.id))

    def test_eliminar_dueno_no_encontrado(self):
        with self.assertRaises(DuenoNoEncontrado):
            EliminarDueno(self.repo, self.mascotas).ejecutar(999)


class TestMascotas(unittest.TestCase):
    def setUp(self):
        self.duenos = DuenoRepoFalso()
        self.repo = MascotaRepoFalso()
        self.dueno = CrearDueno(self.duenos).ejecutar(
            "12.345.678-5", "Carolina", "+56 9 1", "carolina@gmail.com", "Renca"
        )
        self.crear = CrearMascota(self.repo, self.duenos)
        self.rocky = self.crear.ejecutar(
            self.dueno.id, " Rocky ", "PERRO", "m", " Labrador ", date(2019, 4, 12)
        )

    def test_crear_guarda_y_normaliza(self):
        self.assertEqual(self.rocky.nombre, "Rocky")
        self.assertEqual(self.rocky.especie, "perro")
        self.assertEqual(self.rocky.sexo, "M")
        self.assertEqual(self.rocky.raza, "Labrador")
        self.assertIsNotNone(self.rocky.id)

    def test_raza_y_fecha_son_opcionales(self):
        m = self.crear.ejecutar(self.dueno.id, "Mishi", "gato", "H", "  ", None)
        self.assertIsNone(m.raza)
        self.assertIsNone(m.fecha_nacimiento)

    def test_dueno_debe_existir(self):
        with self.assertRaises(DuenoNoEncontrado):
            self.crear.ejecutar(999, "Fido", "perro", "M")

    def test_nombre_duplicado_para_el_mismo_dueno(self):
        with self.assertRaises(MascotaNombreDuplicado):
            self.crear.ejecutar(self.dueno.id, "rocky", "gato", "H")

    def test_mismo_nombre_en_otro_dueno_es_valido(self):
        otro = CrearDueno(self.duenos).ejecutar(
            "15.678.234-3", "Felipe", "+56 9 1", "felipe@outlook.com", "Renca"
        )
        m = self.crear.ejecutar(otro.id, "Rocky", "perro", "M")
        self.assertEqual(m.dueno_id, otro.id)

    def test_especie_sexo_y_nombre_invalidos(self):
        with self.assertRaises(EspecieInvalida):
            self.crear.ejecutar(self.dueno.id, "Nemo", "pez", "M")
        with self.assertRaises(SexoInvalido):
            self.crear.ejecutar(self.dueno.id, "Nemo", "perro", "X")
        with self.assertRaises(ReglaIncumplida):
            self.crear.ejecutar(self.dueno.id, "   ", "perro", "M")

    def test_fecha_nacimiento_futura(self):
        manana = date.today() + timedelta(days=1)
        with self.assertRaises(FechaNacimientoFutura):
            self.crear.ejecutar(self.dueno.id, "Futuro", "perro", "M", None, manana)
        # Hoy sí es válido
        self.crear.ejecutar(self.dueno.id, "Recién", "perro", "M", None, date.today())

    def test_obtener_y_no_encontrada(self):
        self.assertEqual(ObtenerMascota(self.repo).ejecutar(self.rocky.id).nombre, "Rocky")
        with self.assertRaises(MascotaNoEncontrada):
            ObtenerMascota(self.repo).ejecutar(999)

    def test_listar_con_filtros(self):
        self.crear.ejecutar(self.dueno.id, "Mishi", "gato", "H", "Doméstico")
        listar = ListarMascotas(self.repo)
        self.assertEqual([m.nombre for m in listar.ejecutar()], ["Mishi", "Rocky"])
        self.assertEqual(len(listar.ejecutar(especie="gato")), 1)
        self.assertEqual(len(listar.ejecutar(texto="labra")), 1)
        self.assertEqual(len(listar.ejecutar(dueno_id=self.dueno.id)), 2)
        self.assertEqual(len(listar.ejecutar(dueno_id=999)), 0)

    def test_actualizar_con_su_propio_nombre_no_es_duplicado(self):
        m = ActualizarMascota(self.repo, self.duenos).ejecutar(
            self.rocky.id, self.dueno.id, "Rocky", "perro", "M", "Golden", None
        )
        self.assertEqual(m.raza, "Golden")

    def test_actualizar_con_nombre_de_otra_mascota_del_dueno(self):
        mishi = self.crear.ejecutar(self.dueno.id, "Mishi", "gato", "H")
        with self.assertRaises(MascotaNombreDuplicado):
            ActualizarMascota(self.repo, self.duenos).ejecutar(
                mishi.id, self.dueno.id, "Rocky", "gato", "H"
            )

    def test_actualizar_no_encontrada_o_dueno_inexistente(self):
        act = ActualizarMascota(self.repo, self.duenos)
        with self.assertRaises(MascotaNoEncontrada):
            act.ejecutar(999, self.dueno.id, "X", "perro", "M")
        with self.assertRaises(DuenoNoEncontrado):
            act.ejecutar(self.rocky.id, 999, "Rocky", "perro", "M")

    def test_eliminar_mascota_sin_atenciones(self):
        EliminarMascota(self.repo, AtencionRepoFalso()).ejecutar(self.rocky.id)
        self.assertIsNone(self.repo.obtener(self.rocky.id))

    def test_r3_no_elimina_mascota_con_atenciones(self):
        eliminar = EliminarMascota(self.repo, AtencionRepoFalso({self.rocky.id}))
        with self.assertRaises(MascotaEnUso):
            eliminar.ejecutar(self.rocky.id)
        self.assertIsNotNone(self.repo.obtener(self.rocky.id))

    def test_eliminar_mascota_no_encontrada(self):
        with self.assertRaises(MascotaNoEncontrada):
            EliminarMascota(self.repo, AtencionRepoFalso()).ejecutar(999)


if __name__ == "__main__":
    unittest.main()
