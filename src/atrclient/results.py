import atrclient.models as models


class Announce(models.schema.Strict):
    success: bool = models.schema.example(True)
    message: str = models.schema.example("Announcement sent.")
