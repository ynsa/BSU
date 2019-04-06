class Advert(object):
    def init(self, gen):
        self.prob = round(gen.uniform(0.1, 1), 1)
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

    # if type(winners[0]) == DeviantAdvert and winners[0].get_bid_func:
    #     print(f'\tWinner: {winners[0]}\tdeviant winner combination: {winners[0].prob * winners[0].get_bid(ads)}')

    gold_positions = sum(map(lambda x: x[0].get_bid(ads) * x[1] * x[0].prob, zip(winners, position_prob)))
    # if n == 2:
        # costs[0] = winners[2].get_bid(ads) * winners[2].prob / winners[0].prob
        # costs[1] = winners[2].get_bid(ads) * winners[2].prob / winners[1].prob
        # costs[0] = (position_prob[0] * winners[1].get_bid(ads) + position_prob[1] * winners[2].get_bid(ads) - position_prob[1] * winners[1].get_bid(ads)) / position_prob[0]
        # costs[1] = winners[2].get_bid(ads)
    # elif n == 3:
    #     costs[0] = winners[3].get_bid(ads) * winners[3].prob / winners[0].prob
    #     costs[1] = winners[3].get_bid(ads) * winners[3].prob / winners[1].prob
    #     costs[2] = winners[3].get_bid(ads) * winners[3].prob / winners[2].prob
        # costs[0] = (position_prob[0] * winners[1].get_bid(ads) + position_prob[1] * winners[2].get_bid(ads) + position_prob[2] * winners[3].get_bid(ads)
        #             - position_prob[1] * winners[1].get_bid(ads) - position_prob[2] * winners[2].get_bid(ads)) / position_prob[0]
        # costs[1] = (position_prob[1] * winners[2].get_bid(ads) + position_prob[1] * winners[3].get_bid(ads) - position_prob[2] * winners[2].get_bid(ads)) / position_prob[1]
        # costs[2] = winners[3].get_bid(ads)

    # elif n == 3:
    # for i, winner in enumerate(winners[:-1]):
    #     unreal_winners = winners.copy()
    #     unreal_winners.pop(i)
    #     m = sum(map(lambda x: x[0].get_bid(ads) * x[1], zip(unreal_winners, position_prob)))
    #     costs[i] = (m - (gold_positions - position_prob[i] * winner.get_bid(ads))) / position_prob[i]
    #     # print(costs[i])

    # else:
    #     # print(f'n = {n}')
    #     # costs[0] = winners[1].get_bid(ads)
    for i, winner in enumerate(winners[:-1]):
        print(f'\tWinner: {winner}\tget_bid: {winner.get_bid(ads)}\n\tdeviant winner combination: {winner.prob * winner.get_bid(ads)}')
        unreal_winners = winners.copy()
        unreal_winners.pop(i)
        m = sum(map(lambda x: x[0].get_bid(ads) * x[1] * x[0].prob, zip(unreal_winners, position_prob)))
        costs[i] = (m - (gold_positions - position_prob[i] * winner.get_bid(ads) * winner.prob)) / position_prob[i]
        # if type(winner) == DeviantAdvert:
        #     print(f'\tdeviant winner combination: {winner.prob * winner.get_bid(ads)}')
            # print(costs[i])
    del winners[-1]
    return winners, costs
