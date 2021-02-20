import logging
from cloudfoundry_client.networking.entities import EntityManager
from typing import List

_logger = logging.getLogger(__name__)


class Policy:
    def __init__(self, src_id: str, dst_id: str, proto: str, start_port: int, end_port: int):
        self.source = {"id": src_id}

        self.destination = {"id": dst_id, "ports": {}}

        __protos = ["tcp", "udp"]
        if proto.lower() in __protos:
            self.destination["protocol"] = proto.lower()
        else:
            raise ValueError("unknown protocol {got}, known values are {known}" "".format(got=proto, known=__protos))

        if 1 <= start_port <= 65535:
            self.destination["ports"]["start"] = start_port
        else:
            raise ValueError("start port is out of range")

        if 1 <= end_port <= 65535:
            self.destination["ports"]["end"] = end_port
        else:
            raise ValueError("end port is out of range")

    @classmethod
    def from_dict(cls, policy: dict):
        return cls(
            src_id=policy["source"]["id"],
            dst_id=policy["destination"]["id"],
            proto=policy["destination"]["protocol"],
            start_port=policy["destination"]["ports"]["start"],
            end_port=policy["destination"]["ports"]["end"],
        )

    def dump(self):
        return self.__dict__


class PolicyManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(PolicyManager, self).__init__(target_endpoint, client, "/networking/v1/external/policies")

    def create(self, policies: List[Policy]):
        """create a new network policy

        Responses:
        * 200 (successful)
        * 400 (invalid request)
        * 406 (unsupported API version)

        :param policies: the policies to create, a list of Policy objects
        """
        data = list()
        for policy in policies:
            if not isinstance(policy, Policy):
                raise TypeError
            data.append(policy.dump())
        return super(PolicyManager, self)._create({"policies": data})

    def delete(self, policies: List[Policy]):
        """remove a new network policy

        Responses:
        * 200 (successful)
        * 400 (invalid request)
        * 406 (unsupported API version)

        :param policies: the policies to create, a list of Policy objects
        """
        data = list()
        for policy in policies:
            if not isinstance(policy, Policy):
                raise TypeError
            data.append(policy.dump())
        return super(PolicyManager, self)._delete({"policies": data})
