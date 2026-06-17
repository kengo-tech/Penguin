# Crypto Derivatives Structuring Lab

Binanceの公開マーケットデータを使い、暗号資産デリバティブ/仕組商品のリスクを数学的・統計的に理解するための学習プロジェクトです。

目的は「高利回りに見える商品をどう売るか」ではなく、販売時に顧客へ説明すべき期待値、損失分布、転換確率、テールリスク、ヘッジの限界をコードで見えるようにすることです。

## このプロジェクトで扱う問い

- Dual Currency Investmentは、実質的にどのオプションを売っているのか
- 顧客に提示するAPRは、下落/上昇リスクに対して妥当か
- 満期時に不利な通貨へ転換される確率はどれくらいか
- 期待リターン、VaR、CVaR、損失確率はどう変わるか
- Binance Futuresの価格、funding、basis情報をどう商品設計に使うか

## 実装済みの最小機能

- Binance USD-M Futuresの公開REST APIクライアント
- BTCUSDTなどのkline取得
- funding rate history取得
- Dual Currency Investmentのpayoffシミュレーション
- GBM Monte Carloによる満期価格分布
- 期待値、損失確率、VaR、CVaR、転換確率の算出
- Black-Scholesによる参照用オプション理論価格
- APIなしで動くoffline demo

## セットアップ

このリポジトリは標準ライブラリだけで動きます。

```powershell
python -m unittest discover -s tests
```

API接続なしのデモ:

```powershell
python -m structuring_lab.cli dci --offline-demo --side put --spot 100000 --strike 90000 --notional 100000 --apr 0.12 --tenor-days 30
```

Binanceの公開データを使う例:

```powershell
python -m structuring_lab.cli dci --symbol BTCUSDT --lookback 365 --side put --strike-moneyness 0.9 --notional 100000 --apr 0.12 --tenor-days 30
```

## 商品理解

### Stablecoin建てDCI

顧客がUSDT/USDCを預け、満期時にBTCがストライク以上ならstablecoinで元本と利回りを受け取ります。BTCがストライク未満なら、元本と利回りがストライク価格でBTCに転換されます。

これは、金融工学的にはcash-secured put sellingに近い構造です。

### BTC建てDCI

顧客がBTCを預け、満期時にBTCがストライク以下ならBTCのまま利回りを受け取ります。BTCがストライク超なら、BTCがストライク価格でstablecoinへ転換されます。

これは、金融工学的にはcovered call sellingに近い構造です。

## 販売時に見るべき指標

- Expected return: 平均的に顧客が得る/失うもの
- Probability of loss: 元本割れ確率
- Conversion probability: 満期時に不利な受渡になる確率
- VaR: 指定信頼水準での損失
- CVaR: VaRを超える悪いケースの平均損失
- Benchmark gap: 単純保有やstablecoin保有との比較

## 参照した公式API

- Binance USD-M Futures kline: `GET /fapi/v1/klines`
- Binance USD-M Futures exchange info: `GET /fapi/v1/exchangeInfo`
- Binance USD-M Futures funding rate history: `GET /fapi/v1/fundingRate`

## 注意

これは教育・面接準備・商品理解用のコードです。投資助言、勧誘、実運用、顧客向け資料としてそのまま使用するものではありません。

