SELECT date_trading, turnover
FROM bond_quotes
WHERE issuer = 'Альфа-Банк'
AND isin = '{isin}'
AND date_trading BETWEEN '{date_1}' AND '{date_2}'
