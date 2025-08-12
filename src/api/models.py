from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import enum

db = SQLAlchemy()

class TransactionType(enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

class RecurrenceFrequency(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, default="Usuario")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relaciones
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    recurring_payments = relationship("RecurringPayment", back_populates="user", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Category(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(7), nullable=False, default="#FF69B4")  # Color rosa por defecto
    icon: Mapped[str] = mapped_column(String(50), nullable=False, default="🐱")  # Emoji gatuno por defecto
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relaciones
    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "icon": self.icon,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Transaction(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    transaction_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relaciones
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

    def serialize(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "description": self.description,
            "transaction_type": self.transaction_type.value,
            "transaction_date": self.transaction_date.isoformat() if self.transaction_date else None,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "category": self.category.serialize() if self.category else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class RecurringPayment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    frequency: Mapped[RecurrenceFrequency] = mapped_column(Enum(RecurrenceFrequency), nullable=False)
    next_payment_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relaciones
    user = relationship("User", back_populates="recurring_payments")
    category = relationship("Category", back_populates="recurring_payments")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "amount": self.amount,
            "description": self.description,
            "frequency": self.frequency.value,
            "next_payment_date": self.next_payment_date.isoformat() if self.next_payment_date else None,
            "is_active": self.is_active,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "category": self.category.serialize() if self.category else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }