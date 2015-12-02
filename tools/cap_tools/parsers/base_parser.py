from bs4 import BeautifulSoup


class BaseParser(object):

    def __init__(self, content):
        self.content = content
        self.soup = BeautifulSoup(content, "html.parser")

        self._get_name()
        self._get_author()
        self._get_time_yield()
        self._get_description()
        self._get_ingredients()
        self._get_instructions()
        self._get_topics()
        self._get_notes()
        self._get_nutrition()
        self._get_image_url()

    def _get_name(self):
        pass

    def _get_author(self):
        pass

    def _get_time_yield(self):
        pass

    def _get_description(self):
        pass

    def _get_ingredients(self):
        pass

    def _get_instructions(self):
        pass

    def _get_topics(self):
        pass

    def _get_notes(self):
        pass

    def _get_nutrition(self):
        pass

    def _get_image_url(self):
        pass
