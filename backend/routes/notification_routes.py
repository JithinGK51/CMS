from flask import Blueprint, g
from services.notification_service import NotificationService
from middleware.auth_middleware import token_required
from utils.response_helper import success_response, error_response

notif_bp = Blueprint('notification', __name__)

@notif_bp.route('/api/notifications', methods=['GET'])
@token_required
def get_notifications():
    try:
        notifs = NotificationService.get_user_notifications(g.user['id'])
        return success_response("Notifications fetched", notifs)
    except Exception as e:
        return error_response(str(e))
