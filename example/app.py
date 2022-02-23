import asyncio
from loader import api
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('app')


async def test():
    await api.set_default(0, 0)
    data = await api.params()
    org_name, org_id = data['Organizations'][0]['OrgName'], data['Organizations'][0]['OrgId']
    delivery_guid, delivery_title = data['DeliveryAddress'][0]['Guid'], data['DeliveryAddress'][0]['Title']
    logger.info(f'ID: {org_id}\nNAME: {org_name}\n'
                f'Address: {delivery_title}\n'
                f'GUID: {delivery_guid}')

    await api.close()


asyncio.run(test())
