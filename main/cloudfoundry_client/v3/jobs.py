import types
from typing import TYPE_CHECKING

import polling2

from cloudfoundry_client.v3.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class JobTimeout(Exception):
    pass


class JobManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(JobManager, self).__init__(target_endpoint, client, "/v3/jobs")

    def wait_for_job_completion(
        self,
        job_guid: str,
        step: int = 1,
        step_function: types.FunctionType = lambda step: min(step + step, 60),
        poll_forever: bool = False,
        timeout: int = 600,
    ) -> Entity:
        try:
            return polling2.poll(
                lambda: self.get(job_guid),
                step=step,
                step_function=step_function,
                poll_forever=poll_forever,
                timeout=timeout,
                check_success=lambda job: job["state"] != "PROCESSING",
            )
        except polling2.TimeoutException as e:
            raise JobTimeout(e)
