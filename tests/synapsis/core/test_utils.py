import pytest

from synapsis.core import Utils


def test_find():
    with pytest.raises(TypeError, match='object is not iterable'):
        Utils.find(None)
    with pytest.raises(AttributeError, match="object has no attribute 'ID'"):
        assert Utils.find([{}], key='ID', value=3)

    assert Utils.find([]) is None
    assert Utils.find([None]) is None
    assert Utils.find([0]) is None
    assert Utils.find(['']) is None
    assert Utils.find('') is None

    assert Utils.find([], default='nope') == 'nope'
    assert Utils.find([None], default='nope') == 'nope'
    assert Utils.find([1], default='nope') == 1

    iterable = [0, 1, 2, 3]
    assert Utils.find(iterable) == 1
    assert Utils.find(iterable, value=2) == 2
    assert Utils.find(iterable, func=lambda i: i == 2) == 2
    assert Utils.find(iterable, lambda i: i == 2, default='nope') == 2
    assert Utils.find(iterable, lambda i: i == 4, default='nope') == 'nope'

    assert Utils.find([{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3}]) == {'id': 0}
    assert Utils.find([{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3}], lambda i: i['id'] == 3) == {'id': 3}

    assert Utils.find([{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3}], key='id', value=2) == {'id': 2}
    assert Utils.find([{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3}], func=lambda i: i == 2, key='id') == {'id': 2}
    assert Utils.find([{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3}], lambda i: i == 2, key='id') == {'id': 2}
    assert Utils.find([{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3}], default='nope', key='id', value=4) == 'nope'


def test_select():
    with pytest.raises(TypeError, match='object is not iterable'):
        Utils.select(None)
    with pytest.raises(AttributeError, match="object has no attribute 'ID'"):
        assert Utils.select([{}], key='ID', value=3)

    assert Utils.select([]) == []
    assert Utils.select([None]) == []
    assert Utils.select([0]) == []
    assert Utils.select(['']) == []
    assert Utils.select('') == []

    iterable = [0, 1, 2, 3]
    assert Utils.select(iterable) == [1, 2, 3]
    assert Utils.select(iterable, lambda i: i == 2) == [2]
    assert Utils.select(iterable, value=2) == [2]
    assert Utils.select(iterable, func=lambda i: i + 1, value=4) == [3]
    assert Utils.select(iterable, lambda i: i + 1, value=4) == [3]
    assert Utils.select(iterable, lambda i: i == 4) == []

    iterable = [{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3}]
    assert Utils.select(iterable) == iterable
    assert Utils.select(iterable, func=lambda i: i['id'] == 3) == [{'id': 3}]
    assert Utils.select(iterable, lambda i: i['id'] == 3) == [{'id': 3}]
    assert Utils.select(iterable, key='id', value=2) == [{'id': 2}]
    assert Utils.select(iterable, func=lambda i: i + 1, key='id', value=4) == [{'id': 3}]
    assert Utils.select(iterable, func=lambda i: i == 3, key='id') == [{'id': 3}]
    assert Utils.select(iterable, func=lambda i: i['id'], value=2) == [{'id': 2}]


def test_first():
    with pytest.raises(TypeError, match='object is not iterable'):
        Utils.first(None)
    with pytest.raises(AttributeError, match="object has no attribute 'ID'"):
        assert Utils.first([{}], key='ID', value=3)

    assert Utils.first([]) is None
    assert Utils.first([None]) is None
    assert Utils.first([0]) == 0
    assert Utils.first(['']) == ''
    assert Utils.first('') is None

    assert Utils.first([], default='nope') == 'nope'
    assert Utils.first([None], default='nope') is None
    assert Utils.first([1], default='nope') == 1

    iterable = [0, 1, 2, 3]
    assert Utils.first(iterable) == 0
    assert Utils.first(iterable, lambda i: i == 2) == 2
    assert Utils.first(iterable, lambda i: i == 2, default='nope') == 2
    assert Utils.first(iterable, lambda i: i == 4, default='nope') == 'nope'

    iterable = [{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3}]
    assert Utils.first(iterable) == {'id': 0}
    assert Utils.first(iterable, lambda i: i['id'] == 3) == {'id': 3}

    assert Utils.first(iterable, key='id', value=2) == {'id': 2}
    assert Utils.first(iterable, func=lambda i: i + 1, key='id', value=4) == {'id': 3}
    assert Utils.first(iterable, func=lambda i: i == 3, key='id') == {'id': 3}
    assert Utils.first(iterable, func=lambda i: i['id'], value=2) == {'id': 2}
    assert Utils.first(iterable, default='nope', key='id', value=4) == 'nope'


def test_last():
    with pytest.raises(TypeError, match='object is not iterable'):
        Utils.last(None)
    with pytest.raises(AttributeError, match="object has no attribute 'ID'"):
        assert Utils.last([{}], key='ID', value=3)

    assert Utils.last([]) is None
    assert Utils.last([None]) is None
    assert Utils.last([0]) == 0
    assert Utils.last(['']) == ''
    assert Utils.last('') is None

    assert Utils.last([], default='nope') == 'nope'
    assert Utils.last([None], default='nope') is None
    assert Utils.last([1], default='nope') == 1

    iterable = [0, 1, 2, 3]
    assert Utils.last(iterable) == 3
    assert Utils.last(iterable, lambda i: i == 2) == 2
    assert Utils.last(iterable, lambda i: i == 2, default='nope') == 2
    assert Utils.last(iterable, lambda i: i == 4, default='nope') == 'nope'

    iterable = [{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3}]
    assert Utils.last(iterable) == {'id': 3}
    assert Utils.last(iterable, lambda i: i['id'] == 3) == {'id': 3}

    assert Utils.last(iterable, key='id', value=2) == {'id': 2}
    assert Utils.last(iterable, func=lambda i: i + 1, key='id', value=4) == {'id': 3}
    assert Utils.last(iterable, func=lambda i: i == 3, key='id') == {'id': 3}
    assert Utils.last(iterable, func=lambda i: i['id'], value=2) == {'id': 2}
    assert Utils.last(iterable, default='nope', key='id', value=4) == 'nope'


def test_map():
    with pytest.raises(TypeError, match='is not iterable'):
        Utils.map(None)
    with pytest.raises(AttributeError, match="object has no attribute 'ID'"):
        assert Utils.map([{}], key='ID')

    assert Utils.map([], func=lambda i: i) == []

    iterable = [0, 1, 2, 3]
    iterable2 = [0, 5, 6, 7]
    assert Utils.map(iterable, func=lambda i: i * 2) == [0, 2, 4, 6]
    assert Utils.map(iterable, lambda i: i * 2) == [0, 2, 4, 6]

    assert Utils.map(iterable, iterable2, func=lambda a, b: a * b) == [0, 5, 12, 21]
    assert Utils.map(iterable, iterable2, lambda a, b: a * b) == [0, 5, 12, 21]

    iterable = [{'id': 1}, {'id': 2}, {'id': 3}]
    assert Utils.map(iterable, key='id') == [1, 2, 3]
    assert Utils.map(iterable, func=lambda i: i * 2, key='id') == [2, 4, 6]
    assert Utils.map(iterable, lambda i: i * 2, key='id', ) == [2, 4, 6]


def test_unique():
    with pytest.raises(TypeError, match='object is not iterable'):
        Utils.unique(None)
    with pytest.raises(AttributeError, match="object has no attribute 'ID'"):
        assert Utils.unique([{}], key='ID')

    assert Utils.unique([]) == []

    iterable = [0, 1, 2, 3]
    assert Utils.unique(iterable) == iterable
    assert Utils.unique(iterable + iterable) == iterable
    assert Utils.unique([0, 0, 0]) == [0]

    iterable = [{'id': 1}, {'id': 2}, {'id': 3}]
    assert Utils.unique(iterable, func=lambda i: i['id']) == iterable
    assert Utils.unique(iterable, lambda i: i['id']) == iterable
    assert Utils.unique(iterable, key='id') == iterable
    assert Utils.unique(iterable, func=lambda i: 1 if i <= 2 else 9, key='id') == [{'id': 1}, {'id': 3}]
    assert Utils.unique(iterable, lambda i: 1 if i <= 2 else 9, key='id') == [{'id': 1}, {'id': 3}]

    iterable = [{'id': 1}, {'id': 1}, {'id': 1}]
    assert Utils.unique(iterable, key='id') == [iterable[0]]
