import datetime


def xnpv (values, dates, rate, base_interval):
    dt = max(dates)
    values = [float(x) for x in values]
    l = [x for x in zip(values, dates)]
    s = sum(list(map(lambda x: x[0] / ((1+rate)**( (x[1] - dt).days/base_interval)), l)))

    #for x in l:
    #    t = (x[1] - dt).days
    #    c = x[0] / ((1+rate)**( (x[1] - dt).days/365))
    #    print (c)
    #    print(t)
    #    print(x[1])
    #    print(dt)
    #    s =+ c
    return s


def xirr (values, dates, base_interval = 365 ):
    rate_min = -0.99  # минимально допустимое значение ставки
    rate_max = 1000  # максимально допустимое значение ставки
    w = 1 / (10 ** 12)  # допустимая погрешность

    rate = (rate_min + rate_max) / 2  # начальное значение ставки
    h = xnpv(values, dates, rate, base_interval)  # начальное значение доходноси

    i = 0  # итерация вычисления

    # прямая (true) или обратная (false) зависимость доходности от ставки для заданного денежного потока
    d = (rate> rate_min) and (h > xnpv(values, dates, rate_min, base_interval))

    while (abs(h) > w and (i < 100)):
        if (h > w and not d) \
                or (h < -w and d):
            rate_min = rate
        elif (h < -w and not d) \
                or (h > w and d):
            rate_max = rate
        else:
            break
        if rate == (rate_min + rate_max) / 2:
            break
        rate = (rate_min + rate_max) / 2
        h = xnpv(values, dates, rate, base_interval)
        i = i + 1
        #print ( "{i: >3} ставка; {p_x: >#024}, доходность: {h: >#024}".format(i = i, p_x = rate, h = h))
        #print("rate_min: {rate_min: >#024}, доходность: {rate_max: >#024}".format(rate_min=rate_min, rate_max = rate_max))
        """
        print(i)
        print(h)
        print(p_x)
        """
    return rate

def depr (values, dates):
    base = 0
    w = 0
    details = []
    for i, v in enumerate(values):
        base+=-1*v
        if abs(base) <= 0: break
        days = 0 if i == len(dates)-1 else (dates[i+1] - dates[i]).days
        if days > 0:
            details.append({'date1': dates[i], 'date2': dates[i+1], 'base': base, 'days': days})
        w+=base*days
        print (f'date {dates[i]} base: {base}   days    {days}')
    rate = -1*(base / w)*365
    return rate, details

def rsi(df, periods=14, ema=True):
    """
    Возвращает pd.Series с индексом относительной силы.
    """
    close_delta = df['close'].diff()
    # Делаем две серий: одну для низких закрытий и одну для высоких закрытий
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)

    if ema == True:
        # Использование экспоненциальной скользящей средней
        ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
        ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    else:
        # Использование простой скользящей средней
        ma_up = up.rolling(window=periods, adjust=False).mean()
        ma_down = down.rolling(window=periods, adjust=False).mean()

    rsi = ma_up / ma_down
    rsi = 100 - (100 / (1 + rsi))
    return rsi