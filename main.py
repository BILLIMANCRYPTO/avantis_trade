
    print(
        f'{current_time.date()} {current_time.time()} | [{i}/{len(wallets)}] | {wallet_address} | Module: Avantis | Open {leverage_factor}X {position} {pair_trade_name}')

    try:
        tx_params = {
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': gas_limit,
            'to': avantis_contract_address,
            'value': random.randint(3460000000000, 7490000000000),
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
        'value': random.randint(3460000000000, 7490000000000),
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
            'value': random.randint(3460000000000, 7490000000000),
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
