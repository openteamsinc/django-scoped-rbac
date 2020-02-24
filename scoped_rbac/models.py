from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from .policy_json import policy_from_json
from .fields import JSONField
from .registry import ResourceType, register_access_controlled_model
import logging


class IdentifiedByIRI(object):
    """
    A model mixin that has an associated RDF IRI indicating its RDF type.

    Subclasses **MUST** define a `resource_type: ResourceType` property.
    """
    ...


class AccessControlledModel(IdentifiedByIRI, models.Model):
    """
    Model classes that will be access controlled in a `rest_framework` view **MUST**
    subclass this class.

    Subclasses **MUST** define a `resource_type: ResourceType` property.
    """

    rbac_context = models.CharField(max_length=2048, default="")

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        register_access_controlled_model(cls)


class Role(AccessControlledModel):
    definition = JSONField(null=False)

    # Required by AccessControlled
    resource_type = ResourceType(
        "rbac.Role", "Role", "A Role definition as a JSON resource."
    )

    @property
    def as_policy(self):
        return policy_from_json(self.definition)


class RoleAssignment(AccessControlledModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    resource_type = ResourceType(
        "rbac.RoleAssignment",
        "RoleAssignment",
        "The assignment of an rbac.Role to a User.",
    )


#TODO Figure out how to support custom User models
UserResourceType = ResourceType(
    "rbac.User",
    "User",
    "A resource representing a User.",
)
