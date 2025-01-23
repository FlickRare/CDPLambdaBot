from json import load as jload
from toml import load as tload
from cdp_bot import Bot


def configure_client(trading_pair):
    with open("cdp_api_key.json", "r", encoding="UTF-8") as handle:
        cdp_api_keys = jload(handle)
    currency_config = bot_config.get(trading_pair)
    product_id = currency_config["product_id"]
    stack_params = currency_config.get("stack_bot")
    stack_active, stack_threshold, stack_quote = stack_params["active"], stack_params["threshold"], stack_params["quote"]
    bot = Bot(cdp_api_keys, product_id, stack_active, stack_threshold, stack_quote)
    client = bot.initialize()
    return stack_active, stack_quote, bot, client


def stack_bot(client):
    drop_bool, price, ppc = bot.check_price_drop(client)
    print(price, ppc)
    if drop_bool is True:
            bot.stack_buy_order(client)


with open("bot_settings.toml", "r", encoding = "UTF-8") as handle:
    bot_config = tload(handle)
for trading_pair in bot_config:
    stack_active, stack_quote, bot, client = configure_client(trading_pair)
    available_USDC = bot.available_USDC(client)
    print(available_USDC)
    if stack_active and available_USDC > stack_quote:
        print(stack_bot(client))
