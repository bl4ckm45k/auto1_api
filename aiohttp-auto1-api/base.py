import asyncio
import logging
import ssl
import typing
from typing import Dict, List, Optional, Union, Type

import aiohttp
import certifi
import ujson as json
import api
from utils.payload import generate_payload

logger = logging.getLogger('auto1.by')


class BaseApi:

    def __init__(
            self,
            login: str,
            password: str,
            loop: Optional[Union[asyncio.BaseEventLoop, asyncio.AbstractEventLoop]] = None,
            connections_limit: int = None,
            timeout: typing.Optional[typing.Union[int, float, aiohttp.ClientTimeout]] = None,
    ):
        """You can read the documentation API here: https://auto1.by/help/api2

        :param login: login from auto1.by
        :type login: 'str'
        :param password: password from auto1.by
        :type password: 'str'
        """

        self._main_loop = loop
        # Authentication
        self._login = login
        self._password = password
        self._org_id = None
        self._point = None
        self._order_type = None
        ssl_context = ssl.create_default_context(cafile=certifi.where())

        self._session: Optional[aiohttp.ClientSession] = None
        self._connector_class: Type[aiohttp.TCPConnector] = aiohttp.TCPConnector
        self._connector_init = dict(limit=connections_limit, ssl=ssl_context)

        self._timeout = None
        self.timeout = timeout

    async def get_new_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
            connector=self._connector_class(**self._connector_init),
            json_serialize=json.dumps
        )

    @property
    def loop(self) -> Optional[asyncio.AbstractEventLoop]:
        return self._main_loop

    async def get_session(self) -> Optional[aiohttp.ClientSession]:
        if self._session is None or self._session.closed:
            self._session = await self.get_new_session()

        if not self._session._loop.is_running():
            await self._session.close()
            self._session = await self.get_new_session()

        return self._session

    def session(self) -> Optional[aiohttp.ClientSession]:
        return self._session

    async def close(self):
        """
        Close all client sessions
        """
        if self._session:
            await self._session.close()

    async def request(self, method: str,
                      data: Optional[Dict] = None, post: bool = False, **kwargs) -> Union[List, Dict, bool]:
        """
        Make an request to ABCP API

        :param method: API method
        :type method: :obj:`str`
        :param data: request parameters
        :param post:
        :type data: :obj:`dict`
        :return: result
        :rtype: Union[List, Dict]
        :raise: :obj:`utils.exceptions`
        """

        return await api.make_request(await self.get_session(), self._login, self._password,
                                      method, data, post, timeout=self.timeout, **kwargs)

    async def params(self):
        """Возвращает список параметров."""
        return await self.request(api.Methods.PARAMS)

    async def set_default(self, org_id: int = 0, delivery_id: int = 0):
        data = await self.params()
        logger.info(f"\nОтгружающая организация: {data['Organizations'][org_id]['OrgName']}\n"
                    f"Тип заказа: {data['Organizations'][org_id]['OrderTypeName']}\n"
                    f"Адрес доставки: {data['DeliveryAddress'][delivery_id]['Title']}")
        self._org_id, self._order_type, self._point = data['Organizations'][org_id]['OrgId'], \
                                                      data['Organizations'][org_id][
                                                          'OrderType'], data['DeliveryAddress'][delivery_id]['Guid']

    async def search(self, pattern: Union[str, int], search_type: str = 'as'):
        """
        :param pattern: Артикул товара
        :param search_type: По умолчанию только из наличия auto1.by. None чтобы по всем складам
        :return: dict
        """
        org_id = self._org_id
        order_type = self._order_type
        point = self._point
        payload = generate_payload(**locals())
        return await self.request(api.Methods.SEARCH, payload)

    async def brand_by_article(self, pattern: Union[str, int]):
        """
        :param pattern: Артикул товара
        :return: list of dicts брендов
        """
        org_id = self._org_id
        order_type = self._order_type
        payload = generate_payload(**locals())
        return await self.request(api.Methods.BRANDS, payload)

    async def search_by_article(
            self, article: Union[str, int], brand: str,
            search_type: str = 'as', with_analogues: str = None):
        """
        :param article: Артикул (Разделители не учитываются)
        :param brand: Бренд
        :param search_type: 'as' - по складам auto1.by. None = Все склады
        :param with_analogues: 'true' либо None
        :return: list of dicts
        """
        org_id = self._org_id
        order_type = self._order_type
        point = self._point
        payload = generate_payload(**locals())
        return await self.request(api.Methods.SEARCH_BY_ARTICLE, payload)

    async def add_to_cart(self, store_id: Union[str, int], number: Union[str, int],
                          quantity: Union[str, int], comment: str = None):
        """
        :param store_id: StoreId из ответа поиска
        :param number: Number из ответа поиска
        :param quantity: заказываемое количество, кратно Multiplicity из ответа поиска
        :param comment: коментарий к заказу
        :return:
        """
        org_id = self._org_id
        order_type = self._order_type
        point = self._point
        payload = generate_payload(**locals())
        return await self.request(api.Methods.ADD_TO_CART, payload, True)

    async def cart_items(self):
        return await self.request(api.Methods.CART_ITEMS)

    async def get_routes(self):
        point = self._point
        payload = generate_payload(**locals())
        return await self.request(api.Methods.GET_ROUTES)

    async def send_order(self, route: str):
        point = self._point
        payload = generate_payload(**locals())
        return await self.request(api.Methods.SEND_ORDER, payload, True)

    async def clear_cart(self):
        return await self.request(api.Methods.CLEAR_CART, post=True)

    async def orders_history(self, start: str = None, end: str = None, search_pattern: str = None):
        org_id = self._org_id
        payload = generate_payload(**locals())
        return await self.request(api.Methods.ORDERS_HISTORY, payload)
