from django.urls import path
from .import views

urlpatterns = [
	#Leave as empty string for base url
	
	
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
	path('store/',views.store1 ,name="store"),
	path('signup/',views.signup,name="signup"),
	path('login/',views.login,name="login"),
	path('logout/',views.logoutpage,name="logout"),
	path('about/',views.about,name="about"),
	path('contact/',views.contact,name="contact"),
	path('',views.home,name="home"),
	path('update_item/',views.updateItem,name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
    path('productDetail/<int:pk>',views.productDetail,name="productDetail"),


	 
]