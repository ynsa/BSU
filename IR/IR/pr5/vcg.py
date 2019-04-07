class Advert(object):
    def init(self, gen):
        self.prob = gen.random()
        self._value = gen.randint(1, 10) * 9 + 1
        return self

    def __repr__(self):
        return 'Prob: %0.3f, Value: %0.3f' % (
            self.prob, self._value
        )

    def get_bid(self, ads):
        return self._value


class DeviantAdvert(Advert):
    def __init__(self, get_bid_func):
        self.get_bid_func = get_bid_func

    def get_bid(self, ads):
        if self.get_bid_func is not None:
            bid = self.get_bid_func(self, ads)
            assert bid >= 0.0
            return bid
        return Advert.get_bid(self, ads)


def auction_first_price(ads, position_prob):
    n = len(position_prob)
    winners = sorted(ads, key=lambda ad: ad.prob * ad.get_bid(ads), reverse=True)[:n]
    costs = [ad.get_bid(ads) for ad in winners]
    return winners, costs


def auction_next_price(ads, position_prob):
    n = len(position_prob)
    winners = sorted(ads, key=lambda ad: ad.prob * ad.get_bid(ads), reverse=True)[:n + 1]
    costs = [winners[i + 1].get_bid(ads) for i in range(len(winners) - 1)]
    del winners[-1]
    return winners, costs


def auction_vcg(ads, position_prob):
    n = len(position_prob)
    winners = sorted(ads, key=lambda ad: ad.prob * ad.get_bid(ads), reverse=True)[:n + 1]
    costs = [0] * n

    gold_positions = sum(map(lambda x: x[0].get_bid(ads) * x[1] * x[0].prob, zip(winners, position_prob)))
    for i, winner in enumerate(winners[:-1]):
        unreal_winners = winners.copy()
        unreal_winners.pop(i)
        m = sum(map(lambda x: x[0].get_bid(ads) * x[1] * x[0].prob, zip(unreal_winners, position_prob)))

        winner_weight = position_prob[i] * winner.prob
        costs[i] = (m - (gold_positions - winner.get_bid(ads) * winner_weight)) / winner_weight
    del winners[-1]
    return winners, costs
