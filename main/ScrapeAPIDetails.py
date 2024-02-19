from bs4 import BeautifulSoup as bs
import pandas as pd
import requests


def get_soup(url_param):
    response = requests.get(url_param)
    if response.status_code == 200:
        data = response.text
        soup = bs(data, "html.parser")
        return soup
    else:
        return None


def get_api_details():
    has_next = True
    total_apis = 0
    url = "https://apislist.com/apis"
    data = {}

    while has_next:
        current_page_soup = get_soup(url)
        apis = current_page_soup.find_all("div", {"class": "category-content w-100"})
        for api in apis:
            # Get details on the current page
            title = api.find("div").find("h4").find('a').text
            overview = api.find('p').text
            link = api.find("div").find("h4").find('a').get("href")
            # Get details on the API's detail page
            api_detail_soup = get_soup("https://apislist.com" + link)
            if api_detail_soup is not None:
                api_detail = api_detail_soup.find("div", {"class": "api-card card"})
                description = api_detail.find("div", {"class": "text-muted bd-callout bd-callout-info"}).find('p').text
                https_support = api_detail.find("td", string="HTTPS Support").find_next_sibling("td").text.strip()
                cors_support = api_detail.find("td", string="CORS Support").find_next_sibling("td").text.strip()
                authentication_type = api_detail.find("td", string="Authentication Type").find_next_sibling(
                    "td").text.strip()
                pricing = api_detail.find("td", string="Pricing").find_next_sibling("td").text.strip()
            else:
                description = https_support = cors_support = authentication_type = pricing = "NA"
            # Store the details in dict to be put in csv later
            total_apis += 1
            data[total_apis] = [title, overview, link, description, https_support, cors_support, authentication_type,
                                pricing]
            print("Title:", title, "\nOverview:", overview, "\nLink:", link, "\nDescription:", description,
                  "\nHTTPS Support:", https_support, "\nCORS Support:", cors_support,
                  "\nAuthentication Type:", authentication_type, "\nPricing:", pricing, "\nAPI Count:", total_apis,
                  "\n-----")
        current_page_button = current_page_soup.find("li", {"class": "page-item active"})
        next_page_button = current_page_button.find_next_sibling("li", {"class": "page-item"}).find('a')
        if next_page_button is not None:
            url = next_page_button.get("href")
        else:
            has_next = False
    print("Total number of APIs:", total_apis)
    # Save the data to a csv file
    dataframe = pd.DataFrame.from_dict(data, orient="index", columns=["API Name", "Overview", "Link", "Description",
                                                                      "HTTPS Support", "CORS Support",
                                                                      "Authentication Type", "Pricing"])
    dataframe.to_csv("APIList.csv")


get_api_details()
