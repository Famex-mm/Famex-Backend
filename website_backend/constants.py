from website_backend.settings import DEBUG

NETWORK_CHOICES = [
    ('5', 'Goerli Test Network'),
    ('56', 'Binance Smart Chain'),
]

TRADING_API_NETWORK_NAMES = {'5': 'GTN', '56': 'BSC'}

NETWORK_PROVIDERS = {
    '4': 'https://rinkeby.infura.io/v3/1daddf6be92c434cb846e9c1394fd5c5',
    '5': 'https://goerli.infura.io/v3/1daddf6be92c434cb846e9c1394fd5c5',
    '56': 'https://bsc-dataseed.binance.org/'
}

ADDRESSES = {
    '56': {
        'MarketMakerDeployer': '0x1024cB8649930efdD158958BD5ab552B295eD33c',
    },
    '5': {
        'MarketMakerDeployer': '0xcd0Cb9a57028Ba5720D4d86Ee8afe66eb3999FB7',
    }
}

if DEBUG:
    DEFAULT_NETWORK = '5'
else:
    DEFAULT_NETWORK = '56'

DISALLOWED_COUNTRIES = ['KP', 'IR', 'SY']
