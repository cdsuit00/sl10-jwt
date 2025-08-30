import random
from datetime import date, timedelta
from faker import Faker
from server.app import create_app
from server.extensions import db
from server.models import User, Expense

fake = Faker()

def run():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Users
        users = []
        for i in range(3):
            u = User(username=f"user{i+1}")
            u.set_password("password123")
            db.session.add(u)
            users.append(u)

        db.session.commit()

        categories = ["Travel", "Lodging", "Food"]
        today = date.today()

        # Expenses
        for u in users:
            for _ in range(15):
                d = today - timedelta(days=random.randint(0, 60))
                e = Expense(
                    user_id=u.id,
                    category=random.choice(categories),
                    description=fake.sentence(nb_words=6),
                    amount=round(random.uniform(10, 400), 2),
                    date=d,
                )
                db.session.add(e)

        db.session.commit()
        print("Seed complete. Users: user1/user2/user3 (password: password123)")

if __name__ == "__main__":
    run()
