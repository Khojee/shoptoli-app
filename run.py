# run.py

from shoptoli import create_app
from shoptoli.models import db, Product

app = create_app()

@app.cli.command("seed-data")
def seed_data():
    """Seeds the database with sample products."""
    with app.app_context():
        # Clear existing products first to avoid duplicates
        Product.query.delete()
        
        products_data = [
            {'name': 'Google Pixel 8 Pro', 'description': 'The all-pro phone, powered by Google Tensor G3.', 'price': 12530000.00, 'stock_quantity': 50, 'image_file': 'pixel_8_pro.webp'},
            {'name': 'Google Pixel 8', 'description': 'Powerful and helpful. The best of Google, built around you.', 'price': 8770000.00, 'stock_quantity': 75, 'image_file': 'pixel_8.webp'},
            {'name': 'Google Pixel Fold', 'description': 'The power of a Pixel. The flexibility of a foldable.', 'price': 22550000.00, 'stock_quantity': 20, 'image_file': 'pixel_fold.png'},
            {'name': 'Google Pixel 7a', 'description': 'The Google Pixel 7a is fast, secure, and full of essentials.', 'price': 6260000.00, 'stock_quantity': 100, 'image_file': 'pixel_7a.webp'},
            {'name': 'Google Pixel Watch 2', 'description': 'Help by Google. Health by Fitbit. All on your wrist.', 'price': 4390000.00, 'stock_quantity': 60, 'image_file': 'pixel_watch_2.webp'},
            {'name': 'Google Pixel Buds Pro', 'description': 'Big sound. Small package. With premium, immersive sound.', 'price': 2510000.00, 'stock_quantity': 120, 'image_file': 'pixel_buds_pro.png'},
        ]

        for data in products_data:
            product = Product(**data)
            db.session.add(product)
        
        db.session.commit()
        print("Database seeded with Google Pixel products!")

if __name__ == '__main__':
    app.run(debug=True)