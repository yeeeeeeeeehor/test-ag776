from web3 import Account
import os

num_wallets = int(input("Введите количество кошельков для создания: "))

wallets = []
private_keys = []

for _ in range(num_wallets):
    account = Account.create()

    wallet_address = account.address
    private_key = account._private_key.hex()

    wallets.append(wallet_address)
    private_keys.append(private_key)

with open('wallet.txt', 'w') as wallet_file:
    for wallet_address in wallets:
        wallet_file.write(wallet_address + '\n')

with open('privatekey.txt', 'w') as private_key_file:
    for private_key in private_keys:
        private_key_file.write(private_key + '\n')

print(f"Создано {num_wallets} кошельков.")
print("Адреса кошельков сохранены в файле wallet.txt.")
print("Приватные ключи сохранены в файле privatekey.txt.")
