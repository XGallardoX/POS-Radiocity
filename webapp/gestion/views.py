from django.shortcuts import render, redirect, get_object_or_404
from gestion.models import Compra, DetalleCompra, Producto, Proveedor, ConfiguracionFactura, Factura, DetalleFactura, Cliente, Empleado, DetalleImpuesto, TipoPago
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from gestion.analytics.utils import ventas_por_dia, ventas_por_mes
from django.db.models import Sum

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Aquí puedes redirigir según el tipo de usuario:
            if user.is_superuser or user.groups.filter(name='Administrador').exists():
                return redirect('panel_admin')
            else:
                return redirect('panel_user')  # puedes definir esta vista luego
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'gestion/login.html')
def logout_view(request):
    logout(request)
    return redirect('login')
def es_admin(user):
    return user.is_superuser or user.groups.filter(name='Administrador').exists()

def es_user(user):
    return not es_admin(user)

@login_required
@user_passes_test(es_admin)
def panel_admin(request):
    # Obtener productos con stock bajo (ej. menos de 10 unidades)
    productos_bajo_stock = Producto.objects.filter(stock__lt=10).order_by('nombre')

    # Obtener las ventas totales de hoy para el panel del dueño
    today = timezone.localdate()
    ventas_hoy_admin = Factura.objects.filter(fecha_emision=today, anulado=False).aggregate(total_dia=Sum('total'))['total_dia'] or Decimal('0.00')

    context = {
        'productos_bajo_stock': productos_bajo_stock,
        'ventas_hoy_admin': ventas_hoy_admin,
    }
    return render(request, 'gestion/panel_admin.html', context)

@login_required
@user_passes_test(es_user)
def panel_user(request):
    # Obtener las ventas totales de hoy para el negocio (cuadre de caja general)
    # No se filtra por empleado específico, ya que la caja es compartida o manejada por pocos.
    today = timezone.localdate()
    ventas_hoy_general = Factura.objects.filter(
        fecha_emision=today,
        anulado=False
    ).aggregate(total_dia=Sum('total'))['total_dia'] or Decimal('0.00')

    context = {
        'ventas_hoy_general': ventas_hoy_general,
    }
    return render(request, 'gestion/panel_user.html', context)

def ventas_panel(request):
    if request.method == 'POST':
        venta_id = request.POST.get('venta_id')
        try:
            factura = Factura.objects.get(pk=venta_id)
            factura.anulado = not factura.anulado
            factura.save()
            estado = "anulada" if factura.anulado else "reactivada"
            messages.success(request, f"Venta #{factura.id} {estado} correctamente.")
        except Factura.DoesNotExist:
            messages.error(request, "Venta no encontrada.")
        return redirect('ventas_panel')

    query_id = request.GET.get('id')
    if query_id:
        ventas = Factura.objects.filter(id=query_id).select_related('cliente', 'empleado')
    else:
        ventas = Factura.objects.select_related('cliente', 'empleado').order_by('-fecha_emision')

    configuracion = ConfiguracionFactura.objects.first()

    # Aquí se define la URL del panel correcto
    if request.user.is_superuser or request.user.groups.filter(name='Administrador').exists():
        panel_url = 'panel_admin'
    else:
        panel_url = 'panel_user'

    return render(request, 'gestion/ventas_panel.html', {
        'ventas': ventas,
        'query_id': query_id or '',
        'configuracion': configuracion,
        'panel_url': panel_url  # ← Añadimos esto
    })
def detalle_factura(request, factura_id):
    factura = get_object_or_404(
        Factura.objects.select_related('cliente', 'empleado', 'tipo_impuesto', 'tipo_pago', 'configuracion')
                       .prefetch_related('detalles__producto'),
        pk=factura_id
    )
    return render(request, 'gestion/detalle_factura.html', {
        'factura': factura
    })
def compras_panel(request):
    query_id = request.GET.get('id')
    if query_id:
        compras = Compra.objects.filter(id=query_id).select_related('proveedor')
    else:
        compras = Compra.objects.select_related('proveedor').order_by('-fecha')
    return render(request, 'gestion/compras_panel.html', {
        'compras': compras,
        'query_id': query_id or ''
    })

def empleados_panel(request):
    query_id = request.GET.get('id')
    if query_id:
        empleados = Empleado.objects.filter(id=query_id)
    else:
        empleados = Empleado.objects.all()
    return render(request, 'gestion/empleados_panel.html', {
        'empleados': empleados,
        'query_id': query_id or ''
    })

def inventario_panel(request):
    query_nombre = request.GET.get('nombre')
    if query_nombre:
        productos = Producto.objects.filter(nombre__icontains=query_nombre)
    else:
        productos = Producto.objects.all()

    # Determina el panel de retorno y permisos
    if request.user.is_superuser or request.user.groups.filter(name='Administrador').exists():
        panel_url = 'panel_admin'
        puede_editar = True
    else:
        panel_url = 'panel_user'
        puede_editar = False

    return render(request, 'gestion/inventario_panel.html', {
        'productos': productos,
        'query_nombre': query_nombre or '',
        'panel_url': panel_url,
        'puede_editar': puede_editar
    })


def opciones_panel(request):
    configuracion = ConfiguracionFactura.objects.first()

    if request.method == 'POST':
        nuevo_prefijo = request.POST.get('prefijo')
        if configuracion:
            configuracion.prefijo = nuevo_prefijo
            configuracion.save()
        else:
            ConfiguracionFactura.objects.create(prefijo=nuevo_prefijo)
        return redirect('opciones_panel')

    return render(request, 'gestion/opciones_panel.html', {'configuracion': configuracion})

@transaction.atomic
def registrar_compra(request):
    if request.method == 'POST':
        proveedor_id = request.POST.get('proveedor')
        productos = request.POST.getlist('producto')
        cantidades = request.POST.getlist('cantidad')
        costos = request.POST.getlist('costo')

        proveedor = Proveedor.objects.get(pk=proveedor_id) if proveedor_id else None
        compra = Compra.objects.create(proveedor=proveedor)
        total = 0

        for pid, cant, cost in zip(productos, cantidades, costos):
            producto = Producto.objects.get(pk=pid)
            cantidad = int(cant)
            costo_producto = Decimal(cost)

            DetalleCompra.objects.create(
                compra=compra,
                producto=producto,
                cantidad=cantidad,
                costo_producto=costo_producto
            )

            producto.stock += cantidad
            producto.save()

            total += cantidad * costo_producto

        compra.total = total
        compra.save()

        return redirect('compras_panel')

    context = {
        'productos': Producto.objects.all(),
        'proveedores': Proveedor.objects.all(),
    }
    return render(request, 'gestion/registrar_compra.html', context)

@transaction.atomic
def modificar_compra(request, compra_id):
    compra = get_object_or_404(Compra, pk=compra_id)

    if request.method == 'POST':
        proveedor_id = request.POST.get('proveedor')
        productos = request.POST.getlist('producto')
        cantidades = request.POST.getlist('cantidad')
        costos = request.POST.getlist('costo')

        proveedor = Proveedor.objects.get(pk=proveedor_id) if proveedor_id else None
        compra.proveedor = proveedor
        compra.total = 0

        for detalle in compra.detalles.all():
            producto = detalle.producto
            producto.stock -= detalle.cantidad
            producto.save()

        compra.detalles.all().delete()

        total = 0
        for pid, cant, cost in zip(productos, cantidades, costos):
            producto = Producto.objects.get(pk=pid)
            cantidad = int(cant)
            costo_producto = Decimal(cost)

            DetalleCompra.objects.create(
                compra=compra,
                producto=producto,
                cantidad=cantidad,
                costo_producto=costo_producto
            )

            producto.stock += cantidad
            producto.save()

            total += cantidad * costo_producto

        compra.total = total
        compra.save()

        return redirect('compras_panel')

    context = {
        'compra': compra,
        'productos': Producto.objects.all(),
        'proveedores': Proveedor.objects.all(),
    }
    return render(request, 'gestion/modificar_compra.html', context)

@transaction.atomic
def registrar_venta(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        empleado_id = request.POST.get('empleado')
        tipo_pago_id = request.POST.get('tipo_pago')
        impuesto_id = request.POST.get('tipo_impuesto')
        recibido = Decimal(request.POST.get('recibido') or '0.00')
        propina = Decimal(request.POST.get('propina') or '0.00')
        productos = request.POST.getlist('producto')
        cantidades = request.POST.getlist('cantidad')

        cliente = Cliente.objects.get(pk=cliente_id) if cliente_id else None
        empleado = Empleado.objects.get(pk=empleado_id) if empleado_id else None
        tipo_pago = TipoPago.objects.get(pk=tipo_pago_id)
        tipo_impuesto = DetalleImpuesto.objects.get(pk=impuesto_id)

        errores = []

        subtotal = Decimal('0.00')
        productos_validos = []

        for pid, cant in zip(productos, cantidades):
            producto = Producto.objects.get(pk=pid)
            cantidad = int(cant)

            if cantidad > producto.stock:
                errores.append(f"Stock insuficiente para el producto: {producto.nombre} (stock disponible: {producto.stock})")

            subtotal += producto.precio * cantidad
            productos_validos.append((producto, cantidad))

        if errores:
            context = {
                'productos': Producto.objects.all(),
                'clientes': Cliente.objects.all(),
                'empleados': Empleado.objects.all(),
                'tipos_pago': TipoPago.objects.all(),
                'impuestos': DetalleImpuesto.objects.all(),
                'errores': errores,
                'cliente_id': cliente_id,
                'empleado_id': empleado_id,
                'tipo_pago_id': tipo_pago_id,
                'impuesto_id': impuesto_id,
                'propina': propina,
                'recibido': recibido,
                'productos_seleccionados': productos,
                'cantidades_seleccionadas': cantidades
            }
            return render(request, 'gestion/registrar_venta.html', context)

        # Todo OK, seguir con la creación
        impuesto_decimal = tipo_impuesto.impuesto / Decimal('100.0')
        base_gravable = subtotal
        impuesto_total = (base_gravable * impuesto_decimal).quantize(Decimal('0.01'))
        total = base_gravable + impuesto_total + propina

        factura = Factura.objects.create(
            cliente=cliente,
            empleado=empleado,
            subtotal=subtotal,
            base_gravable=base_gravable,
            tipo_impuesto=tipo_impuesto,
            total=total,
            tipo_pago=tipo_pago,
            recibido=recibido,
            propina=propina,
        )

        for producto, cantidad in productos_validos:
            DetalleFactura.objects.create(
                factura=factura,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio
            )
            producto.stock -= cantidad
            producto.save()

        return redirect('ventas_panel')

    # GET normal
    context = {
        'productos': Producto.objects.all(),
        'clientes': Cliente.objects.all(),
        'empleados': Empleado.objects.all(),
        'tipos_pago': TipoPago.objects.all(),
        'impuestos': DetalleImpuesto.objects.all(),
    }
    return render(request, 'gestion/registrar_venta.html', context)


@transaction.atomic
def modificar_venta(request, venta_id):
    factura = get_object_or_404(Factura, pk=venta_id)
    detalles_anteriores = list(factura.detallefactura_set.all())

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        empleado_id = request.POST.get('empleado')
        tipo_pago_id = request.POST.get('tipo_pago')
        impuesto_id = request.POST.get('tipo_impuesto')
        recibido = Decimal(request.POST.get('recibido') or '0.00')
        propina = Decimal(request.POST.get('propina') or '0.00')
        productos = request.POST.getlist('producto')
        cantidades = request.POST.getlist('cantidad')

        cliente = Cliente.objects.get(pk=cliente_id) if cliente_id else None
        empleado = Empleado.objects.get(pk=empleado_id) if empleado_id else None
        tipo_pago = TipoPago.objects.get(pk=tipo_pago_id)
        tipo_impuesto = DetalleImpuesto.objects.get(pk=impuesto_id)

        # Revertir stock anterior
        for detalle in detalles_anteriores:
            producto = detalle.producto
            producto.stock += detalle.cantidad
            producto.save()

        # Eliminar detalles anteriores
        factura.detallefactura_set.all().delete()

        subtotal = Decimal('0.00')
        for pid, cant in zip(productos, cantidades):
            producto = Producto.objects.get(pk=pid)
            cantidad = int(cant)
            subtotal += producto.precio * cantidad

        impuesto_decimal = tipo_impuesto.impuesto / Decimal('100.0')
        base_gravable = subtotal
        impuesto_total = (base_gravable * impuesto_decimal).quantize(Decimal('0.01'))
        total = base_gravable + impuesto_total + propina

        # Actualizar factura
        factura.cliente = cliente
        factura.empleado = empleado
        factura.tipo_pago = tipo_pago
        factura.tipo_impuesto = tipo_impuesto
        factura.subtotal = subtotal
        factura.base_gravable = base_gravable
        factura.total = total
        factura.recibido = recibido
        factura.propina = propina
        factura.save()

        # Crear nuevos detalles y descontar stock
        for pid, cant in zip(productos, cantidades):
            producto = Producto.objects.get(pk=pid)
            cantidad = int(cant)

            if cantidad > producto.stock:
                raise ValueError(f"Stock insuficiente para {producto.nombre}")

            DetalleFactura.objects.create(
                factura=factura,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio
            )

            producto.stock -= cantidad
            producto.save()

        return redirect('ventas_panel')

    context = {
        'factura': factura,
        'detalles': factura.detallefactura_set.all(),
        'productos': Producto.objects.all(),
        'clientes': Cliente.objects.all(),
        'empleados': Empleado.objects.all(),
        'tipos_pago': TipoPago.objects.all(),
        'impuestos': DetalleImpuesto.objects.all(),
    }
    return render(request, 'gestion/modificar_venta.html', context)

@transaction.atomic
def registrar_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio = Decimal(request.POST.get('precio') or '0.00')
        stock = int(request.POST.get('stock') or '0')
        cantidad_medida = int(request.POST.get('cantidad_medida') or '1')
        unidad_medida = request.POST.get('unidad_medida') or ''
        
        if nombre and precio >= 0 and unidad_medida:
            Producto.objects.create(
                nombre=nombre,
                precio=precio,
                stock=stock,
                cantidad_medida=cantidad_medida,
                unidad_medida=unidad_medida
            )
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('inventario_panel')
        else:
            messages.error(request, 'Debe ingresar todos los campos requeridos correctamente.')

    return render(request, 'gestion/registrar_producto.html')

@transaction.atomic
def modificar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)

    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.precio = Decimal(request.POST.get('precio') or '0.00')
        producto.stock = int(request.POST.get('stock') or '0')
        producto.cantidad_medida = int(request.POST.get('cantidad_medida') or '1')
        producto.unidad_medida = request.POST.get('unidad_medida') or ''
        producto.save()
        messages.success(request, 'Producto actualizado exitosamente.')
        return redirect('inventario_panel')

    context = {
        'producto': producto,
    }
    return render(request, 'gestion/modificar_producto.html', context)

@transaction.atomic
def registrar_empleado(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        celular = request.POST.get('celular')

        if not id or not nombre or not apellido or not celular:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('registrar_empleado')

        try:
            celular = int(celular)
            empleado = Empleado(id=id,nombre=nombre, apellido=apellido, celular=celular, estado=True)
            empleado.save()
            messages.success(request, 'Empleado registrado con éxito.')
            return redirect('listar_empleados')
        except ValueError:
            messages.error(request, 'El celular debe ser un número válido.')
        except Exception as e:
            messages.error(request, f'Error al registrar el empleado: {e}')
    
    return render(request, 'gestion/registrar_empleado.html')

@transaction.atomic
def modificar_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, pk=empleado_id)

    if request.method == 'POST':
        empleado.nombre = request.POST.get('nombre', '').strip()
        empleado.apellido = request.POST.get('apellido', '').strip()
        celular = request.POST.get('celular')
        estado = request.POST.get('estado')  # Viene como 'on' si está activo

        if not empleado.nombre or not empleado.apellido or not celular:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('modificar_empleado', empleado_id=empleado_id)

        try:
            empleado.celular = int(celular)
            empleado.estado = True if estado == 'on' else False
            empleado.save()
            messages.success(request, 'Empleado modificado con éxito.')
            return redirect('listar_empleados')
        except ValueError:
            messages.error(request, 'El celular debe ser un número válido.')
        except Exception as e:
            messages.error(request, f'Error al modificar el empleado: {e}')

    return render(request, 'gestion/modificar_empleado.html', {'empleado': empleado})

def factura_pdf(request, factura_id):
    factura = get_object_or_404(Factura.objects.prefetch_related('detalles__producto'), pk=factura_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Factura_{factura.id}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 40

    # Cabecera
    p.setFont("Helvetica-Bold", 16)
    prefijo = factura.configuracion.prefijo  # Asegúrate que existe ese campo
    p.drawCentredString(width / 2, y, f"Factura {prefijo}{factura.id}")
    y -= 30

    # Datos básicos
    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Fecha: {factura.fecha_emision} {factura.hora_emision.strftime('%H:%M')}")
    y -= 20
    p.drawString(50, y, f"Cliente: {factura.cliente}")
    y -= 20
    p.drawString(50, y, f"Empleado: {factura.empleado}")
    y -= 20
    p.drawString(50, y, f"Método de Pago: {factura.tipo_pago}")
    y -= 40

    # Encabezados de tabla
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, "Producto")
    p.drawString(250, y, "Cantidad")
    p.drawString(350, y, "Precio Unit.")
    p.drawString(450, y, "Total")
    y -= 20

    p.setFont("Helvetica", 10)
    for item in factura.detalles.all():
        if y < 100:  # Salto de página si estamos muy abajo
            p.showPage()
            y = height - 40
        total_item = item.precio_unitario * item.cantidad
        p.drawString(50, y, str(item.producto.nombre))
        p.drawString(250, y, str(item.cantidad))
        p.drawString(350, y, f"${item.precio_unitario:.2f}")
        p.drawString(450, y, f"${total_item:.2f}")
        y -= 18

    # Totales
    y -= 30
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, f"Subtotal: ${factura.subtotal:.2f}")
    y -= 18
    p.drawString(50, y, f"Base Gravable: ${factura.base_gravable:.2f}")
    y -= 18
    impuesto = factura.total - factura.base_gravable
    p.drawString(50, y, f"Impuesto ({factura.tipo_impuesto.nombre}): ${impuesto:.2f}")
    y -= 18
    p.drawString(50, y, f"Propina: ${factura.propina:.2f}")
    y -= 18
    p.drawString(50, y, f"Total: ${factura.total:.2f}")
    y -= 18
    p.drawString(50, y, f"Recibido: ${factura.recibido:.2f}")
    y -= 18
    cambio = factura.recibido - factura.total
    p.drawString(50, y, f"Cambio: ${cambio:.2f}")

    p.showPage()
    p.save()
    return response
