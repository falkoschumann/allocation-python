import json

import pytest
from tenacity import Retrying, stop_after_delay

from . import api_client, redis_client
from ..random_refs import random_batchref, random_orderid, random_sku


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
@pytest.mark.usefixtures("restart_redis_pubsub")
def test_change_quantity_leading_to_reallocation():
    # Beginne mit zwei Batches und einem zugeteilten Auftrag.
    orderid, sku = random_orderid(), random_sku()
    earlier_batch = random_batchref('old')
    later_batch = random_batchref('newer')
    api_client.post_to_add_batch(earlier_batch, sku, qty=10, eta='2011-01-01')
    api_client.post_to_add_batch(later_batch, sku, qty=10, eta='2011-01-01')
    response = api_client.post_to_allocate(orderid, sku, 10)
    assert response.json()['batchref'] == earlier_batch

    subscription = redis_client.subscribe_to('line_allocated')

    # Anzahl beim zugeteilten Batch so ändern, dass weniger als für unseren
    # Auftrag da ist
    redis_client.publish_message(
        'change_batch_quantity', {'batchref': earlier_batch, 'qty': 5}
    )

    # Warten, bis wir eine Nachricht mit der bestätigten Neuzuteilung erhalten
    messages = []
    for attempt in Retrying(stop=stop_after_delay(3), reraise=True):
        with attempt:
            message = subscription.get_message(timeout=1)
            if message:
                messages.append(message)
                print(message)
            data = json.loads(messages[-1]['data'])
            assert data['orderid'] == orderid
            assert data['batchref'] == later_batch
