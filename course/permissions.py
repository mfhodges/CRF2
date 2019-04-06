from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    TODO: Expand this so it can check if requesting on behalf of another user
    with on_behalf_of = request.session.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the instance.
        return obj.owner == request.user


# I SHOULD MAKE ONE FOR INSTRUCTORS
# lets check if they are masquerading as the owner or if they are the owner
# IF THE OBJECT IS A REQUEST WE MUST CHECK IF THEY ARE ADMIN OR INSTRUCTOR ( OR MASQ AS INSTRUCTOR ) OF THE ASSOCIATED COURSE
