# Sistema de Gestión de Pedidos de Exportación – Vircatex International Sourcing SAC

Trabajo final del curso IS275 Fundamentos de Programación 2.

## Cómo ejecutar

Requisito: Python 3.10 o superior. No usa librerías externas.

```
python main.py              # abre el menú
python -m unittest -v       # corre las pruebas
```

En el menú, la opción **6** carga datos de ejemplo (3 clientes, 3 talleres, 4 prendas y 2 pedidos)
para probar sin digitar todo.

## Estructura

```
main.py                  inicio del programa
vircatex/
  empresas.py            Empresa -> Cliente, Proveedor           (herencia)
  prendas.py             Prenda (abstracta) -> Polo, Camisa, Chompa (polimorfismo)
  fabrica.py             FabricaPrendas                          (patrón Factory)
  descuentos.py          EstrategiaDescuento y sus variantes     (patrón Strategy)
  pedido.py              Pedido y LineaPedido                    (composición, cálculos)
  calidad.py             InspeccionCalidad (tabla AQL 2.5)
  sistema.py             SistemaVircatex                         (patrón Singleton)
  excepciones.py         excepciones propias
  entradas.py            lectura validada del teclado
  menu.py                menú de consola
  datos_demo.py          datos de ejemplo
tests/                   pruebas unitarias (unittest)
docs/                    modelo UML para Modelio (.xmi) e imágenes de los diagramas
```

Los diagramas se abren en Modelio 6.2 importando `docs/Vircatex_modelo.xmi`.
