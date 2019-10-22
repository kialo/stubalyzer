from elasticsearch.client.indices import IndicesClient


def create() -> None:
    client = IndicesClient(None)
    client.create(index=None, body=None, params=None, include_type_name=True)
