from .AccountService import AccountService
from .ProblemsetServiceImpl import ProblemsetServiceImpl
from .WebdriverService import WebdriverService
from .WebscraperService import WebscraperService

webscraper_service = WebscraperService()
webdriver_service = WebdriverService()
account_service = AccountService()
problemset_service = ProblemsetServiceImpl(
    webscraper_service=webscraper_service,
    webdriver_service=webdriver_service
)
