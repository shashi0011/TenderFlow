from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("admin-register/", views.admin_register, name="admin_register"),
    path("register/", views.vendor_register, name="vendor_register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.add_category, name="add_category"),
    path("categories/delete/<int:id>/", views.category_delete, name="category_delete"),
    path("vendors/", views.vendors_list, name="vendors_list"),
    path("vendors/<int:id>/<str:status>/", views.vendor_status, name="vendor_status"),
    path("rfp/", views.rfp_list, name="rfp_list"),
    path("rfp/add/", views.add_rfp, name="add_rfp"),
    path("quotes/", views.quotes_list, name="quotes_list"),
    path("vendor-dashboard/", views.vendor_dashboard, name="vendor_dashboard"),
    path("vendor-rfp/", views.vendor_rfp, name="vendor_rfp"),
    path("submit-quote/<int:id>/", views.submit_quote, name="submit_quote"),
   
    path("forgot-password/",auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html"),name="password_reset",),
    path("forgot-password/done/",auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),name="password_reset_done",),
    path("reset-password/<uidb64>/<token>/",auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"),name="password_reset_confirm",),
    path("reset-password/done/",auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"),name="password_reset_complete",),
]


