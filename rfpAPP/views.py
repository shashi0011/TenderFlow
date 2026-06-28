from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render

from .models import Category, Quote, RFP, RFPVendor, User, VendorProfile


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid Email or Password")
            return redirect("login")

        if user.role == "vendor":
            vendor = VendorProfile.objects.filter(user=user).first()

            if vendor is None:
                messages.error(request, "Vendor profile not found.")
                return redirect("login")

            if vendor.status == "pending":
                messages.warning(request, "Your account is waiting for admin approval.")
                return redirect("login")

            if vendor.status == "rejected":
                messages.error(request, "Your registration has been rejected.")
                return redirect("login")

            login(request, user)
            return redirect("vendor_dashboard")

        login(request, user)
        return redirect("dashboard")

    return render(request, "index.html")


def logout_view(request):
    logout(request)
    return redirect("login")


def admin_register(request):
    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        email = request.POST.get("email")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("admin_register")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("admin_register")

        User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            role="admin",
        )

        messages.success(request, "Admin signup successful. Please login.")
        return redirect("login")

    return render(request, "adminpannel/admin_register.html")


def vendor_register(request):
    categories = Category.objects.all()

    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        email = request.POST.get("email")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("vendor_register")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("vendor_register")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            role="vendor",
        )

        vendor = VendorProfile.objects.create(
            user=user,
            company_name=request.POST.get("company_name"),
            phone=request.POST.get("phone"),
            gst_number=request.POST.get("gst_number"),
            pan_number=request.POST.get("pan_number"),
            annual_revenue=request.POST.get("annual_revenue"),
            no_of_employees=request.POST.get("no_of_employees"),
            status="pending",
        )

        selected_categories = request.POST.getlist("categories")
        vendor.categories.set(selected_categories)

        send_mail(
            "RFP Management Registration",
            "Your registration is submitted. Please wait for admin approval.",
            "noreply@rfp.com",
            [email],
        )

        messages.success(request, "Registration successful. Wait for Admin Approval.")
        return redirect("login")

    return render(request, "register.html", {"categories": categories})


def admin_required(user):
    return user.is_authenticated and user.role == "admin"


def vendor_required(user):
    return user.is_authenticated and user.role == "vendor"


@login_required
def dashboard(request):
    if not admin_required(request.user):
        return redirect("login")

    vendor_count = VendorProfile.objects.count()
    category_count = Category.objects.count()
    rfp_count = RFP.objects.count()
    quote_count = Quote.objects.count()

    return render(request, "adminpannel/dashboard.html", {
        "vendor_count": vendor_count,
        "category_count": category_count,
        "rfp_count": rfp_count,
        "quote_count": quote_count,
    })


@login_required
def category_list(request):
    if not admin_required(request.user):
        return redirect("login")

    categories = Category.objects.all()
    return render(request, "adminpannel/categories.html", {"categories": categories})


@login_required
def add_category(request):
    if not admin_required(request.user):
        return redirect("login")

    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            Category.objects.create(name=name)
            messages.success(request, "Category added successfully.")
            return redirect("category_list")

    return render(request, "adminpannel/add_category.html")


@login_required
def category_delete(request, id):
    if not admin_required(request.user):
        return redirect("login")

    category = get_object_or_404(Category, id=id)
    category.delete()
    messages.success(request, "Category deleted.")
    return redirect("category_list")


@login_required
def vendors_list(request):
    if not admin_required(request.user):
        return redirect("login")

    vendors = VendorProfile.objects.all()
    return render(request, "adminpannel/vendors.html", {"vendors": vendors})


@login_required
def vendor_status(request, id, status):
    if not admin_required(request.user):
        return redirect("login")

    vendor = get_object_or_404(VendorProfile, id=id)

    if status == "approved":
        vendor.status = "approved"
        messages.success(request, "Vendor approved.")

    if status == "rejected":
        vendor.status = "rejected"
        messages.success(request, "Vendor rejected.")

    vendor.save()
    return redirect("vendors_list")


@login_required
def rfp_list(request):
    if not admin_required(request.user):
        return redirect("login")

    rfps = RFP.objects.all()
    return render(request, "adminpannel/rfp.html", {"rfps": rfps})


@login_required
def add_rfp(request):
    if not admin_required(request.user):
        return redirect("login")

    categories = Category.objects.all()
    vendors = VendorProfile.objects.filter(status="approved")

    if request.method == "POST":
        rfp = RFP.objects.create(
            category_id=request.POST.get("category"),
            created_by=request.user,
            title=request.POST.get("title"),
            item_name=request.POST.get("item_name"),
            quantity=request.POST.get("quantity"),
            min_price=request.POST.get("min_price"),
            max_price=request.POST.get("max_price"),
            last_date=request.POST.get("last_date"),
        )

        selected_vendors = request.POST.getlist("vendors")

        for vendor_id in selected_vendors:
            vendor_profile = VendorProfile.objects.get(id=vendor_id)
            RFPVendor.objects.create(rfp=rfp, vendor=vendor_profile.user)

            send_mail(
                "New RFP Assigned",
                "A new RFP has been assigned to you.",
                "noreply@rfp.com",
                [vendor_profile.user.email],
            )

        messages.success(request, "RFP created successfully.")
        return redirect("rfp_list")

    return render(request, "adminpannel/add_rfp.html", {
        "categories": categories,
        "vendors": vendors,
    })


@login_required
def quotes_list(request):
    if not admin_required(request.user):
        return redirect("login")

    quotes = Quote.objects.all()
    return render(request, "adminpannel/quotes.html", {"quotes": quotes})


@login_required
def vendor_dashboard(request):
    if not vendor_required(request.user):
        return redirect("login")

    assigned_count = RFPVendor.objects.filter(vendor=request.user).count()
    open_count = RFPVendor.objects.filter(vendor=request.user, reply_status="open").count()

    return render(request, "venderpannel/vendor_dashboard.html", {
        "assigned_count": assigned_count,
        "open_count": open_count,
    })


@login_required
def vendor_rfp(request):
    if not vendor_required(request.user):
        return redirect("login")

    rfp_vendors = RFPVendor.objects.filter(vendor=request.user)
    return render(request, "venderpannel/vendor_rfp.html", {"rfp_vendors": rfp_vendors})


@login_required
def submit_quote(request, id):
    if not vendor_required(request.user):
        return redirect("login")

    rfp_vendor = get_object_or_404(RFPVendor, id=id, vendor=request.user)

    if rfp_vendor.reply_status == "closed":
        messages.error(request, "Quote already submitted.")
        return redirect("vendor_rfp")

    if request.method == "POST":
        Quote.objects.create(
            rfp_vendor=rfp_vendor,
            price=request.POST.get("price"),
            total_cost=request.POST.get("total_cost"),
        )

        rfp_vendor.reply_status = "closed"
        rfp_vendor.save()

        admin_emails = User.objects.filter(role="admin").values_list("email", flat=True)

        send_mail(
            "New Quote Submitted",
            "A vendor has submitted a quote.",
            "noreply@rfp.com",
            list(admin_emails),
        )

        messages.success(request, "Quote submitted.")
        return redirect("vendor_rfp")

    return render(request, "venderpannel/submit_quote.html", {"rfp_vendor": rfp_vendor})
