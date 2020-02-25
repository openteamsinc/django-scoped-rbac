from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .filters import RbacFilter
from .models import Role, RoleAssignment, UserResourceType
from .permissions import DEFAULT_CONTEXT
from .serializers import (
    RoleSerializer,
    RoleAssignmentSerializer,
    UserSerializer,
)


class DefaultPageNumberPagination(PageNumberPagination):
    page_size = 100


class AccessControlledAPIView:
    """
    This `APIView` interface is required for non-object based views in combination with
    the `IsAuthorized` permission class.
    """
    filter_backends = [RbacFilter]

    def resource_type_iri_for(self, request):
        """
        Return the resource_type_iri for the resource type indicated by this request.
        """

        if self.action == "list":
            return self.list_type_iri
        else:
            return self.resource_type_iri


    @property
    def resource_type_iri(self):
        """
        Subclasses **MUST** override this method.
        Return the resource_type_iri for the base resource supported by this view.
        """

        raise NotImplementedError()


    @property
    def list_type_iri(self):
        """
        Return the list resource_type_iri for this view.
        """

        return f"{self.resource_type_iri}/list"


class AccessControlledModelViewSet(ModelViewSet, AccessControlledAPIView):
    def get_success_headers(self, instance):
        try:
            return {
                "Location": reverse(self.basename + "-detail", args=[instance.id])
            }
        except (TypeError, KeyError):
            return {}

    def list(self, request, *args, **kwargs):
        #TODO restrict listing to authorized contexts
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.instance)
        # headers["etag"] = serializer.etag()
        # headers["last-modified"] = serializer.last_modified()
        # if serializer.link_header_content():
            # headers["link"] = serializer.link_header_content()
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def retrieve(self, request, *args, **kwargs):
        #TODO authorize
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        #TODO authorize
        return super().update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        #TODO authorize
        return super().delete(request, *args, **kwargs)


class RoleViewSet(AccessControlledModelViewSet):
    """
    TODO restrict queryset to authorized contexts for user
    """

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    pagination_class = DefaultPageNumberPagination

    @property
    def resource_type_iri(self):
        return Role.resource_type.iri


class RoleAssignmentViewSet(AccessControlledModelViewSet):
    """
    TODO restrict queryset to authorized contexts for user
    """

    queryset = RoleAssignment.objects.all()
    serializer_class = RoleAssignmentSerializer
    pagination_class = DefaultPageNumberPagination

    @property
    def resource_type_iri(self):
        return RoleAssignment.resource_type.iri


class UserViewSet(AccessControlledModelViewSet):
    """
    API which allows users to be viewed or edited.
    TODO restrict queryset to authorized contexts for user
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = DefaultPageNumberPagination

    @property
    def resource_type_iri(self):
        return UserResourceType.iri
