from flask import Blueprint, jsonify, request

from database.models import db, Broadcast, Course
from tools.auth import require_api_key

api = Blueprint('api', __name__)


@api.route('/start_broadcast', methods=['POST'])
@require_api_key
def start_broadcast():
    global next_broadcast_title
    data = request.json
    course = Course.query.filter_by(short_name=data['short_name']).first()
    if course:
        title = next_broadcast_title if next_broadcast_title else f"Трансляция курса: {course.name}"
        new_broadcast = Broadcast(course_id=course.id, is_live=True, title=title)
        db.session.add(new_broadcast)
        db.session.commit()
        return jsonify({"message": "Broadcast started successfully", "broadcast_id": new_broadcast.id, "title": new_broadcast.title}), 200
    return jsonify({"message": "Course not found"}), 404


@api.route('/end_broadcast', methods=['POST'])
@require_api_key
def end_broadcast():
    data = request.json
    broadcast = Broadcast.query.filter_by(id=data['broadcast_id']).first()
    if broadcast:
        broadcast.is_live = False
        broadcast.video_path = data['video_path']
        db.session.commit()
        return jsonify({"message": "Broadcast ended successfully"}), 200
    return jsonify({"message": "Broadcast not found"}), 404
