import os
import shrimpy
from datetime import datetime
from arbitrage import *


def main():
    shrimpy_public_key = os.environ.get("PUBLIC_KEY")
    shrimpy_secret_key = os.environ.get("PRIVATE_KEY")
    shrimpy_client = shrimpy.ShrimpyApiClient(shrimpy_public_key, shrimpy_secret_key)

    # Works well on binance but have bugs on some other exchanges
    exchange = "binance"

    sentence = "\n----------------------- \n-----------------------\n {} on {}\n----------------------- \n-----------------------"
    date = str(datetime.now())
    sentence = sentence.format(date, exchange)

    with open("infos.csv", "a") as file:
        file.write(sentence)

    triangle_creation = Triangle()
    triangles = triangle_creation.form_triangles(exchange,
                                                 shrimpy_public_key,
                                                 shrimpy_secret_key,
                                                 shrimpy_client)

    array_of_symbols1 = triangles[0]["symbol"]
    array_of_symbols1_base = triangles[0]["base"]
    array_of_symbols1_quote = triangles[0]["quote"]

    array_of_symbols2 = triangles[1]["symbol"]
    array_of_symbols2_base = triangles[1]["base"]
    array_of_symbols2_quote = triangles[1]["quote"]

    array_of_symbols3 = triangles[2]["symbol"]
    array_of_symbols3_base = triangles[2]["base"]
    array_of_symbols3_quote = triangles[2]["quote"]

    # Release memory
    del sentence
    del date
    del triangle_creation
    del triangles

    def Arbitrage():
        if (len(array_of_symbols1) == len(array_of_symbols1_base) == len(array_of_symbols1_quote) ==
                len(array_of_symbols2) == len(array_of_symbols2_base) == len(array_of_symbols2_quote) ==
                len(array_of_symbols3) == len(array_of_symbols3_base) == len(array_of_symbols3_quote)):

            while True:

                for i in range(len(array_of_symbols1) - 1):
                    triangle = Triangle()

                    try:
                        triangle.set_fees(shrimpy_public_key, shrimpy_secret_key, shrimpy_client, exchange)

                    except:
                        print("Can't access the fees")
                        continue

                    triangle.symbol1 = Symbol(array_of_symbols1[i], array_of_symbols1_base[i],
                                              array_of_symbols1_quote[i])
                    triangle.symbol2 = Symbol(array_of_symbols2[i], array_of_symbols2_base[i],
                                              array_of_symbols2_quote[i])
                    triangle.symbol3 = Symbol(array_of_symbols3[i], array_of_symbols3_base[i],
                                              array_of_symbols3_quote[i])

                    try:
                        triangle.order_triangle()

                        triangle.symbol1.calc_bid_and_ask(shrimpy_public_key, shrimpy_secret_key, shrimpy_client,
                                                          exchange)
                        triangle.symbol2.calc_bid_and_ask(shrimpy_public_key, shrimpy_secret_key, shrimpy_client,
                                                          exchange)
                        triangle.symbol3.calc_bid_and_ask(shrimpy_public_key, shrimpy_secret_key, shrimpy_client,
                                                          exchange)

                    except:
                        continue

                    triangle.calculate_delta_long()
                    triangle.calculate_delta_short()

                    if triangle.PLBuy > triangle.fees:
                        try:
                            gain_net = str(round(triangle.PLBuy - triangle.fees, 2))
                            triangle.save_triangle("infos.csv", gain_net, "long")

                        except:
                            print("Error")

                        print(
                            f"Long arbitrage opportunity in triangle: {triangle.symbol1.name} = {triangle.symbol2.name} * {triangle.symbol3.name}")
                        print(f"Gain net : {gain_net} percent")

                    elif triangle.PLSell > triangle.fees:
                        try:
                            gain_net = str(round(triangle.PLSell - triangle.fees, 2))
                            triangle.save_triangle("infos.csv", gain_net, "short")

                        except:
                            print("Error")

                        print(
                            f"Short arbitrage opportunity in triangle: {triangle.symbol1.name} = {triangle.symbol2.name} * {triangle.symbol3.name}")
                        print(f"Gain net : {gain_net} percent")
                    else:
                        print(
                            f"No arbitrage opportunity in triangle: {triangle.symbol1.name} {triangle.symbol2.name} {triangle.symbol3.name}")

    Arbitrage()


if __name__ == '__main__':
    main()
