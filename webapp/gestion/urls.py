from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-panel/', views.panel_admin, name='panel_admin'),
    path('admin-panel/usuarios/', views.panel_user, name='panel_user'),

    path('admin-panel/ventas/', views.ventas_panel, name='ventas_panel'),
    path('admin-panel/compras/', views.compras_panel, name='compras_panel'),
    path('admin-panel/empleados/', views.empleados_panel, name='empleados_panel'),
    path('admin-panel/inventario/', views.inventario_panel, name='inventario_panel'),
    path('admin-panel/opciones/', views.opciones_panel, name='opciones_panel'),

    path('compras/registrar/', views.registrar_compra, name='registrar_compra'),
    path('compras/modificar/<int:compra_id>/', views.modificar_compra, name='modificar_compra'),

    path('ventas/registrar/', views.registrar_venta, name='registrar_venta'),
    path('ventas/<str:factura_id>/', views.detalle_factura, name='detalle_factura'),

    path('inventario/registrar/', views.registrar_producto, name='registrar_producto'),
    path('inventario/modificar/<int:producto_id>/', views.modificar_producto, name='modificar_producto'),

    path('empleados/registrar/', views.registrar_empleado, name='registrar_empleado'),
    path('empleados/modificar/<str:empleado_id>/', views.modificar_empleado, name='modificar_empleado'),
    
    path('factura/<str:factura_id>/pdf/', views.factura_pdf, name='factura_pdf'),
    
]
