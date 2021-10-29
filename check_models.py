from Lib.models import Session, User, Item, Orders

session = Session()

user = User(user_id=1, username="user1", first_name="Aria", last_name="Montgomery",
            email="aria@gmail.com", password="12345")
item = Item(item_id=1, name="Book", quantity=25, price=215, status="available")
order = Orders(order_id=1, user_id=1, item_id=1, price=215)

session.add(user)
session.add(item)
session.add(order)

session.commit()

print(session.query(User).all())
print(session.query(Item).all())
print(session.query(Orders).all())

session.close()




