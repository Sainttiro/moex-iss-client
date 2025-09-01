ATTACH TABLE _ UUID '5b19ad74-4c67-4880-b8ab-0ea898aacc09'
(
    `BOARDID` String,
    `TRADEDATE` Date,
    `SHORTNAME` String,
    `SECID` String,
    `NUMTRADES` Float64,
    `VALUE` Float64,
    `OPEN` Float64,
    `LOW` Float64,
    `HIGH` Float64,
    `LEGALCLOSEPRICE` Float64,
    `WAPRICE` Float64,
    `CLOSE` Float64,
    `VOLUME` Float64,
    `MARKETPRICE2` Float64,
    `MARKETPRICE3` Float64,
    `ADMITTEDQUOTE` Float64,
    `MP2VALTRD` Float64,
    `MARKETPRICE3TRADESVALUE` Float64,
    `ADMITTEDVALUE` Float64,
    `WAVAL` Float64
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(TRADEDATE)
ORDER BY (TRADEDATE, SECID)
SETTINGS index_granularity = 8192
