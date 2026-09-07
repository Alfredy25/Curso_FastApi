from typing import List
from sqlalchemy import Integer, String, ForeignKey, Text, Float, Table, Column
from sqlalchemy.orm import mapped_column, Mapped, relationship

from ejercicios.proyect.db_config.config import Base


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)

    addresses: Mapped[List["Address"]] = relationship("Address", back_populates="customer",
                                                      cascade="all, delete-orphan", lazy="selectin")
    shipments: Mapped[List["Shipment"]] = relationship("Shipment", back_populates="customer", lazy="selectin")

class Address(Base):
    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    street: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(5), nullable=False)

    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"))
    customer: Mapped["Customer"] = relationship("Customer", back_populates="addresses", lazy="joined")

shipment_services = Table("shipment_services",
                          Base.metadata,
                          Column("shipment_id", ForeignKey("shipments.id")),
                          Column("service_id", ForeignKey("extra_services.id"))
                          )

class Shipment(Base):
    __tablename__ = "shipments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tracking_number: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"))
    customer: Mapped["Customer"] = relationship("Customer", back_populates="shipments", lazy="joined")
    label: Mapped["ShippingLabel"] = relationship("ShippingLabel", back_populates="shipment",
                                                  cascade= "all, delete-orphan", uselist=False, lazy="joined")
    services: Mapped[list["ExtraService"]] = relationship("ExtraService", secondary=shipment_services,
                                                          back_populates="shipments", lazy="selectin")

class ShippingLabel(Base):
    __tablename__ = "shipping_labels"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pdf_path: Mapped[str] = mapped_column(Text, nullable=False)
    shipment_id: Mapped[int] = mapped_column(Integer, ForeignKey("shipments.id"), unique=True)
    shipment: Mapped["Shipment"] = relationship("Shipment", back_populates="label")


class ExtraService(Base):
    __tablename__ = "extra_services"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float(asdecimal=True), nullable=False)
    shipments: Mapped[list["Shipment"]] = relationship("Shipment",
                                                       secondary=shipment_services,
                                                       back_populates="services")


