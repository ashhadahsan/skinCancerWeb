import re
import random


def decouple_url(url: str):
    bucket_name = re.findall(r"s3://([^/]+)/", url)[0]
    # Extract the object name and file name
    object_name = url.replace(f"s3://{bucket_name}/", "")
    file_name = object_name.split("/")[-1]
    return bucket_name, object_name, file_name


def get_random_avatar() -> str:
    avatars = [
        "adventurer",
        "adventurer-neutral",
        "avataaars",
        "avataaars-neutral",
        "big-ears",
        "big-ears-neutral",
        "big-smile",
        "bottts",
        "bottts-neutral",
        "croodles",
        "croodles-neutral",
        "fun-emoji",
        "icons",
        "identicon",
        "initials",
        "lorelei",
        "lorelei-neutral",
        "micah",
        "miniavs",
        "open-peeps",
        "personas",
        "pixel-art",
        "pixel-art-neutral",
        "shapes",
        "thumbs",
    ]
    index = random.randint(0, len(avatars) - 1)
    return avatars[index]


try:
    from urllib.parse import urlencode, quote
except:
    from urllib import urlencode, quote


def get_url(storage_bucket="long-plexus-376814.appspot.com", file=None):
    return "https://firebasestorage.googleapis.com/v0/b/{0}/o/{1}?alt=media".format(
        storage_bucket, quote(file, safe="")
    )
