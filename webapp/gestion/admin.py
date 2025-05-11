from django.contrib import admin
from .models import (
    DetalleImpuesto, Producto, Proveedor, Cliente, Empleado,
    Compra, DetalleCompra, ConfiguracionFactura, TipoPago,
    Factura, DetalleFactura
)

@admin.register(DetalleImpuesto)
class DetalleImpuestoAdmin(admin.ModelAdmin):
    search_fields = ['nombre']
    list_display = ['nombre', 'impuesto']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    search_fields = ['nombre']
    list_display = ['nombre', 'precio', 'stock', 'unidad_medida']

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    search_fields = ['nombre']
    list_display = ['nombre', 'celular', 'direccion']

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    search_fields = ['nombre', 'celular', 'email']
    list_display = ['nombre', 'celular', 'email']

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    search_fields = ['nombre', 'apellido', 'celular']
    list_display = ['nombre', 'apellido', 'celular', 'estado']

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    search_fields = ['proveedor__nombre']
    list_display = ['id', 'fecha', 'proveedor', 'total']
    list_filter = ['fecha']

@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):
    search_fields = ['producto__nombre', 'compra__id']
    list_display = ['compra', 'producto', 'cantidad', 'costo_producto']

@admin.register(ConfiguracionFactura)
class ConfiguracionFacturaAdmin(admin.ModelAdmin):
    list_display = ['prefijo']

@admin.register(TipoPago)
class TipoPagoAdmin(admin.ModelAdmin):
    search_fields = ['nombre']
    list_display = ['nombre']

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    search_fields = ['id', 'cliente__nombre', 'empleado__nombre']
    list_display = ['id', 'fecha_emision', 'hora_emision', 'cliente', 'empleado', 'total']
    list_filter = ['fecha_emision', 'tipo_pago']

@admin.register(DetalleFactura)
class DetalleFacturaAdmin(admin.ModelAdmin):
    search_fields = ['producto__nombre', 'factura__id']
    list_display = ['factura', 'producto', 'cantidad', 'precio_unitario']
