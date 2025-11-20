from flask import Blueprint, jsonify, request

from ..models import Customer
from ..services import (
    customer_service,
    hotel_service,
    room_service,
)

hotel_bp = Blueprint("hotel", __name__, url_prefix="/api/hotel")


@hotel_bp.get("/available")
def getAvailableRooms():
    ids = room_service.getAvailableRoomIds()
    return jsonify(ids)


@hotel_bp.get("/rooms/available")
def getAvailableRoomDetails():
    rooms = [room.to_dict() for room in hotel_service.getAvailableRooms()]
    return jsonify(rooms)


@hotel_bp.post("/checkin")
def checkIn():
    payload = request.get_json() or {}
    try:
        message = hotel_service.checkIn(payload)
        return jsonify({"message": message})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@hotel_bp.post("/checkout/<int:roomId>")
def checkout(roomId: int):
    try:
        response = hotel_service.checkOut(roomId)
        return jsonify(response.to_dict())
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

