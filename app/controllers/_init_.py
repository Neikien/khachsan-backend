from .auth import router as auth_router
from .hotel import router as hotel_router
from .room import router as room_router
from .booking import router as booking_router
from .customer import router as customer_router
from .service import router as service_router

__all__ = [
    'auth_router',
    'hotel_router', 
    'room_router',
    'booking_router',
    'customer_router',
    'service_router'
]
