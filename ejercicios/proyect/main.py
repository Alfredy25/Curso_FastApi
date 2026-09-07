from ejercicios.proyect.db_config.config import Base, engine, SessionLocal
from entities.models import Customer, Address, Shipment, ShippingLabel, ExtraService

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine) # dev
    with SessionLocal() as session:
        shipment = session.get(Shipment, 3)
        for service in shipment.services:
            print(service.name)


        shipment.services.remove(shipment.services[0])
        session.commit()
        session.refresh(shipment)

        for service in shipment.services:
            print(service.name)

        # cliente = session.get(Customer, 1)
        # shipment = session.get(Shipment, 3)
        #
        # seguro = ExtraService(name="Seguro", price=150)
        # sabado = ExtraService(name="Entrega Sabado", price=80)
        #
        # shipment_created = Shipment(tracking_number="FEDEX12345", status="Pendiente")
        # shipment_created.customer = cliente
        #
        # shipment_created.services.extend([seguro, sabado])
        # shipment.services.extend([seguro, sabado])
        #
        # session.add_all([shipment_created, shipment])
        # session.commit()


        # shipment = session.get(Shipment, 3)
        # # label = ShippingLabel(pdf_path="shipments/shipping_fedex1231.pdf")
        # otra_label = ShippingLabel(pdf_path="shipments/shipping_fedex2358.pdf")
        #
        # shipment.label = otra_label
        # session.add(otra_label)
        # session.commit()
        # session.refresh(shipment)

        # print(f"Ruta de la guia pdf del envío -> {shipment.label.pdf_path}")



        # cliente_juan = session.get(Customer, 2)
        # direccion_delete = session.get(Address, 3)
        # cliente_juan.addresses.remove(direccion_delete)
        # session.commit()
        # session.refresh(cliente_juan)
        # for direccion in cliente_juan.addresses:
        #     print("Direcciones del cliente juan: \n", direccion.street)
        #     print(direccion.city, direccion.postal_code)
        #
        # envio1 = session.get(Shipment, 1)
        # session.delete(envio1)
        # session.commit()


        # # Crear un customer
        # cliente_juan = Customer(name="Juanito", email="juanito12@gmail.com")
        #
        # # Crear dos Addres
        # direccion1 = Address(street="calle langosta", city="ciudad azul", postal_code="11122")
        # direccion2 = Address(street="calle ostras", city="cd guanajuato", postal_code="22233")
        #
        # cliente_juan.addresses.extend([direccion1, direccion2])
        #
        # # Crear 3 Envios
        # envio1 = Shipment(tracking_number="EN23825856", status="Pendiente")
        # envio2 = Shipment(tracking_number="EN23825876", status="Entregado")
        # envio3 = Shipment(tracking_number="EN23825886", status="Enviado")
        #
        # cliente_juan.shipments.append(envio1)
        # cliente_juan.shipments.append(envio2)
        # cliente_juan.shipments.append(envio3)
        #
        # session.add(cliente_juan)
        # session.commit()













        # cliente = Customer(name="Alfredo", email="alfred123@gmail.com")
        #
        # # Crear dos direcciones
        # direccion1 = Address(street="calle 1 num 10", city="ciudad del carmen", postal_code="12345")
        # direccion2 = Address(street="calle segunda num 15", city="ciudad oeste", postal_code="54321")
        #
        # cliente.addresses.extend([direccion1, direccion2])
        #
        # # Otra forma de agregar datos a las tablas
        # # session.add_all([cliente, direccion1, direccion2])
        # session.add(cliente)
        # session.commit()




