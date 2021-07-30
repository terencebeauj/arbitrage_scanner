# arbitrage_scanner

![Triangular-Arbitrage](https://user-images.githubusercontent.com/69433462/127597332-e5643ea7-276e-49ac-8b94-b7d8fea920b5.png)

This bot is a scanner for triangular arbitrage patterns, for the binance exchange.
All the combinations are made by the bot, and it continuously performs the calculations on all the pair to detect arbitrages.
When arbitrages are detected, they are recorded in a log with the triangle name, the gain and the type of arbitrage: long or short.
The infos.csv file is an exemple of what the log looks like.

You should at least, use the method presented here to deal with your keys: export them in the .env file, and then put this file into the .gitignore. Because it is of great importance that only you can access your private key, otherwise your funds could be stolen anytime.
