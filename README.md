<p align="center"><img src="resources/zora.jpg" alt="zora logo" width=60% height=60%/></p>
<h1 align="center">Zora Software V2</h1>

---

## Инструкция по запуску:
```
pip install -r requirements.txt
python main.py
```

---
## Инструкция по настройке:
### Mint settings
- **NFT 1155 URL** - адрес NFT коллекции. Важно! На данный момент это должна быть 1155 NFT и только в сети Zora.
- **Mint NFT price (ETH)** - цена минта. По умолчанию комиссия Zora 0.000777 ETH. По-этому "бесплатный" минт будет стоить 0.000777
- **Gas price for mint (Gwei)** - цена газа в Zora за минт. Рекомендуется использовать значение по-умолчанию (0.005).
- **Gas for mint** - количество газа в транзакцию. В среднем газа для минта нужно ~101к. По умолчанию стоит 130к.
- **Testnet** - включает Testnet для функции mint.

### Bridge settings
- **Max price for gas in Ethereum (Gwei)** - скрипт будет ждать, пока газ опустится ниже указанного значения, прежде чем бриджить.
- **Min amount for bridge (ETH)** - минимальное количество ETH для бриджа. 
- **Max amount for bridge (ETH)** - максимальное количество ETH для бриджа.
Важно! Рандомное число будет с максимальным знаком после запятой, из этих двух чисел! Т.е. 0.01 и 0.012 - число будет с 3-мя знаками после разделителя (напр. 0.011).
- **Testnet** - включает Testnet для функции bridge.

---
## Благодарности:
Большое спасибо выражаю цветным братишкам за помощь в консультировании и тестировании:
- вишнёвый (он же Вишня) ([https://t.me/vishnya_crypto](https://t.me/vishnya_crypto))
- зелёный (он же Пепыч) ([https://t.me/cypherfrog](https://t.me/cypherfrog))
