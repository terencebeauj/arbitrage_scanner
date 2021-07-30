import  sys

class Symbol():
    def __init__(self, name, base, quote, volume_min=0, volume_max=0, volume_step=0,
                 ticksize=0, digits=0, digits_volume=0, slippage=0, spread=800000000,
                 price=0, bid=0, ask=0, ticket=0, mrg=0):
        """
        Constructor
        """
        self.name = name  # pair name
        self.base = base  # base name
        self.quote = quote  # quote name
        self.volume_min = volume_min  # volume min for this symbol
        self.volume_max = volume_max  # volume max for this symbol
        self.volume_step = volume_step  # volume step
        self.ticksize = ticksize  # tick size for this symbol
        self.digits = digits  # number of digits this symbol accepts
        self.digits_volume = digits_volume  # number of digits for the volume
        self.slippage = slippage  # possible slippage
        self.spread = spread  # actual spread in the symbol
        self.price = price  # pair open price in the triangle
        self.bid = bid  # actual bid
        self.ask = ask  # actual ask
        self.ticket = ticket  # actual ticket for this symbol
        self.mrg = mrg  # current margin, necessary for opening

    def calc_volume_and_tick_size(self, binance_public_key, binance_secret_key, binance_client):
        """
        Fill the attributes
        Args : public key for binance, secret key for binance et le instantiated client
        void function
        """

        try:
            infos = binance_client.get_symbol_info(self.name)

        except:
            print("Error with binance client for getting volume and tick size")
        self.volume_min = float(infos["filters"][2]["minQty"])
        self.volume_max = float(infos["filters"][2]["maxQty"])
        self.volume_step = float(infos["filters"][2]["stepSize"])
        self.ticksize = float(infos["filters"][0]["tickSize"])

    def calc_bid_and_ask(self, shrimpy_public_key, shrimpy_secret_key, client, exchange):
        """
        Get the bid and ask for this symbol
        Takes in input the public and secret keys for shrimpy and the shrimpy client
        Fill the bid and ask attributes
        """

        try:
            orderbook = client.get_orderbooks(exchange,
                                              self.base,
                                              self.quote,
                                              1)

        except:
            print(f"Error with {exchange} client")

        self.bid = float(orderbook[0]["orderBooks"][0]["orderBook"]["bids"][0]["price"])
        self.ask = float(orderbook[0]["orderBooks"][0]["orderBook"]["asks"][0]["price"])


class Triangle():
    def __init__(self, symbol1="", symbol2="", symbol3="",
                 volume_min=0, volume_max=0, magic=None, status=0,
                 pl=0, PLBuy=0, PLSell=0, spread=800000000):
        """
        Constructor
        """
        self.symbol1 = symbol1  # object symbol
        self.symbol2 = symbol2  # object symbol
        self.symbol3 = symbol3  # object symbol
        self.volume_min = volume_min  # volume min for all the triangle
        self.volume_max = volume_max  # volume max for all the triangle
        self.magic = magic  # ID of the triangle
        self.status = status  # Status of the triangle : 0 - not used, 1 - sent for opening, 2 - successfully opened, 3- sent for closing
        self.pl = pl  # Triangle profit
        self.PLBuy = PLBuy  # Potential profit when buying the triangle
        self.PLSell = PLSell  # Potential profit when selling the triangle
        self.fees = 0.0  # Total commissions

    def form_triangles(self, exchange, shrimpy_public_key, shrimpy_secret_key, shrimpy_client):
        '''
        This function builds all the possible triangles per exchanges
        Takes the public kry, secret key and shrimpy client
        return an array of dictionaries with symbol, base and quote
        '''
        # Create the client and get all the pairs in the given exchange
        try:
            pairs = shrimpy_client.get_trading_pairs(exchange)

        except:
            print("Error with client")

        # Preparation to receive datas
        bases = []
        quotes = []
        symbols = []
        symb1_triangle = []
        symb2_triangle = []
        symb3_triangle = []
        symb1_triangle_base = []
        symb1_triangle_quote = []
        symb2_triangle_base = []
        symb2_triangle_quote = []
        symb3_triangle_base = []
        symb3_triangle_quote = []

        # Get the datas
        for i, pair in enumerate(pairs):
            bases.append(pair["baseTradingSymbol"])
            quotes.append(pair["quoteTradingSymbol"])
            symbols.append(bases[i] + quotes[i])

        # Get the first pair
        for i in range(len(symbols) - 2):
            symbol1 = symbols[i]
            symb1base = bases[i]
            symb1quote = quotes[i]

            # Get the second pair
            for j in range(i + 1, len(symbols) - 1):
                symbol2 = symbols[j]
                symb2base = bases[j]
                symb2quote = quotes[j]
                if (
                        symb1base == symb2base or symb1base == symb2quote or symb1quote == symb2base or symb1quote == symb2quote):
                    pass

                # If condition dont satisfied, go to next iteration
                else:
                    continue

                # Get the third pair
                for k in range(j + 1, len(symbols)):
                    symbol3 = symbols[k]
                    symb3base = bases[k]
                    symb3quote = quotes[k]
                    if (
                            symb3base == symb1base or symb3base == symb1quote or symb3base == symb2base or symb3base == symb2quote):
                        pass
                    else:
                        continue
                    if (
                            symb3quote == symb1base or symb3quote == symb1quote or symb3quote == symb2base or symb3quote == symb2quote):
                        pass
                    else:
                        continue
                    symb1_triangle.append(symbol1)
                    symb2_triangle.append(symbol2)
                    symb3_triangle.append(symbol3)
                    symb1_triangle_base.append(symb1base)
                    symb1_triangle_quote.append(symb1quote)
                    symb2_triangle_base.append(symb2base)
                    symb2_triangle_quote.append(symb2quote)
                    symb3_triangle_base.append(symb3base)
                    symb3_triangle_quote.append(symb3quote)

        return [{"symbol": symb1_triangle,
                 "base": symb1_triangle_base,
                 "quote": symb1_triangle_quote},
                {"symbol": symb2_triangle,
                 "base": symb2_triangle_base,
                 "quote": symb2_triangle_quote},
                {"symbol": symb3_triangle,
                 "base": symb3_triangle_base,
                 "quote": symb3_triangle_quote}]

    def set_volume_min(self, volume_array):
        """
        Fill the minimum volume attribute the triangle can trade
        """
        self.volume_min = max(volume_array)

    def set_volume_max(self, volume_array):
        """
        Fill the maximum volume attribute the triangle can trade
        """
        self.volume_max = min(volume_array)

    def set_fees(self, shrimpy_public_key, shrimpy_secret_key, shrimpy_client, exchange):
        """
        Get the fees for the exchange passed as argument
        """
        exchanges = shrimpy_client.get_supported_exchanges()
        for i in range(len(exchanges) - 1):
            if exchange == exchanges[i]["exchange"]:
                self.fees = round(float(exchanges[i]["worstCaseFee"] * 100) * 3, 2)

    def order_triangle(self):
        """
        This function attributes the good positions for each symbols inside the triangle;
        When we created the triangle, the symbol were placed randomly, but they need a specific place for calculations
        """
        if self.symbol1.base != self.symbol2.base:
            if self.symbol1.base == self.symbol3.base:
                temp = self.symbol2.name
                temp_base = self.symbol2.base
                temp_quote = self.symbol2.quote
                self.symbol2.name = self.symbol3.name
                self.symbol2.base = self.symbol3.base
                self.symbol2.quote = self.symbol3.quote
                self.symbol3.name = temp
                self.symbol3.base = temp_base
                self.symbol3.quote = temp_quote

            if self.symbol2.base == self.symbol3.base:
                temp = self.symbol1.name
                temp_base = self.symbol1.base
                temp_quote = self.symbol1.quote
                self.symbol1.name = self.symbol3.name
                self.symbol1.base = self.symbol3.base
                self.symbol1.quote = self.symbol3.quote
                self.symbol3.name = temp
                self.symbol3.base = temp_base
                self.symbol3.quote = temp_quote

        if self.symbol3.base != self.symbol2.quote:
            temp = self.symbol1.name
            temp_base = self.symbol1.base
            temp_quote = self.symbol1.quote
            self.symbol1.name = self.symbol2.name
            self.symbol1.base = self.symbol2.base
            self.symbol1.quote = self.symbol2.quote
            self.symbol2.name = temp
            self.symbol2.base = temp_base
            self.symbol2.quote = temp_quote

        print(f"We use triangle {self.symbol1.name} = {self.symbol2.name} * {self.symbol3.name}")

    def calculate_delta_long(self):
        """
        Calculate the mathematical expectation of gain for long positions
        """
        if self.symbol1.ask < self.symbol2.bid * self.symbol3.bid:
            gain = round(abs((self.symbol1.ask - (self.symbol2.bid * self.symbol3.bid)) / (
                        self.symbol2.bid * self.symbol3.bid) * 100), 2)
            self.PLBuy = gain

        else:
            self.PLBuy = -sys.float_info.max

    def calculate_delta_short(self):
        """
        Calculate the mathematical expectation of gain for short positions
        """
        if self.symbol1.bid > self.symbol2.ask * self.symbol3.ask:
            gain = round(abs((self.symbol1.bid - (self.symbol2.ask * self.symbol3.ask)) / (
                        self.symbol2.ask * self.symbol3.ask) * 100), 2)
            self.PLSell = gain

        else:
            self.PLSell = -sys.float_info.max

    def save_triangle(self, path, gain, _type):
        """
        Save the triangle if there is an arbitrage opportunity (long or short)
        """
        sentence = "\nTriangle: {} {} {}, Gains : {} percent, Type: {}."
        sentence = sentence.format(self.symbol1.name, self.symbol2.name, self.symbol3.name, gain, _type)
        with open(path, "a") as file:
            file.write(sentence)

    def optimization(self):
        """
        Perform portfolio optimization
        """
        pass