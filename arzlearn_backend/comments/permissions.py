from rest_framework import permissions


class IsCommentOwner(permissions.BasePermission):
    """فقط صاحب دیدگاه اجازه ویرایش/حذف دارد؛ خواندن (GET) برای همه آزاد است."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user_id == request.user.id
