from .user import UserRepository
from .category import CategoryRepository
from .item import ItemRepository
from .rental import RentalRepository
from .conversation import ConversationRepository
from .message import MessageRepository
from .review import ReviewRepository

class Repository:
    def __init__(self, session):
        self.users = UserRepository(session)
        self.categories = CategoryRepository(session)
        self.items = ItemRepository(session)
        self.rentals = RentalRepository(session)
        self.conversations = ConversationRepository(session)
        self.messages = MessageRepository(session)
        self.reviews = ReviewRepository(session)