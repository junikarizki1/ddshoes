from .models import Brand, Category, Product

def menu_links_brand(request):
    links_brand = Brand.objects.all()
    links_category = Category.objects.all()
    all_products_count = Product.objects.filter(is_available=True).count()
    
    return {
        'links_brand': links_brand,
        'links_category': links_category,
        'all_products_count': all_products_count,
    }