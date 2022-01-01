from dataclasses import dataclass, asdict
from enum import Enum, auto
from typing import TYPE_CHECKING, Optional, List

from cloudfoundry_client.v3.entities import EntityManager, ToManyRelationship, Entity, ToOneRelationship

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class RuleProtocol(Enum):
    TCP = auto()
    UDP = auto()
    ICMP = auto()
    ALL = auto()

    def __repr__(self):
        return '%s' % self.name.lower()


@dataclass
class Rule:
    protocol: RuleProtocol
    destination: str
    ports: Optional[str] = None
    type: Optional[int] = None
    code: Optional[int] = None
    description: Optional[str] = None
    log: Optional[bool] = None


@dataclass
class GloballyEnabled:
    running: Optional[bool] = None
    staging: Optional[bool] = None


class SecurityGroupManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(SecurityGroupManager, self).__init__(target_endpoint, client, "/v3/security_groups")

    def create(self,
               name: str,
               rules: Optional[List[Rule]] = None,
               globally_enabled: Optional[GloballyEnabled] = None,
               staging_spaces: Optional[ToManyRelationship] = None,
               running_spaces: Optional[ToManyRelationship] = None) -> Entity:
        payload = self._generate_payload(name, rules, globally_enabled, staging_spaces, running_spaces)
        return super()._create(payload)

    def update(self,
               security_group_id: str,
               name: Optional[str] = None,
               rules: Optional[List[Rule]] = None,
               globally_enabled: Optional[GloballyEnabled] = None,
               staging_spaces: Optional[ToManyRelationship] = None,
               running_spaces: Optional[ToManyRelationship] = None) -> Entity:
        payload = self._generate_payload(name, rules, globally_enabled, staging_spaces, running_spaces)
        return super()._update(security_group_id, payload)

    def remove(self, security_group_id: str):
        return super()._remove(security_group_id)

    def bind_running_security_group_to_spaces(self, security_group_id: str, space_guids: ToManyRelationship) \
            -> ToManyRelationship:
        relationship = "running_spaces"
        return self._bind_spaces(security_group_id, space_guids, relationship)

    def bind_staging_security_group_to_spaces(self, security_group_id: str, space_guids: ToManyRelationship) \
            -> ToManyRelationship:
        relationship = "staging_spaces"
        return self._bind_spaces(security_group_id, space_guids, relationship)

    def unbind_running_security_group_from_space(self, security_group_id: str, space_guid: ToOneRelationship):
        relationship = "running_spaces"
        return self._unbind_space(security_group_id, space_guid, relationship)

    def unbind_staging_security_group_from_space(self, security_group_id: str, space_guid: ToOneRelationship):
        relationship = "staging_spaces"
        return self._unbind_space(security_group_id, space_guid, relationship)

    def _bind_spaces(self, security_group_id: str, space_guids: ToManyRelationship, relationship: str) \
            -> ToManyRelationship:
        url = "%s%s/%s/relationships/%s" % (self.target_endpoint, self.entity_uri, security_group_id, relationship)
        return ToManyRelationship.from_json_object(super()._post(url, space_guids))

    def _unbind_space(self, security_group_id: str, space_guid: ToOneRelationship, relationship: str):
        url = "%s%s/%s/relationships/%s/%s" \
              % (self.target_endpoint, self.entity_uri, security_group_id, relationship, space_guid.guid)
        super()._delete(url)

    @staticmethod
    def _generate_payload(name: Optional[str],
                          rules: Optional[List[Rule]],
                          globally_enabled: Optional[GloballyEnabled],
                          staging_spaces: Optional[ToManyRelationship],
                          running_spaces: Optional[ToManyRelationship]):
        payload = {}
        if name:
            payload["name"] = name
        if rules:
            payload["rules"] = [asdict(rule, dict_factory=lambda x: {k: repr(v) if k == "protocol" else v
                                                                     for (k, v) in x if v is not None})
                                for rule in rules]
        if globally_enabled:
            payload["globally_enabled"] = asdict(globally_enabled,
                                                 dict_factory=lambda x: {k: v for (k, v) in x if v is not None})
        relationships = dict()
        if staging_spaces:
            relationships["staging_spaces"] = staging_spaces
        if running_spaces:
            relationships["running_spaces"] = running_spaces
        if len(relationships) > 0:
            payload["relationships"] = relationships
        return payload
