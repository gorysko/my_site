title: Monads
date: 2013-09-18
type: post

`import operator`


class Functor(object):

    def fmap(self, func):
        raise NotImplementedError()


class Applicative(Functor):

    def applicate(self, monad_value):
        raise NotImplementedError()


class Monad(Applicative):

    def bind(self, monad_func):
        raise NotImplementedError()

    def then(self, monad_func):
        raise NotImplementedError()

    @property
    def result(self):
        raise NotImplementedError()

#------------------------------------------------------------------
class Maybe(Monad):

    @classmethod
    def just(cls, x):
        return cls(just=x)

    @classmethod
    def nothing(cls):
        return cls(nothing=True)

    @classmethod
    def _from_monad_value(cls, monad_value):
        assert isinstance(monad_value, Maybe)
        nothing, just = monad_value.result
        if nothing:
            return cls.nothing()
        return cls.just(just)


    def __init__(self, just=None, nothing=False):
        super(Maybe, self).__init__()
        self._just = just
        self._nothing = nothing


    def fmap(self, func):
        if self._nothing:
            return self.__class__(nothing=True)
        return self.__class__(just=func(self._just))


    def applicate(self, monad_value):
        if self._nothing:
            return self.nothing()
        nothing, val = monad_value.result
        if nothing:
            return self.nothing()
        return self.just(self._just(val))


    def bind(self, monad_func):
        if self._nothing:
            return self.nothing()
        return self._from_monad_value(
            monad_func(self._just))


    def then(self, monad_func):
        return self._from_monad_value(monad_func())


    def __repr__(self):
        if self._nothing:
            val = 'nothing = True'
        else:
            val = 'just = %s' % repr(self._just)
        return 'Maybe(%s)' % val


    @property
    def result(self):
        return (self._nothing, self._just)


just = lambda x: Maybe.just(x)
nothing = lambda: Maybe.nothing()

liftMaybe = lambda fn: lambda x: just(fn(x))

#------------------------------------------------------------------

class List(list, Monad):

    @classmethod
    def _from_lol(cls, list_of_lists):
        return cls(reduce(operator.add, list_of_lists, []))

    def fmap(self, func):
        return self.__class__(map(func, self))

    def applicate(self, monad_value):
        return self._from_lol(
            map(lambda fn: map(fn, monad_value), self)
        )

    def bind(self, monad_func):
        return self._from_lol(map(monad_func, self))

    def then(self, monad_func):
        return self.__class__(monad_func())

    def __repr__(self):
        return 'List(%s)' % list.__repr__(self)

    @property
    def result(self):
        return self

liftList = lambda fn: lambda x: List(fn(x))

#------------------------------------------------------------------
if __name__ == '__main__':
    def showMaybe(maybe):
        print maybe

    # ==== Maybe as functor ====
    showMaybe(
        just(-3).fmap(abs)
    )

    # ==== Maybe as applicative functor ====
    add = lambda x: lambda y: x+y
    print nothing(  ).applicate( just(1)   ).applicate( just(2)   )
    print just( add ).applicate( nothing() ).applicate( just(2)   )
    print just( add ).applicate( just(1)   ).applicate( nothing() )
    print just( add ).applicate( just(1)   ).applicate( just(2)   )

    # ==== Maybe as monad ====
    maybe_div = lambda x: nothing() if x == 0 else just(100 // x)
    print just(4).bind(
        maybe_div
    ).bind(
        liftMaybe(str)
    ).bind(
        liftMaybe(lambda x: x*3)
    )
    print nothing().then( lambda : just("Use force!") )

    #-------------------------------------------------------------------
    # ==== List as functor ====
    print List([1,2,3]).fmap(str).fmap(lambda x: x*2)

    # ==== List as applicative functor ====
    print List( [str, abs] ).applicate( [-100, -200] )
    print List(            ).applicate( [-100, -200] )
    print List( [str, abs] ).applicate( [] )

    print List([
        lambda x: lambda y: x + y,
        lambda x: lambda y: x * y
    ]).applicate(
        [1, 2]
    ).applicate(
        [10, 100]
    )

    # ==== List as monad ====
    # все точки, достижимые шахматным конем из указанной точки
    raw_jumps = lambda (x, y): List([
        (x + 1, y + 2),
        (x + 1, y - 2),
        (x - 1, y + 2),
        (x - 1, y - 2),
        (x + 2, y + 1),
        (x + 2, y - 1),
        (x - 2, y + 1),
        (x - 2, y - 1),
    ])
    # отбрасывание точек, выходящих за пределы доски
    if_valid = lambda (x, y): (
        List([(x, y)]) if 1 <= x <= 8 and 1 <= y <= 8 else List()
    )

    # ход конём из точки во всё возможные допустимые точки
    jump = lambda pos: List([pos]).bind( raw_jumps ).bind( if_valid )

    # проерка, можно ли достичь некоторой точки шахматной доски
    # из исходной ровно за 3 хода коня
    in3jumps = lambda pos_from, pos_to: pos_to in (
        List([pos_from]).bind( jump ).bind( jump ).bind( jump )
    )

    print in3jumps((3,3), (5,1))
    print in3jumps((3,3), (5,2))

    `