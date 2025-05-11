from django.db import models
from django.contrib.auth.models import User
import datetime

class DetalleImpuesto(models.Model):
    nombre = models.CharField(max_length=45)
    impuesto = models.DecimalField(max_digits=5, decimal_places=3)

    def __str__(self):
        return f"{self.nombre} ({self.impuesto}%)"

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    cantidad_medida = models.IntegerField()
    unidad_medida = models.CharField(max_length=45)

    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    nombre = models.CharField(max_length=150)
    celular = models.BigIntegerField(null=True, blank=True)
    direccion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    nombre = models.CharField(max_length=100, blank=True)
    celular = models.BigIntegerField(null=True, blank=True)
    email = models.EmailField(max_length=100, blank=True)

    def __str__(self):
        return self.nombre if self.nombre else f"Cliente #{self.pk}"

class Empleado(models.Model):
    id = models.CharField(primary_key=True, max_length=20, editable=False)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    celular = models.BigIntegerField(unique=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Compra(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    proveedor = models.ForeignKey(Proveedor, null=True, blank=True, on_delete=models.PROTECT, related_name='compras')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Compra #{self.pk} - {self.fecha.date()}"

class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    costo_producto = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto} x{self.cantidad}"

class ConfiguracionFactura(models.Model):
    prefijo = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"Prefijo: {self.prefijo}"

class TipoPago(models.Model):
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

class Factura(models.Model):
    id = models.CharField(primary_key=True, max_length=20, editable=False)  # Nuevo ID personalizado
    configuracion = models.ForeignKey('ConfiguracionFactura', on_delete=models.PROTECT, default=1)
    fecha_emision = models.DateField(auto_now_add=True)
    hora_emision = models.TimeField(auto_now_add=True)
    empleado = models.ForeignKey('Empleado', on_delete=models.PROTECT)
    cliente = models.ForeignKey('Cliente', on_delete=models.PROTECT, default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_impuesto = models.ForeignKey('DetalleImpuesto', on_delete=models.PROTECT)
    base_gravable = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_pago = models.ForeignKey('TipoPago', on_delete=models.PROTECT)
    recibido = models.DecimalField(max_digits=10, decimal_places=2) 
    propina = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    anulado = models.BooleanField(default=False)

    def __str__(self):
        return f"Factura #{self.id}"
    def __str__(self):
        estado = " (Anulada)" if self.anulado else ""
        return f"Factura #{self.id}{estado}"
    def save(self, *args, **kwargs):
        if not self.id:
            hoy = datetime.date.today()
            fecha_str = hoy.strftime("%y%m%d")  # Ej: 250407
            cantidad = Factura.objects.filter(fecha_emision=hoy).count() + 1
            self.id = f"{fecha_str}{cantidad:04d}"
        super().save(*args, **kwargs)

class DetalleFactura(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto} x{self.cantidad}"
