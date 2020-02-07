import os
import csv
from helpers import utc_now


class DataCollector:
    @staticmethod
    def store(phrase, city, ads):
        if not os.path.exists('data'):
            os.mkdir('data')

        file_path = ('data/%s_%s' % (utc_now(), phrase)).replace(':', '_').replace('.', '_').replace(' ', '_')
        with open(file_path + '.csv', 'w', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for ad in ads:
                csv_writer.writerow(list(ad.values()))

