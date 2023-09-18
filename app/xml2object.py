from .util import pt_in_2_value


class PositionExtractor:
    def __init__(self, root):
        self.root = root
        self.namespaces = {
            'v': 'urn:schemas-microsoft-com:vml',
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        }

    def extract_positions_from_xml(self):
        results = []
        write_flag = False
        page = 0

        for rect in self.root.findall(".//v:rect", self.namespaces):
            style = rect.get('style')
            position_data = {}
            for pair in style.split(';'):
                name, _, value = pair.partition(':')
                position_data[name] = value

            text_content = rect.find(".//w:t", self.namespaces)
            if text_content is not None:
                text = text_content.text
                if 'Страница' in text:
                    write_flag = False
                if write_flag:
                    ml = pt_in_2_value(position_data['margin-left'])
                    mt = pt_in_2_value(position_data['margin-top'])
                    w = pt_in_2_value(position_data['width'])
                    h = pt_in_2_value(position_data['height'])
                    if ml >= 0 and mt >= 0 and w >= 0 and h >= 0:
                        position = {'margin-left': ml, 'margin-top': mt, 'width': w, 'height': h}
                        results.append({'text': text, 'position': position, 'page': page})
                if text == ' 2':
                    write_flag = True
                    page += 1

        return results