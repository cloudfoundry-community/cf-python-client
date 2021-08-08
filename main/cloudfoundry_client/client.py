import logging
from http import HTTPStatus
from typing import Optional

import requests
from oauth2_client.credentials_manager import CredentialManager, ServiceInformation
from requests import Response

from cloudfoundry_client.doppler.client import DopplerClient
from cloudfoundry_client.errors import InvalidStatusCode
from cloudfoundry_client.networking.v1.external.policies import PolicyManager
from cloudfoundry_client.rlpgateway.client import RLPGatewayClient
from cloudfoundry_client.v2.apps import AppManager as AppManagerV2
from cloudfoundry_client.v2.buildpacks import BuildpackManager as BuildpackManagerV2
from cloudfoundry_client.v2.entities import EntityManager as EntityManagerV2
from cloudfoundry_client.v2.events import EventManager
from cloudfoundry_client.v2.jobs import JobManager as JobManagerV2
from cloudfoundry_client.v2.resources import ResourceManager
from cloudfoundry_client.v2.routes import RouteManager
from cloudfoundry_client.v2.service_bindings import ServiceBindingManager
from cloudfoundry_client.v2.service_brokers import ServiceBrokerManager as ServiceBrokerManagerV2
from cloudfoundry_client.v2.service_instances import ServiceInstanceManager as ServiceInstanceManagerV2
from cloudfoundry_client.v2.service_keys import ServiceKeyManager
from cloudfoundry_client.v2.service_plan_visibilities import ServicePlanVisibilityManager
from cloudfoundry_client.v2.service_plans import ServicePlanManager as ServicePlanManagerV2

from cloudfoundry_client.v3.apps import AppManager
from cloudfoundry_client.v3.buildpacks import BuildpackManager
from cloudfoundry_client.v3.domains import DomainManager
from cloudfoundry_client.v3.feature_flags import FeatureFlagManager
from cloudfoundry_client.v3.isolation_segments import IsolationSegmentManager
from cloudfoundry_client.v3.organization_quotas import OrganizationQuotaManager
from cloudfoundry_client.v3.processes import ProcessManager
from cloudfoundry_client.v3.organizations import OrganizationManager
from cloudfoundry_client.v3.service_brokers import ServiceBrokerManager
from cloudfoundry_client.v3.service_credential_bindings import ServiceCredentialBindingManager
from cloudfoundry_client.v3.service_instances import ServiceInstanceManager
from cloudfoundry_client.v3.service_offerings import ServiceOfferingsManager
from cloudfoundry_client.v3.service_plans import ServicePlanManager
from cloudfoundry_client.v3.spaces import SpaceManager
from cloudfoundry_client.v3.tasks import TaskManager
from cloudfoundry_client.v3.jobs import JobManager

_logger = logging.getLogger(__name__)


class Info:
    def __init__(
        self,
        api_v2_version: str,
        authorization_endpoint: str,
        api_endpoint: str,
        doppler_endpoint: Optional[str],
        log_stream_endpoint: Optional[str],
    ):
        self.api_v2_version = api_v2_version
        self.authorization_endpoint = authorization_endpoint
        self.api_endpoint = api_endpoint
        self.doppler_endpoint = doppler_endpoint
        self.log_stream_endpoint = log_stream_endpoint


class NetworkingV1External(object):
    def __init__(self, target_endpoint: str, credential_manager: "CloudFoundryClient"):
        self.policies = PolicyManager(target_endpoint, credential_manager)


class V2(object):
    def __init__(self, target_endpoint: str, credential_manager: "CloudFoundryClient"):
        self.apps = AppManagerV2(target_endpoint, credential_manager)
        self.buildpacks = BuildpackManagerV2(target_endpoint, credential_manager)
        self.jobs = JobManagerV2(target_endpoint, credential_manager)
        self.service_bindings = ServiceBindingManager(target_endpoint, credential_manager)
        self.service_brokers = ServiceBrokerManagerV2(target_endpoint, credential_manager)
        self.service_instances = ServiceInstanceManagerV2(target_endpoint, credential_manager)
        self.service_keys = ServiceKeyManager(target_endpoint, credential_manager)
        self.service_plan_visibilities = ServicePlanVisibilityManager(target_endpoint, credential_manager)
        self.service_plans = ServicePlanManagerV2(target_endpoint, credential_manager)
        # Default implementations
        self.event = EventManager(target_endpoint, credential_manager)
        self.organizations = EntityManagerV2(target_endpoint, credential_manager, "/v2/organizations")
        self.private_domains = EntityManagerV2(target_endpoint, credential_manager, "/v2/private_domains")
        self.routes = RouteManager(target_endpoint, credential_manager)
        self.services = EntityManagerV2(target_endpoint, credential_manager, "/v2/services")
        self.shared_domains = EntityManagerV2(target_endpoint, credential_manager, "/v2/shared_domains")
        self.spaces = EntityManagerV2(target_endpoint, credential_manager, "/v2/spaces")
        self.stacks = EntityManagerV2(target_endpoint, credential_manager, "/v2/stacks")
        self.user_provided_service_instances = EntityManagerV2(
            target_endpoint, credential_manager, "/v2/user_provided_service_instances"
        )
        self.security_groups = EntityManagerV2(target_endpoint, credential_manager, "/v2/security_groups")
        self.users = EntityManagerV2(target_endpoint, credential_manager, "/v2/users")
        # Resources implementation used by push operation
        self.resources = ResourceManager(target_endpoint, credential_manager)


class V3(object):
    def __init__(self, target_endpoint: str, credential_manager: "CloudFoundryClient"):
        self.apps = AppManager(target_endpoint, credential_manager)
        self.buildpacks = BuildpackManager(target_endpoint, credential_manager)
        self.domains = DomainManager(target_endpoint, credential_manager)
        self.feature_flags = FeatureFlagManager(target_endpoint, credential_manager)
        self.isolation_segments = IsolationSegmentManager(target_endpoint, credential_manager)
        self.jobs = JobManager(target_endpoint, credential_manager)
        self.organizations = OrganizationManager(target_endpoint, credential_manager)
        self.organization_quotas = OrganizationQuotaManager(target_endpoint, credential_manager)
        self.processes = ProcessManager(target_endpoint, credential_manager)
        self.service_brokers = ServiceBrokerManager(target_endpoint, credential_manager)
        self.service_credential_bindings = ServiceCredentialBindingManager(target_endpoint, credential_manager)
        self.service_instances = ServiceInstanceManager(target_endpoint, credential_manager)
        self.service_offerings = ServiceOfferingsManager(target_endpoint, credential_manager)
        self.service_plans = ServicePlanManager(target_endpoint, credential_manager)
        self.spaces = SpaceManager(target_endpoint, credential_manager)
        self.tasks = TaskManager(target_endpoint, credential_manager)


class CloudFoundryClient(CredentialManager):
    def __init__(self, target_endpoint: str, client_id: str = "cf", client_secret: str = "", **kwargs):
        """ "
        :param target_endpoint :the target endpoint
        :param client_id: the client_id
        :param client_secret: the client secret
        :param proxy: a dict object with entries http and https
        :param verify: parameter directly passed to underlying requests library.
            (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``.
        :param token_format: string Can be set to opaque to retrieve an opaque and revocable token.
            See UAA API specifications
        :param login_hint: string. Indicates the identity provider to be used.
            The passed string has to be a URL-Encoded JSON Object, containing the field origin with value as origin_key
            of an identity provider. Note that this identity provider must support the grant type password.
            See UAA API specifications
        """
        proxy = kwargs.get("proxy", dict(http="", https=""))
        verify = kwargs.get("verify", True)
        self.token_format = kwargs.get("token_format")
        self.login_hint = kwargs.get("login_hint")
        target_endpoint_trimmed = target_endpoint.rstrip("/")
        info = self._get_info(target_endpoint_trimmed, proxy, verify=verify)
        if not info.api_v2_version.startswith("2."):
            raise AssertionError("Only version 2 is supported for now. Found %s" % info.api_v2_version)
        service_information = ServiceInformation(
            None, "%s/oauth/token" % info.authorization_endpoint, client_id, client_secret, [], verify
        )
        super(CloudFoundryClient, self).__init__(service_information, proxies=proxy)
        self.v2 = V2(target_endpoint_trimmed, self)
        self.v3 = V3(target_endpoint_trimmed, self)
        self._doppler = (
            DopplerClient(
                info.doppler_endpoint,
                self.proxies["http" if info.doppler_endpoint.startswith("ws://") else "https"],
                self.service_information.verify,
                self,
            )
            if info.doppler_endpoint is not None
            else None
        )
        self._rlpgateway = (
            RLPGatewayClient(
                info.log_stream_endpoint,
                self.proxies["https"],
                self.service_information.verify,
                self,
            )
            if info.log_stream_endpoint is not None
            else None
        )
        self.networking_v1_external = NetworkingV1External(target_endpoint_trimmed, self)
        self.info = info

    @property
    def doppler(self) -> DopplerClient:
        if self._doppler is None:
            raise NotImplementedError("No droppler endpoint for this instance")
        else:

            return self._doppler

    @property
    def rlpgateway(self):
        if self._rlpgateway is None:
            raise NotImplementedError("No RLP gateway endpoint for this instance")
        else:

            return self._rlpgateway

    def _get_info(self, target_endpoint: str, proxy: Optional[dict] = None, verify: bool = True) -> Info:
        root_response = CloudFoundryClient._check_response(
            requests.get("%s/" % target_endpoint, proxies=proxy if proxy is not None else dict(http="", https=""), verify=verify)
        )
        root_info = root_response.json()

        root_links = root_info["links"]
        logging = root_links.get("logging")
        log_stream = root_links.get("log_stream")
        return Info(
            root_links["cloud_controller_v2"]["meta"]["version"],
            self._resolve_login_endpoint(root_links),
            target_endpoint,
            logging.get("href") if logging is not None else None,
            log_stream.get("href") if log_stream is not None else None,
        )

    @staticmethod
    def _resolve_login_endpoint(root_links):
        return (root_links.get("login") or root_links.get("uaa") or root_links.get("self"))["href"]

    @staticmethod
    def _is_token_expired(response: Response) -> bool:
        if response.status_code == HTTPStatus.UNAUTHORIZED.value:
            try:
                json_data = response.json()
                invalid_token_error = "CF-InvalidAuthToken"
                if json_data.get("errors") is not None:  # V3 error response
                    for error in json_data.get("errors"):
                        if error.get("code", 0) == 1000 and error.get("title", "") == invalid_token_error:
                            _logger.info("_is_token_v3_expired - true")
                            return True
                    _logger.info("_is_token_v3_expired - false")
                    return False
                else:  # V2 error response
                    token_expired = json_data.get("code", 0) == 1000 and json_data.get("error_code", "") == invalid_token_error
                    _logger.info("_is_token__v2_expired - %s" % str(token_expired))
                    return token_expired
            except Exception:  # noqa: E722
                return False
        else:
            return False

    @staticmethod
    def _token_request_headers(_) -> dict:
        return dict(Accept="application/json")

    def __getattr__(self, item):
        sub_attr = getattr(self.v2, item, None)
        if sub_attr is not None:
            return sub_attr
        else:
            raise AttributeError("type '%s' has no attribute '%s'" % (type(self).__name__, item))

    def _grant_password_request(self, login: str, password: str) -> dict:
        request = super(CloudFoundryClient, self)._grant_password_request(login, password)
        if self.token_format is not None:
            request["token_format"] = self.token_format
        if self.login_hint is not None:
            request["login_hint"] = self.login_hint
        return request

    def _grant_refresh_token_request(self, refresh_token: str) -> dict:
        request = super(CloudFoundryClient, self)._grant_refresh_token_request(refresh_token)
        if self.token_format is not None:
            request["token_format"] = self.token_format
        return request

    def _grant_client_credentials_request(self) -> dict:
        return dict(
            grant_type="client_credentials",
            scope=" ".join(self.service_information.scopes),
            client_id=self.service_information.client_id,
            client_secret=self.service_information.client_secret,
        )

    def get(self, url: str, params: Optional[dict] = None, **kwargs) -> Response:
        response = super(CloudFoundryClient, self).get(url, params, **kwargs)
        CloudFoundryClient._log_request("GET", url, response)
        return CloudFoundryClient._check_response(response)

    def post(self, url: str, data=None, json=None, **kwargs) -> Response:
        response = super(CloudFoundryClient, self).post(url, data, json, **kwargs)
        CloudFoundryClient._log_request("POST", url, response)
        return CloudFoundryClient._check_response(response)

    def put(self, url: str, data=None, json=None, **kwargs) -> Response:
        response = super(CloudFoundryClient, self).put(url, data, json, **kwargs)
        CloudFoundryClient._log_request("PUT", url, response)
        return CloudFoundryClient._check_response(response)

    def patch(self, url: str, data=None, json=None, **kwargs) -> Response:
        response = super(CloudFoundryClient, self).patch(url, data, json, **kwargs)
        CloudFoundryClient._log_request("PATCH", url, response)
        return CloudFoundryClient._check_response(response)

    def delete(self, url: str, **kwargs) -> Response:
        response = super(CloudFoundryClient, self).delete(url, **kwargs)
        CloudFoundryClient._log_request("DELETE", url, response)
        return CloudFoundryClient._check_response(response)

    @staticmethod
    def _log_request(method: str, url: str, response: Response):
        _logger.debug(
            f"{method}: url={url} - status_code={response.status_code}"
            f" - vcap-request-id={response.headers.get('x-vcap-request-id', 'N/A')} - response={response.text}"
        )

    @staticmethod
    def _check_response(response: Response) -> Response:
        if int(response.status_code / 100) == 2:
            return response
        else:
            try:
                body = response.json()
            except ValueError:
                body = response.text
            raise InvalidStatusCode(HTTPStatus(response.status_code), body, response.headers.get("x-vcap-request-id"))
