import json
import random
import time
import logging
import requests
from datetime import datetime, timedelta
from web3 import Web3
from colorama import init, Fore
from eth_account import Account
from urllib.parse import urlencode
from utils.keys import private_keys
from settings import RPC, MIN_START, MAX_START, MIN_TRADE, MAX_TRADE, MIN_CONTROL_POSITION, MAX_CONTROL_POSITION, MIN_DELAY_TRADE, MAX_DELAY_TRADE
import threading

# Инициализация colorama
init(autoreset=True)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Чтение ABI контрактов из файла utils/abi.json
with open('utils/abi.json', 'r') as f:
    abi_data = json.load(f)

avantis_contract_abi = abi_data['avantis']
avantis_contract_address = "0x5FF292d70bA9cD9e7CCb313782811b3D7120535f"  # Адрес контракта
# STORAGE
storage_contract_abi = abi_data['avantis_storage']
storage_contract_address = "0x8a311D7048c35985aa31C131B9A13e03a5f7422d"  # Адрес контракта
# USDC
pay_contract_abi = abi_data['arbitrum']  # ABI для ERC20 токенов
usdc_contract_address = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"  # Адрес контракта

# Генерация кошельков из приватных ключей
wallets = [Account.from_key(private_key).address for private_key in private_keys]

def wait_random_time(wallet_address):
    delay = random.randint(MIN_CONTROL_POSITION, MAX_CONTROL_POSITION)
    print(f"{datetime.now().date()} {datetime.now().time()} | [{i}/{len(wallets)}] | {wallet_address} | Module: Avantis | Time to close position {delay} seconds")
    time.sleep(delay)

def wait_trade_time(wallet_address):
    delay = random.randint(MIN_DELAY_TRADE, MAX_DELAY_TRADE)
    print(
        f"{datetime.now().date()} {datetime.now().time()} | [{i}/{len(wallets)}] | {wallet_address} | Module: Avantis | Time to next trade {delay} seconds")
    time.sleep(delay)

pair_price = [
    "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace",  # ETH/USDC
    "0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",  # BTC/USDC
    "0xef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d",  # SOL/USDC
    "0x2f95862b045670cd22bee3114c39763a4a08beeb663b145d283c31d7d1101c4f",  # BNB/USDC
    "0x3fa4252848f9f0a1480be62745a4629d9eb1322aebab8a791e344b3b9c1adcf5",  # ARB/USDC
    "0xdcef50dd0a4cd2dcc17e45df1676dcb336a11a61c69df7a0299b0150c672d25c",  # DOGE/USDC
    "0x93da3352f9f1d105fdfe4971cfa80e9dd777bfc5d0f683ebb6e1294b92137bb7",  # AVAX/USDC
    "0x385f64d993f7b77d8182ed5003d97c60aa3361f3cecfe711544d2d59165e9bdf",  # OP/USDC
    "0x09f7c1d7dfbb7df2b8fe3d3d87ee94a2259d212da4f30c1f0540d066dfa44723",  # TIA/USDC
    "0x53614f1cb0c031d4af66c04cb9c756234adad0e1cee85303795091499a4084eb",  # SEI/USDC
]

index_trade = {
    "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace": "0",  # ETH/USDC
    "0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43": "1",  # BTC/USDC
    "0xef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d": "2",  # SOL/USDC
    "0x2f95862b045670cd22bee3114c39763a4a08beeb663b145d283c31d7d1101c4f": "3",  # BNB/USDC
    "0x3fa4252848f9f0a1480be62745a4629d9eb1322aebab8a791e344b3b9c1adcf5": "4",  # ARB/USDC
    "0xdcef50dd0a4cd2dcc17e45df1676dcb336a11a61c69df7a0299b0150c672d25c": "5",  # DOGE/USDC
    "0x93da3352f9f1d105fdfe4971cfa80e9dd777bfc5d0f683ebb6e1294b92137bb7": "6",  # AVAX/USDC
    "0x385f64d993f7b77d8182ed5003d97c60aa3361f3cecfe711544d2d59165e9bdf": "7",  # OP/USDC
    "0x5de33a9112c2b700b8d30b8a3402c103578ccfa2765696471cc672bd5cf6ac52": "8",  # MATIC/USDC
    "0x09f7c1d7dfbb7df2b8fe3d3d87ee94a2259d212da4f30c1f0540d066dfa44723": "9",  # TIA/USDC
    "0x53614f1cb0c031d4af66c04cb9c756234adad0e1cee85303795091499a4084eb": "10",  # SEI/USDC
}

pairn_name = {
    "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace": "ETH/USDC",  # ETH/USDC
    "0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43": "BTC/USDC",  # BTC/USDC
    "0xef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d": "SOL/USDC",  # SOL/USDC
    "0x2f95862b045670cd22bee3114c39763a4a08beeb663b145d283c31d7d1101c4f": "BNB/USDC",  # BNB/USDC
    "0x3fa4252848f9f0a1480be62745a4629d9eb1322aebab8a791e344b3b9c1adcf5": "ARB/USDC",  # ARB/USDC
    "0xdcef50dd0a4cd2dcc17e45df1676dcb336a11a61c69df7a0299b0150c672d25c": "DOGE/USDC", # DOGE/USDC
    "0x93da3352f9f1d105fdfe4971cfa80e9dd777bfc5d0f683ebb6e1294b92137bb7": "AVAX/USDC", # AVAX/USDC
    "0x385f64d993f7b77d8182ed5003d97c60aa3361f3cecfe711544d2d59165e9bdf": "OP/USDC",   # OP/USDC
    "0x5de33a9112c2b700b8d30b8a3402c103578ccfa2765696471cc672bd5cf6ac52": "MATIC/USDC",# MATIC/USDC
    "0x09f7c1d7dfbb7df2b8fe3d3d87ee94a2259d212da4f30c1f0540d066dfa44723": "TIA/USDC",  # TIA/USDC
    "0x53614f1cb0c031d4af66c04cb9c756234adad0e1cee85303795091499a4084eb": "SEI/USDC",  # SEI/USDC
}

def get_eth_usdc_price(pair_avantis):
    base_url = "https://hermes.pyth.network/api/latest_price_feeds"
    params = {"ids[]": [pair_avantis]}  # Обернуть pair_avantis в массив
    url = f"{base_url}?{urlencode(params, doseq=True)}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    price_info = data[0]["price"]
    price = price_info["price"]
    return price

def random_margin(wallet_address, web3, i):
    usdc_contract = web3.eth.contract(address=web3.to_checksum_address(usdc_contract_address), abi=pay_contract_abi)

    # Получить текущий баланс USDC
    balance = usdc_contract.functions.balanceOf(wallet_address).call()

    # Проверить, что баланс достаточен
    if balance < 10000000:
        print(f"Insufficient USDC balance in wallet {wallet_address}. Skipping.")
        return None

    # Генерация случайного значения от 10,000,000 до текущего баланса
    min_margin = 10000000
    max_margin = balance
    margin_open = random.randint(min_margin, max_margin)
    current_time = datetime.now()
    print(
        f"{current_time.date()} {current_time.time()} | [{i}/{len(wallets)}] | {wallet_address} | Module: Avantis | Generated random margin: {margin_open / 10**6} USDC")
    return margin_open

def expert_trade(index_avantis):
    url = "https://socket-api.avantisfi.com/v1/data"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    pair_info = data["data"]["pairInfos"].get(str(index_avantis))

    if pair_info:
        long_value = pair_info["openInterest"]["long"]
        short_value = pair_info["openInterest"]["short"]

        if long_value > short_value:
            return False  # long > short
        else:
            return True  # short > long
    else:
        raise ValueError(f"No pair information found for index {index_avantis}")

def avantis_open_trade(wallet_address, private_key, web3, i, margin_open, price, index_avantis, pair_trade_name, smart_buy):
    # Инициализация контракта
    avantis_contract = web3.eth.contract(address=web3.to_checksum_address(avantis_contract_address),
                                         abi=avantis_contract_abi)

    trader = wallet_address
    pairIndex = int(index_avantis)
    index = 0
    initialPosToken = 0
    positionSizeUSDC = margin_open
    openPrice = int(price) * 10**2
    buy = smart_buy
    position = "Long" if buy else "Short"
    leverage_factor = random.randint(20, 50)
    leverage = leverage_factor * 10 ** 10
    tp = 0
    sl = 0
    timestamp = 0
    open_trade_call = [trader, pairIndex, index, initialPosToken, positionSizeUSDC, openPrice, buy, leverage, tp, sl, timestamp]

    usdc_type = 0
    slippageP = 10000000000
    executionFee = 0

    nonce = web3.eth.get_transaction_count(wallet_address)
    balance = web3.eth.get_balance(wallet_address)
    if balance <= 0:
        logging.error(f"Insufficient balance in wallet {wallet_address}")
        return None

    current_gas_price = web3.eth.gas_price
    gas_price = int(current_gas_price * 1.1)

    # Оценка gasLimit
    gas_limit = web3.eth.estimate_gas({
        'from': wallet_address,
        'to': avantis_contract_address,
        'value': random.randint(3460000000000, 3490000000000),
        'data': avantis_contract.encodeABI(fn_name='openTrade', args=[open_trade_call, usdc_type, slippageP, executionFee]),
    })

    # Получение текущей даты и времени
    current_time = datetime.now()

    print(
        f'{current_time.date()} {current_time.time()} | [{i}/{len(wallets)}] | {wallet_address} | Module: Avantis | Open {leverage_factor}X {position} {pair_trade_name}')

    try:
        tx_params = {
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': gas_limit,
            'to': avantis_contract_address,
            'value': random.randint(3460000000000, 3490000000000),
            'data': avantis_contract.encodeABI(fn_name='openTrade', args=[open_trade_call, usdc_type, slippageP, executionFee]),
            'chainId': 8453,  # ID сети ETH
        }

        signed_tx = web3.eth.account.sign_transaction(tx_params, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        # Ожидание подтверждения транзакции
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        if tx_receipt.status == 1:
            print(Fore.GREEN + f'{current_time.date()} {current_time.time()} | [{i}/{len(wallets)}] | {wallet_address} | https://basescan.org/tx/{tx_hash.hex()}')
        else:
            print(Fore.RED + f'{current_time.date()} {current_time.time()} | [{i}/{len(wallets)}] | {wallet_address} | https://basescan.org/tx/{tx_hash.hex()}')

        return tx_hash.hex()

    except Exception as e:
        logging.error(f'Error occurred for wallet {wallet_address}: {e}')
        logging.exception("Exception occurred", exc_info=True)
        return None

def avantis_close_trade(wallet_address, private_key, web3, i, index_avantis, pair_trade_name, smart_buy):
    # Инициализация контракта
    avantis_contract = web3.eth.contract(address=web3.to_checksum_address(avantis_contract_address), abi=avantis_contract_abi)
    storage_contract = web3.eth.contract(address=web3.to_checksum_address(storage_contract_address), abi=storage_contract_abi)

    trader = wallet_address
    pairIndex = int(index_avantis)
    index = 0
    margin_data = storage_contract.functions.openTrades(trader, pairIndex, index).call()

    close_margin = margin_data[3]

    executionFee = 0

    buy = smart_buy
    position = "Long" if buy else "Short"

    nonce = web3.eth.get_transaction_count(wallet_address)
    balance = web3.eth.get_balance(wallet_address)
    if balance <= 0:
        logging.error(f"Insufficient balance in wallet {wallet_address}")
        return None

    current_gas_price = web3.eth.gas_price
    gas_price = int(current_gas_price * 1.1)

    # Оценка gasLimit
    gas_limit = web3.eth.estimate_gas({
        'from': wallet_address,
        'to': avantis_contract_address,
        'value': random.randint(3460000000000, 3490000000000),
        'data': avantis_contract.encodeABI(fn_name='closeTradeMarket', args=[pairIndex, index, close_margin, executionFee]),
    })

    # Получение текущей даты и времени
    current_time = datetime.now()

    print(
        f'{current_time.date()} {current_time.time()} | [{i}/{len(wallets)}] | {wallet_address} | Module: Avantis | Close {position} {pair_trade_name}')

    try:
        tx_params = {
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': gas_limit,
            'to': avantis_contract_address,
            'value': random.randint(3460000000000, 3490000000000),
            'data': avantis_contract.encodeABI(fn_name='closeTradeMarket', args=[pairIndex, index, close_margin, executionFee]),
            'chainId': 8453,  # ID сети ETH
        }

        signed_tx = web3.eth.account.sign_transaction(tx_params, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        # Ожидание подтверждения транзакции
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        if tx_receipt.status == 1:
            print(Fore.GREEN + f'{current_time.date()} {current_time.time()} | [{i}/{len(wallets)}] | {wallet_address} | https://basescan.org/tx/{tx_hash.hex()}')
        else:
            print(Fore.RED + f'{current_time.date()} {current_time.time()} | [{i}/{len(wallets)}] | {wallet_address} | https://basescan.org/tx/{tx_hash.hex()}')

        return tx_hash.hex()

    except Exception as e:
        logging.error(f'Error occurred for wallet {wallet_address}: {e}')
        logging.exception("Exception occurred", exc_info=True)
        return None

# Главная функция
def avantis(wallet_address, private_key, web3, i, iterations):
    for iteration in range(1, iterations + 1):
        try:
            print(f"{datetime.now().date()} {datetime.now().time()} | [{i}/{len(wallets)}] | {wallet_address} | Trade {iteration}/{iterations}")
            pair_avantis = random.choice(pair_price)
            index_avantis = index_trade.get(pair_avantis)
            pair_trade_name = pairn_name.get(pair_avantis)
            price = get_eth_usdc_price(pair_avantis)

            if price:
                margin_open = random_margin(wallet_address, web3, i)
                if margin_open is None:
                    break  # Прекращаем работу с кошельком, если баланс недостаточен

                smart_buy = expert_trade(index_avantis)  # Вызов expert_trade

                tx_hash = avantis_open_trade(wallet_address, private_key, web3, i, margin_open, price, index_avantis,
                                   pair_trade_name, smart_buy)

                if tx_hash is None:
                    logging.error(f'Failed to open trade for wallet {wallet_address}')
                    continue  # Пропустить итерацию, если не удалось открыть сделку

                wait_random_time(wallet_address)  # Логирование задержки будет выполнено внутри этой функции
                avantis_close_trade(wallet_address, private_key, web3, i, index_avantis, pair_trade_name)

                # Задержка между итерациями
                wait_trade_time(wallet_address)  # Логирование задержки будет выполнено внутри этой функции

            else:
                logging.error(f'Failed to get transaction data for wallet {wallet_address}')
        except Exception as e:
            logging.error(f'Error occurred for wallet {wallet_address}: {e}')
            logging.exception("Exception occurred", exc_info=True)
            print(f"Error occurred for wallet {wallet_address}: {e}. Skipping to the next action.")
            raise e

    # Добавить вывод сообщения по завершении всех итераций
    print(f"{datetime.now().date()} {datetime.now().time()} | [{i}/{len(wallets)}] | {wallet_address} | Work completed")


def start_wallet_with_delay(wallet, private_key, web3, i, start_time):
    while datetime.now() < start_time:
        time.sleep(1)
    iterations = random.randint(MIN_TRADE, MAX_TRADE)  # Количество итераций для каждого кошелька
    avantis(wallet, private_key, web3, i, iterations)

if __name__ == "__main__":
    # RPC
    web3 = Web3(Web3.HTTPProvider(RPC))

    # Подготовка лог-сообщений перед созданием потоков
    logs = []
    start_times = []
    for i, (wallet, private_key) in enumerate(zip(wallets, private_keys), start=1):
        start_delay = random.randint(MIN_START, MAX_START)
        start_time = datetime.now() + timedelta(seconds=start_delay)
        start_times.append(start_time)
        log_message = f"{datetime.now().date()} {datetime.now().time()} | [{i}/{len(wallets)}] | {wallet} | Start work with wallet at {start_time}"
        logs.append(log_message)

    # Вывод всех лог-сообщений
    for log in logs:
        print(log)

    # Создание и запуск потоков после вывода логов
    threads = []
    for i, ((wallet, private_key), start_time) in enumerate(zip(zip(wallets, private_keys), start_times), start=1):
        t = threading.Thread(target=start_wallet_with_delay, args=(wallet, private_key, web3, i, start_time))
        threads.append(t)
        t.start()
