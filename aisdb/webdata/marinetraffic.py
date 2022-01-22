''' scrape vessel information such as deadweight tonnage from marinetraffic.com '''

import json

import requests

from common import data_dir, marinetraffic_VD02_key
from index import index
from webdata.scraper import (
    init_webdriver,
    WebDriverWait,
)


class scrape_tonnage():

    def __init__(self):
        self.filename = 'marinetraffic.db'
        self.driver = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if self.driver is not None:
            self.driver.close()
            self.driver.quit()

    def tonnage_callback(self, mmsi, imo=0, **_):
        if self.driver is None:
            self.driver = init_webdriver()

        loaded = lambda drv: 'asset_type' in drv.current_url or '404' == drv.title[
            0:3] or drv.find_elements_by_id('vesselDetails_voyageInfoSection')

        if imo == 0:
            url = f'https://www.marinetraffic.com/en/ais/details/ships/mmsi:{mmsi}'
        else:
            url = f'https://www.marinetraffic.com/en/ais/details/ships/mmsi:{mmsi}/imo:{imo}'
        print(url, end='\t')
        self.driver.get(url)

        WebDriverWait(self.driver, 15).until(loaded)

        if 'asset_type' in self.driver.current_url:
            for elem in self.driver.find_elements_by_partial_link_text(""):
                if (url := elem.get_attribute('href')) == None: continue
                elif 'vessel:' in url:
                    print(
                        f'multiple entries found for {mmsi=} {imo=} ! fetching {url}'
                    )
                    self.driver.get(url)
                    WebDriverWait(self.driver, 15).until(loaded)
                    break

        elif self.driver.title[0:3] == '404':
            print(f'404 error! {mmsi=} {imo=}')
            return 0

        exists = self.driver.find_elements_by_id(
            'vesselDetails_vesselInfoSection')
        if exists:
            elem = exists[0].find_element_by_id('summerDwt')
            #elem.location_once_scrolled_into_view
            print(mmsi, elem.text)
            return elem.text.split(' ')[2]
        else:
            print(0)
            return 0

    def get_tonnage_mmsi_imo(self, mmsi, imo):
        #if not 201000000 <= mmsi < 776000000: return 0
        if not 1000000 <= imo < 9999999: imo = 0

        with index(bins=False,
                   store=True,
                   storagedir=data_dir,
                   filename=self.filename) as web:
            tonnage = web(callback=self.tonnage_callback,
                          mmsi=mmsi,
                          imo=imo,
                          seed='dwt marinetraffic.com')[0]

        if tonnage == '-': return 0

        return int(tonnage)

    def exit(self):
        self.driver.close()


def api_shipsearch_bymmsi(mmsis):
    ''' Access the marinetraffic API to search master vessel data for vessel
        particulars

        To use this, register a VD02 API token at marinetraffic.com, and store
        the token in your config file, e.g.
        ```
        marinetraffic_VD02_key = e82589918dc450bc712f6f2eec3840c8b4f25206
        ```

        more info:
        https://servicedocs.marinetraffic.com/tag/Vessel-Information#operation/vesselmasterdata

        args:
            mmsis (list of integers)
                search for vessels by MMSI

        returns:
            dict
    '''
    api = 'https://services.marinetraffic.com/api'
    url = f'{api}/vesselmasterdata/{marinetraffic_VD02_key}/mmsi:{",".join(mmsis)}/protocol:json'
    req = requests.get(url)
    res = json.loads(req.content.decode())

    if 'errors' in res.keys():
        for error in res['errors']:
            raise RuntimeError(
                f'Problem calling Marinetraffic API:  {error["detail"]}')

    return res
