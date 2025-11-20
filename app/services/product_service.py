"""Product service layer."""

from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Product
from app.schemas import ProductCreate, ProductRead, ProductUpdate
from app.utils.helpers import apply_pagination, normalize_sku, paginate


class ProductService:
    """Encapsulate product operations."""

    def __init__(self, db: Session):
        self.db = db

    def list_products(
        self,
        sku: Optional[str],
        name: Optional[str],
        active: Optional[bool],
        description: Optional[str],
        page: int,
        limit: int,
    ) -> Tuple[List[ProductRead], int, int]:
        """Return paginated products with total count and total pages."""
        base_query = select(Product)
        count_query = select(func.count(Product.id))

        if sku:
            sku_norm = normalize_sku(sku)
            base_query = base_query.where(Product.sku.ilike(f"%{sku_norm}%"))
            count_query = count_query.where(Product.sku.ilike(f"%{sku_norm}%"))
        if name:
            base_query = base_query.where(Product.name.ilike(f"%{name}%"))
            count_query = count_query.where(Product.name.ilike(f"%{name}%"))
        if description:
            base_query = base_query.where(Product.description.ilike(f"%{description}%"))
            count_query = count_query.where(Product.description.ilike(f"%{description}%"))
        if active is not None:
            base_query = base_query.where(Product.active.is_(active))
            count_query = count_query.where(Product.active.is_(active))

        total_count = self.db.execute(count_query).scalar_one()
        _, total_pages, _ = paginate(total_count, page, limit)
        paginated_query = apply_pagination(base_query.order_by(Product.id.desc()), page, limit)
        results = self.db.execute(paginated_query).scalars().all()

        return [ProductRead.model_validate(prod) for prod in results], total_count, total_pages

    def create_product(self, payload: ProductCreate) -> ProductRead:
        """Create a new product with normalized SKU."""
        product = Product(
            sku=normalize_sku(payload.sku),
            name=payload.name,
            description=payload.description,
            price=payload.price,
            active=payload.active if payload.active is not None else True,
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return ProductRead.model_validate(product)

    def update_product(self, product_id: int, payload: ProductUpdate) -> Optional[ProductRead]:
        """Update product if exists."""
        product = self.db.get(Product, product_id)
        if not product:
            return None

        if payload.sku is not None:
            product.sku = normalize_sku(payload.sku)
        if payload.name is not None:
            product.name = payload.name
        if payload.description is not None:
            product.description = payload.description
        if payload.price is not None:
            product.price = payload.price
        if payload.active is not None:
            product.active = payload.active

        self.db.commit()
        self.db.refresh(product)
        return ProductRead.model_validate(product)

    def delete_product(self, product_id: int) -> bool:
        """Delete product by id."""
        product = self.db.get(Product, product_id)
        if not product:
            return False
        self.db.delete(product)
        self.db.commit()
        return True
