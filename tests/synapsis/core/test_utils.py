from synapsis.core import utils


def test_find():
    assert utils.find([]) is None
    assert utils.find([0]) is None
    assert utils.find(['']) is None
    assert utils.find([None]) is None
    assert utils.find([], None) is None
    assert utils.find([], 'missing') == 'missing'

    iterable = [0, 1, 2, 3]
    assert utils.find(iterable) == 1
    assert utils.find(iterable, lambda i: i == 2) == 2

    iterable = ['', '1', '2', '3']
    assert utils.find(iterable) == '1'
    assert utils.find(iterable, lambda i: i == '2') == '2'

    iterable = [{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3}]
    assert utils.find(iterable) == iterable[0]
    assert utils.find(iterable, lambda i: i['id'] == 2) == iterable[2]


def test_map():
    iterable = [0, 1, 2, 3]
    iterable2 = [0, 5, 6, 7]
    assert utils.map(iterable, lambda i: i * 2) == [0, 2, 4, 6]
    assert utils.map(iterable, iterable2, lambda a, b: a * b) == [0, 5, 12, 21]


def test_first():
    assert utils.first([]) is None
    assert utils.first([0]) == 0
    assert utils.first(['']) == ''
    assert utils.first([None]) is None
    assert utils.first([], None) is None
    assert utils.first([], 'missing') == 'missing'

    iterable = [0, 1, 2, 3]
    assert utils.first(iterable) == 0
    assert utils.first(iterable, lambda i: i == 2) == 2

    iterable = ['', '1', '2', '3']
    assert utils.first(iterable) == ''
    assert utils.first(iterable, lambda i: i == '2') == '2'

    iterable = [{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3}]
    assert utils.first(iterable) == iterable[0]
    assert utils.first(iterable, lambda i: i['id'] == 2) == iterable[2]


def test_last():
    assert utils.last([]) is None
    assert utils.last([0]) == 0
    assert utils.last(['']) == ''
    assert utils.last([None]) is None
    assert utils.last([], None) is None
    assert utils.last([], 'missing') == 'missing'

    iterable = [0, 1, 2, 3]
    assert utils.last(iterable) == 3
    assert utils.last(iterable, lambda i: i == 2) == 2

    iterable = ['', '1', '2', '3']
    assert utils.last(iterable) == '3'
    assert utils.last(iterable, lambda i: i == '2') == '2'

    iterable = [{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3}]
    assert utils.last(iterable) == iterable[3]
    assert utils.last(iterable, lambda i: i['id'] == 2) == iterable[2]
