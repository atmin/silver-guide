from django.core.management.base import BaseCommand

from catalog.models import Category, Product

CATEGORIES = [
    {"name": "Хранителни стоки", "slug": "hrani", "parent": None},
    {
        "name": "Плодове и зеленчуци",
        "slug": "hrani-plodove-zelenchutsi",
        "parent": "hrani",
    },
    {"name": "Плодове", "slug": "hrani-plodove", "parent": "hrani-plodove-zelenchutsi"},
    {
        "name": "Зеленчуци",
        "slug": "hrani-zelenchutsi",
        "parent": "hrani-plodove-zelenchutsi",
    },
    {"name": "Млечни продукти", "slug": "hrani-mlechni", "parent": "hrani"},
    {"name": "Сирена", "slug": "hrani-mlechni-sirena", "parent": "hrani-mlechni"},
    {
        "name": "Мляко и кисело мляко",
        "slug": "hrani-mlechni-mlyako",
        "parent": "hrani-mlechni",
    },
    {"name": "Месо и риба", "slug": "hrani-meso", "parent": "hrani"},
    {"name": "Пилешко", "slug": "hrani-meso-pileshko", "parent": "hrani-meso"},
    {
        "name": "Телешко и свинско",
        "slug": "hrani-meso-teleshko",
        "parent": "hrani-meso",
    },
    {"name": "Хляб и тестени", "slug": "hrani-hlyab", "parent": "hrani"},
]

PRODUCTS = [
    # Плодове
    {
        "sku": "PLO-001",
        "title": "Ябълки Голдън, 1 кг",
        "price": "2.49",
        "category": "hrani-plodove",
        "description": "Сладки ябълки сорт Голдън Делишъс.",
    },
    {
        "sku": "PLO-002",
        "title": "Банани, 1 кг",
        "price": "1.89",
        "category": "hrani-plodove",
        "description": "Узрели банани от Еквадор.",
    },
    {
        "sku": "PLO-003",
        "title": "Портокали, 2 кг",
        "price": "3.29",
        "category": "hrani-plodove",
        "description": "Сочни портокали, подходящи за сок.",
    },
    # Зеленчуци
    {
        "sku": "ZEL-001",
        "title": "Домати, 500 г",
        "price": "1.59",
        "category": "hrani-zelenchutsi",
        "description": "Български домати, прясно набрани.",
    },
    {
        "sku": "ZEL-002",
        "title": "Краставици, 1 кг",
        "price": "1.29",
        "category": "hrani-zelenchutsi",
        "description": "Хрупкави краставици.",
    },
    {
        "sku": "ZEL-003",
        "title": "Чушки червени, 500 г",
        "price": "1.79",
        "category": "hrani-zelenchutsi",
        "description": "Сладки червени чушки.",
    },
    # Сирена
    {
        "sku": "SIR-001",
        "title": "Сирене краве, 400 г",
        "price": "3.99",
        "category": "hrani-mlechni-sirena",
        "description": "Традиционно бяло саламурено сирене.",
    },
    {
        "sku": "SIR-002",
        "title": "Кашкавал Витоша, 300 г",
        "price": "4.49",
        "category": "hrani-mlechni-sirena",
        "description": "Зрял кашкавал от краве мляко.",
    },
    # Мляко
    {
        "sku": "MLY-001",
        "title": "Прясно мляко 3.5%, 1 л",
        "price": "1.99",
        "category": "hrani-mlechni-mlyako",
        "description": "Пастьоризирано прясно мляко.",
    },
    {
        "sku": "MLY-002",
        "title": "Кисело мляко Родопи, 400 г",
        "price": "1.49",
        "category": "hrani-mlechni-mlyako",
        "description": "Традиционно Bulgarian yogurt, 3.6% масленост.",
    },
    # Пилешко
    {
        "sku": "PIL-001",
        "title": "Пилешки гърди, 1 кг",
        "price": "7.99",
        "category": "hrani-meso-pileshko",
        "description": "Пресни пилешки гърди без кост.",
    },
    {
        "sku": "PIL-002",
        "title": "Пилешки бутчета, 1 кг",
        "price": "5.49",
        "category": "hrani-meso-pileshko",
        "description": "Охладени пилешки бутчета.",
    },
    # Телешко и свинско
    {
        "sku": "MES-001",
        "title": "Кайма смесена, 500 г",
        "price": "4.99",
        "category": "hrani-meso-teleshko",
        "description": "Смесена кайма телешко/свинско 50/50.",
    },
    {
        "sku": "MES-002",
        "title": "Свински врат, 1 кг",
        "price": "8.99",
        "category": "hrani-meso-teleshko",
        "description": "Охладен свински врат за скара.",
    },
    # Хляб
    {
        "sku": "HLY-001",
        "title": "Хляб Добруджа, 650 г",
        "price": "1.39",
        "category": "hrani-hlyab",
        "description": "Класически бял хляб.",
    },
    {
        "sku": "HLY-002",
        "title": "Баница със сирене, 300 г",
        "price": "2.29",
        "category": "hrani-hlyab",
        "description": "Прясна баница с краве сирене.",
    },
    # Inactive — for testing soft-delete filtering
    {
        "sku": "PLO-INACTIVE",
        "title": "Дюли, 1 кг",
        "price": "2.99",
        "category": "hrani-plodove",
        "is_active": False,
        "description": "Извън сезон.",
    },
]


class Command(BaseCommand):
    help = "Seed the database with sample categories and products"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush", action="store_true", help="Delete existing data before seeding"
        )

    def handle(self, *args, **options):
        if options["flush"]:
            Product.objects.all().delete()
            Category.objects.update(parent=None)
            Category.objects.all().delete()
            self.stdout.write("Flushed existing data.")

        # Create categories, resolving parent slugs
        slug_to_category = {}
        for data in CATEGORIES:
            parent_slug = data.pop("parent")
            data["parent"] = slug_to_category.get(parent_slug)
            cat, created = Category.objects.get_or_create(
                slug=data["slug"], defaults=data
            )
            slug_to_category[cat.slug] = cat
            self.stdout.write(
                f"  {'created' if created else 'exists '} category: {cat.name}"
            )

        # Create products
        for data in PRODUCTS:
            category_slug = data.pop("category")
            data["category"] = slug_to_category[category_slug]
            data.setdefault("is_active", True)
            product, created = Product.objects.get_or_create(
                sku=data["sku"], defaults=data
            )
            self.stdout.write(
                f"  {'created' if created else 'exists '} product:  {product.title}"
            )

        self.stdout.write(self.style.SUCCESS("Seed complete."))
