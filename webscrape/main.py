from bs4 import BeautifulSoup
import requests
import pandas as pd


def save_file(self, soup: BeautifulSoup):
    with open("test.html", "w", encoding="utf-8") as file:
        file.write(str(soup))


class FarfetchScrape:

    root_path = "https://www.farfetch.com/uk/Boutiques/all?cid=0&region=0&items=80&page="

    element_types = {
        "heading-regular force-ltr boutique_name": "h2",
        "heading-regular boutique_location": "p",
        "boutique_designers": "p"
    }

    def __init__(self):
        self.soup = None
        self.names = []
        self.location = []
        self.designers = []
        self.df_out = pd.DataFrame()

    def get_html(self, page_number:str):
        url = self.root_path + page_number
        req = requests.get(url)
        self.soup = BeautifulSoup(req.content, 'html.parser')

    def extract_values(self, tag: str, class_value: str):
        records = self.soup.find_all(tag, class_=class_value)
        container = []
        for record in records:
            container.append(record.get_text())
        return container

    def return_df(self):

        d = {class_value: self.extract_values(tag, class_value) for (class_value, tag) in self.element_types.items()}

        df = {'Boutique_Name': d['heading-regular force-ltr boutique_name'],
              'Boutique_Location': d['heading-regular boutique_location'],
              'Designers': d["boutique_designers"]}
        df = pd.DataFrame(df)
        self.df_out = pd.concat([self.df_out, df], axis=0)


if __name__ == "__main__":
    session = FarfetchScrape()
    for i in range(8):
        session.get_html(page_number=str(i+1))
        session.return_df()
        print(f"Completed page {i+1}")
    session.df_out[['City', 'Country']] = session.df_out['Boutique_Location'].str.split(',', 1, expand=True)
    session.df_out['Designers'] = session.df_out['Designers'].str.split(", ")
    session.df_out = session.df_out.explode('Designers').drop(columns=['Boutique_Location'])
    session.df_out.to_csv("farfetch-brands-stores-location.csv", index = False)
