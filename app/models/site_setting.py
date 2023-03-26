from mongoengine import DateTimeField, Document, ListField, BooleanField, StringField
from app.utils.logging import logger


class SiteSetting(Document):
    """
    This document only have one document, of which the type is 'site'.
    """

    type = StringField(db_field="n", required=True, unique=True)
    enable_whitelist = BooleanField(db_field="ew", default=True)
    whitelist_emails = ListField(StringField(), db_field="we", default=list)

    meta = {
        "indexes": [
            "type",
        ]
    }

    @classmethod
    def init_site_setting(cls):
        logger.info("-" * 50)
        if cls.objects(type="site").count() > 0:
            logger.info("已有站点设置，跳过初始化")
        else:
            logger.info("初始化站点设置")
            cls(type="site").save()

    @classmethod
    def get(cls) -> "SiteSetting":
        return cls.objects(type="site").first()

    def to_api(self):
        return {
            "enable_whitelist": self.enable_whitelist,
            "whitelist_emails": self.whitelist_emails,
        }