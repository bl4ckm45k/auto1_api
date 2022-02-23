import aiohttp
import logging
from .exceptions import NetworkError, APIError, TeaPot, CartException
from http import HTTPStatus

logger = logging.getLogger('api-auto1.by')


def check_result(method_name: str, content_type: str, status_code: int, body):
    """
    Checks whether `result` is a valid API response.
    A result is considered invalid if:
    - The server returned an HTTP response code other than 200
    - The content of the result is invalid JSON.
    - The method call was unsuccessful (The JSON 'ok' field equals False)

    :param method_name: The name of the method called
    :param status_code: status code
    :param content_type: content type of result
    :param body: result body
    :return: The result parsed to a JSON dictionary
    :raises ApiException: if one of the above listed cases is applicable
    """
    logger.debug('Response for %s: [%d] "%r"', method_name, status_code, body)

    if content_type != 'application/json' and method_name != 'AddToCart':
        raise NetworkError(f"Invalid response with content type {content_type}: \"{body}\"")

    # TODO Нормальное описание ошибок
    if HTTPStatus.OK <= status_code <= HTTPStatus.IM_USED:
        if method_name == 'AddToCart':
            return {'method': 'AddToCart',
                    'status': 'ok'}
        else:
            return body
    elif status_code == HTTPStatus.BAD_REQUEST:
        if method_name == 'AddToCart':
            raise CartException(f"{body}")
        else:
            raise APIError(f"{body} [{status_code}]")
    elif status_code == HTTPStatus.NOT_FOUND:
        raise APIError(f"{body} [{status_code}]")
    elif status_code == HTTPStatus.CONFLICT:
        raise APIError(f"{body} [{status_code}]")
    elif status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
        raise APIError(f"{body} [{status_code}]")
    elif status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
        raise APIError(f"{body} [{status_code}]")
    elif status_code == HTTPStatus.IM_A_TEAPOT:
        raise TeaPot('Кто-то пытается сварить кофе в чайнике')

    raise APIError(f"{body} [{status_code}]")


async def make_request(session, login, password, method, data=None, post: bool = False, **kwargs):
    logger.debug('Make request: "%s" with data: "%r"', method, data)
    url = f'https://auto1.by/WebApi/{method}?login={login}&password={password}'
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Accept': 'application/json',
               'User-Agent': 'auto1_api'}

    try:
        if post:
            async with session.post(url, params=data, headers=headers, **kwargs) as response:
                try:
                    body = await response.json()
                except:
                    body = response.text
                return check_result(method, response.content_type, response.status, body)
        else:
            async with session.get(url, params=data, headers=headers, **kwargs) as response:
                try:
                    body = await response.json()
                except:
                    body = response.text
                return check_result(method, response.content_type, response.status, body)
    except aiohttp.ClientError as e:
        raise NetworkError(f"aiohttp client throws an error: {e.__class__.__name__}: {e}")


class Methods:
    # Orders
    PARAMS = 'GetRequestParameters'  # Параметры запросов
    SEARCH = 'Search'  # Поиск товаров
    BRANDS = 'GetBrands'  # Получение списка брендов по артикулу
    SEARCH_BY_ARTICLE = 'SearchByArticle'  # Поиск товаров по артикулу и бренду
    ADD_TO_CART = 'AddToCart'  # Добавление товара в корзину
    CART_ITEMS = 'GetCartItems'  # Список товаров в корзине
    GET_ROUTES = 'GetRoutes'  # Получение рейсов для доставки
    SEND_ORDER = 'SendOrder'  # Отправка корзины
    CLEAR_CART = 'ClearCart'  # Очистка корщины
    ORDERS_HISTORY = 'GetHistory'  # История заказов
