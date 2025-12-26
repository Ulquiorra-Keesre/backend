from .orm import UserRepository
from .orm import CategoryRepository
from .orm import ItemRepository
from .orm import RentalRepository
from .orm import ConversationRepository
from .orm import MessageRepository
from .orm import ReviewRepository

class Repository:
    def __init__(self, session):
        self.users = UserRepository(session)
        self.categories = CategoryRepository(session)
        self.items = ItemRepository(session)
        self.rentals = RentalRepository(session)
        self.conversations = ConversationRepository(session)
        self.messages = MessageRepository(session)
        self.reviews = ReviewRepository(session)