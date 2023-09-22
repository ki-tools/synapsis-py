from synapsis.core import Utils


def test_find():
    assert Utils.find([]) is None
    assert Utils.find([0]) is None
    assert Utils.find(['']) is None
    assert Utils.find([None]) is None
    assert Utils.find([], None) is None
    assert Utils.find([], 'missing') == 'missing'

    iterable = [0, 1, 2, 3]
    assert Utils.find(iterable) == 1
    assert Utils.find(iterable, lambda i: i == 2) == 2

    iterable = ['', '1', '2', '3']
    assert Utils.find(iterable) == '1'
    assert Utils.find(iterable, lambda i: i == '2') == '2'

    iterable = [{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3}]
    assert Utils.find(iterable) == iterable[0]
    assert Utils.find(iterable, lambda i: i['id'] == 2) == iterable[2]


def test_map():
    iterable = [0, 1, 2, 3]
    iterable2 = [0, 5, 6, 7]
    assert Utils.map(iterable, lambda i: i * 2) == [0, 2, 4, 6]
    assert Utils.map(iterable, iterable2, lambda a, b: a * b) == [0, 5, 12, 21]


def test_first():
    assert Utils.first([]) is None
    assert Utils.first([0]) == 0
    assert Utils.first(['']) == ''
    assert Utils.first([None]) is None
    assert Utils.first([], None) is None
    assert Utils.first([], 'missing') == 'missing'

    iterable = [0, 1, 2, 3]
    assert Utils.first(iterable) == 0
    assert Utils.first(iterable, lambda i: i == 2) == 2

    iterable = ['', '1', '2', '3']
    assert Utils.first(iterable) == ''
    assert Utils.first(iterable, lambda i: i == '2') == '2'

    iterable = [{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3}]
    assert Utils.first(iterable) == iterable[0]
    assert Utils.first(iterable, lambda i: i['id'] == 2) == iterable[2]


def test_last():
    assert Utils.last([]) is None
    assert Utils.last([0]) == 0
    assert Utils.last(['']) == ''
    assert Utils.last([None]) is None
    assert Utils.last([], None) is None
    assert Utils.last([], 'missing') == 'missing'

    iterable = [0, 1, 2, 3]
    assert Utils.last(iterable) == 3
    assert Utils.last(iterable, lambda i: i == 2) == 2

    iterable = ['', '1', '2', '3']
    assert Utils.last(iterable) == '3'
    assert Utils.last(iterable, lambda i: i == '2') == '2'

    iterable = [{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3}]
    assert Utils.last(iterable) == iterable[3]
    assert Utils.last(iterable, lambda i: i['id'] == 2) == iterable[2]
