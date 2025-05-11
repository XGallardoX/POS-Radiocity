# analytics/utils.py
from gestion.models import DetalleFactura
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncMonth

def ventas_por_dia(year):
    """
    Devuelve las ventas por producto agrupadas por día en un año dado.
    """
    ventas = (
        DetalleFactura.objects
        .filter(factura__fecha_emision__year=year, factura__anulado=False)
        .annotate(dia=TruncDay('factura__fecha_emision'))
        .values('dia', 'producto__nombre')
        .annotate(total=Sum('cantidad'))
        .order_by('dia')
    )
    return ventas

def ventas_por_mes(year):
    """
    Devuelve las ventas por producto agrupadas por mes en un año dado.
    """
    ventas = (
        DetalleFactura.objects
        .filter(factura__fecha_emision__year=year, factura__anulado=False)
        .annotate(mes=TruncMonth('factura__fecha_emision'))
        .values('mes', 'producto__nombre')
        .annotate(total=Sum('cantidad'))
        .order_by('mes')
    )
    return ventas
