from django.urls import path,include,re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.views.static import serve 


urlpatterns = [ 
    path('',views.home,name='home'),
    path('careers/',views.careers,name='careers'),
    path('approvals/',views.approvals,name='approvals'),
    path('airplatforms/',views.airplatforms,name='airplatforms'),
    path('contact/',views.contact,name='contact'),
    path('fixed_wing/',views.fixed_wing,name='fixed_wing'),
    path('rotary_wing/',views.rotary_wing,name='rotary_wing'),
    path('land_platforms/',views.land_platforms,name='land_platforms'),
    path('profile/',views.profile,name='profile'),
    path('products/',views.products,name='products'),
    path('approvals/',views.approvals,name='approvals'),
    path('careers/',views.careers,name='careers'),
    path('cart/',views.cart,name='cart'),
    path('checkout/',views.checkout,name='checkout'),
    path('product_detail/<int:id>/',views.product_detail,name='product_detail'),
    path('news/',views.news,name='news'),
    path('signup/',views.signup,name='signup'),
    path('login/',views.login_view,name='login'),
    path('password_reset/',views.password_reset,name='password_reset'),
    path('register_user/',views.register_user,name='register_user'),
    path('login_user/',views.login_user,name='login_user'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('update_cart_item/', views.update_cart_item, name='update_cart_item'),
    path("place-order-ajax/", views.place_order_ajax, name="place_order_ajax"),
    path("order_success/<int:order_id>/", views.order_success, name="order_success"),
    path('orders_page/', views.orders_page, name='orders_page'),
    path("contact_submit", views.contact_submit, name="contact_submit"),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path("send_recovery_code/", views.send_recovery_code, name="send_recovery_code"),
    path("reset_password/", views.reset_password, name="reset_password"),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



 

