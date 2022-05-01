class Job:
    # base_job = Config.base_job
    binary: str
    flags: dict[str, str] = {}
    priority: int = 200


class Config:
    name: str

    base_job: Job

    jobs: DefaultNamespace = DefaultNamespace(
        train=Job(),
    )
