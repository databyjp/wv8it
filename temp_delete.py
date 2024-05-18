import utils
import config

client = utils.get_weaviate_client()

coll = client.collections.delete_all()
