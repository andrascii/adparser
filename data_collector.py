import os
import csv
from helpers import utc_now


class DataCollector:
    @staticmethod
    def store_wordstat_data(additional_found_keywords, for_phrase):
        folder_path_to_store = ['data', 'wordstat']
        DataCollector.__ensure_path_exists(folder_path_to_store)

        file_path = DataCollector.__make_file_path(folder_path_to_store, for_phrase)

        with open(file_path + '.csv', 'w', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for additional_found_keyword in additional_found_keywords:
                csv_writer.writerow([additional_found_keyword])

    @staticmethod
    def store_ad_search_data(parser_name, for_phrase, ads):
        folder_path_to_store = ['data', parser_name]
        DataCollector.__ensure_path_exists(folder_path_to_store)

        file_path = DataCollector.__make_file_path(folder_path_to_store, for_phrase)

        with open(file_path + '.csv', 'w', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for ad in ads:
                row = [for_phrase, None, ad['phone'], ad['ad_header'] + ' ' + ad['ad_text'], None, utc_now(), ad['url']]
                csv_writer.writerow(row)

    @staticmethod
    def __make_file_path(folder_path_to_store, for_phrase):
        return ('%s/%s_%s' % ('/'.join(folder_path_to_store), utc_now(), for_phrase))\
            .replace(':', '_')\
            .replace('.', '_')\
            .replace(' ', '_')

    @staticmethod
    def __ensure_path_exists(folder_list_path: list):
        path = str()
        for folder in folder_list_path:
            path += folder + '/'
            if not os.path.exists(path):
                os.mkdir(path)
