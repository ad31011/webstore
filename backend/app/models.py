"""Modelet ORM, të njëjta me tabelat te schema.sql."""
from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True, nullable=False)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    role = relationship("Role")


class LookupMixin:
    """Kolonat e përbashkëta për tabelat e thjeshta (id, name)."""
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)


class Gender(LookupMixin, Base):
    __tablename__ = "genders"


class Category(LookupMixin, Base):
    __tablename__ = "categories"


class Brand(LookupMixin, Base):
    __tablename__ = "brands"


class Size(LookupMixin, Base):
    __tablename__ = "sizes"


class Color(LookupMixin, Base):
    __tablename__ = "colors"


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    initial_quantity = Column(Integer, nullable=False, default=0)
    gender_id = Column(Integer, ForeignKey("genders.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    brand_id = Column(Integer, ForeignKey("brands.id"))
    color_id = Column(Integer, ForeignKey("colors.id"))
    size_id = Column(Integer, ForeignKey("sizes.id"))
    created_at = Column(DateTime, server_default=func.now())

    gender = relationship("Gender")
    category = relationship("Category")
    brand = relationship("Brand")
    color = relationship("Color")
    size = relationship("Size")
    discounts = relationship("Discount", back_populates="product", cascade="all, delete-orphan")


class Discount(Base):
    __tablename__ = "discounts"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    percentage = Column(Numeric(5, 2), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    product = relationship("Product", back_populates="discounts")


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(30))
    address = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    total_amount = Column(Numeric(10, 2), default=0)
    created_at = Column(DateTime, server_default=func.now())
    client = relationship("Client")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    order = relationship("Order", back_populates="items")
    product = relationship("Product")