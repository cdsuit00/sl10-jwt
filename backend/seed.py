from app import create_app, db
from app.models import User, Expense
from faker import Faker
import random

fake = Faker()

def seed_database():
    app = create_app()
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create test users
        users = []
        for i in range(5):
            user = User(username=f'testuser{i+1}')
            user.password = 'password123'
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        
        # Create expenses for each user
        categories = ['Travel', 'Lodging', 'Food']
        
        for user in users:
            for _ in range(10):
                expense = Expense(
                    category=random.choice(categories),
                    amount=round(random.uniform(10, 500), 2),
                    description=fake.sentence(),
                    user_id=user.id
                )
                db.session.add(expense)
        
        db.session.commit()
        print('Database seeded successfully!')

if __name__ == '__main__':
    seed_database()