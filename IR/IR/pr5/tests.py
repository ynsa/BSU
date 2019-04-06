from random import Random

from pr5.vcg import DeviantAdvert, Advert, auction_vcg, auction_first_price, \
    auction_next_price


def test_from_lecture(auc, answer):
    ads = [Advert() for i in range(3)]
    ads[0]._value = 10
    ads[1]._value = 4
    ads[2]._value = 2
    for i in range(3):
        ads[i].prob = 1

    results = auc(ads, [1.0, 0.8])
    result = results[1]

    error = max(abs(ri - ai) for ri, ai in zip(result, answer))
    if error > 1e-7:
        print(result, '!=', answer)
    else:
        print(auc.__name__, 'is fine!')
    return results


def test_deviant_strategy(auc, position_prob, deviant_advert_func=None,
                          seed=42, debug=False):
    assert position_prob == sorted(position_prob, reverse=True)

    doc_count = len(position_prob) + 1
    gen = Random(seed)
    for it in range(10000):
        print('\n', '-' * 30)
    # for it in range(3):
        # генерируем объявления
        ads = [Advert().init(gen) for i in range(doc_count - 1)]
        ads.append(DeviantAdvert(deviant_advert_func).init(gen))
        deviant = ads[-1]
        print(f'Deviant get_bid: {ads[-1].get_bid(ads)}')
        # запускаем аукцион
        print('F1')
        winners, costs = auc(ads, position_prob)
        assert len(winners) == len(position_prob), 'Something goes wrong'
        assert min(costs) > 0, 'No free lunch'

        cur_deviant_profit = 0.0
        for p, (ad, cost) in zip(position_prob, zip(winners, costs)):
            if ad == deviant:
                # матожидание профита равно вероятности клика
                # умноженной на ценность минус стоимость клика
                cur_deviant_profit = (ad._value - cost) * ad.prob * p
                print(f'get_bid for deviant = {ad.get_bid(ads)}')
                break

        if deviant_advert_func is not None:
            # разыгрываем аукцион как будто девиант ведет себя честно
            deviant.get_bid_func = None
            print('F2')
            winners_bl, costs_bl = auc(ads, position_prob)

            honest_deviant_profit = 0.0
            for p, (ad, cost) in zip(position_prob, zip(winners_bl, costs_bl)):
                if ad == deviant:
                    honest_deviant_profit = (ad._value - cost) * ad.prob * p
                    print(f'cur_deviant_profit = {cur_deviant_profit}\thonest_deviant_profit = {honest_deviant_profit}')
                    break

            # если честный профит меньше нечестного - фейлим тест
            if cur_deviant_profit > honest_deviant_profit:
                print(f'{cur_deviant_profit - honest_deviant_profit}')
                if debug:
                    print('Fail')
                    print(f'n = {len(position_prob)}')
                    print(f'position_prob: {", ".join([str(x) for x in position_prob])}')
                    print('Deviant auction results:')
                    for i, ad in enumerate(ads):
                        try:
                            idx = winners.index(ad)
                            print(f'Ad {i}:', ad, 'Win:', idx, 'Bid:',
                                  ad.get_bid(ads), 'Cost:',
                                  costs[idx])
                        except:
                            print(f'Ad {i}:', ad)
                    print()
                    print('Honest auction results:')
                    for i, ad in enumerate(ads):
                        try:
                            idx = winners_bl.index(ad)
                            print(f'Ad {i}:', ad, 'Win:', idx, 'Bid:',
                                  ad.get_bid(ads), 'Cost:', costs[idx])
                        except:
                            print(f'Ad {i}:', ad)
                    print()
                    print()

                return False, cur_deviant_profit - honest_deviant_profit

    return True, 0.0


def create_eps_strategy(eps):
    def minus_eps_bid(self, ads):
        return max(self._value - eps, 1e-5)
    return minus_eps_bid


def create_eps_pos_strategy(pos_delta, eps):
    def minus_eps_pos_bid(self, ads):
        winners = sorted(ads, key=lambda ad: ad.prob * ad._value, reverse=True)
        idx = winners.index(self)
        idx = max(0, min(idx + pos_delta, len(ads) - 1))
        return max(winners[idx]._value * winners[idx].prob / self.prob + eps, 1e-5)
    return minus_eps_pos_bid

def my_str():
    def nyam(self, ads):
        return 5
    return nyam


STRATEGIES = [
    create_eps_strategy(+0.5),
    create_eps_strategy(-0.5),
    create_eps_strategy(+2),
    create_eps_strategy(-2),
    create_eps_pos_strategy(+1, +1e-5),
    create_eps_pos_strategy(-1, +1e-5),
    create_eps_pos_strategy(+1, -1e-5),
    create_eps_pos_strategy(-1, -1e-5),
    create_eps_pos_strategy(+5, +1e-5),
    create_eps_pos_strategy(-5, +1e-5),
    create_eps_pos_strategy(+5, -1e-5),
    create_eps_pos_strategy(-5, -1e-5),
    my_str()
]


def test_deviant_strategies(aucs):
    # пример вероятностей клика по позиции
    # можно менять на своё усмотрение
    # position_prob = [0.9, 0.7, 0.5, 0.4]
    position_prob = [1, 0.8]
    for auc in aucs:
        for si, strategy in enumerate(STRATEGIES):
            for n in range(1, len(position_prob) + 1):
                ok, profit = test_deviant_strategy(auc, position_prob[:n], deviant_advert_func=strategy, debug=True)
                if not ok:
                    auc_name = auc.__name__
                    strategy_name = strategy.__name__
                    print('Auction `%s` is cheated with strategy `%d: %s` with profit %s' % (auc_name, si, strategy_name, profit))
    print('Done')


def my_test(auc, answer):
    # winners_bl, costs_bl = test_from_lecture(auc, answer)

    ads = [Advert() for i in range(3)]
    ads[0]._value = 10
    ads[1]._value = 4
    ads[2]._value = 2
    for i in range(3):
        ads[i].prob = 1

    position_prob = [1.0, 0.8]
    winners_bl, costs_bl = auc(ads, position_prob)

    for p, (ad, cost) in zip(position_prob, zip(winners_bl, costs_bl)):
        if ad._value == ads[2]._value:
            honest_deviant_profit = (ad._value - cost) * ad.prob * p
            print(f'Honest: {honest_deviant_profit}')
            break

    # for si, strategy in enumerate(STRATEGIES):
    # ads = [Advert() for i in range(3)]
    ads[0]._value = 10
    ads[1]._value = 4
    ads[2] = DeviantAdvert(STRATEGIES[-1])
    ads[2]._value = 2
    for i in range(3):
        ads[i].prob = 1


    # result = auc(ads, [1.0, 0.8])[1]
    winners_bl, costs_bl = auc(ads, position_prob)

    honest_deviant_profit = 0.0
    for p, (ad, cost) in zip(position_prob, zip(winners_bl, costs_bl)):
        if ad._value == ads[2]._value:
            honest_deviant_profit = (ad._value - cost) * ad.prob * p
            print(f'Not honest: {honest_deviant_profit}')
            break

        # if result[1] < honest_res[1]:
        #     print(result[1], '<', honest_res[1])
        # error = max(abs(ri - ai) for ri, ai in zip(result, answer))
        # if error > 1e-7:
        #     print(result, '!=', answer)
        # else:
        #     print(auc.__name__, 'is fine!')


if __name__ == '__main__':
    # my_test(auction_vcg, [2.4, 2.0])
    # test_from_lecture
    # test_from_lecture(auction_first_price, [10, 4])
    # test_from_lecture(auction_next_price, [4, 2])
    # test_from_lecture(auction_vcg, [2.4, 2.0])

    # test_deviant_strategies
    # test_deviant_strategies([auction_first_price, auction_next_price])
    test_deviant_strategies([auction_vcg])